# -*- coding: utf-8 -*-
# $Id$

#   @f( arg )
#   class A: pass
# resolves to
#   class A: pass
#   A = f( arg )( A )
# See section "Function definitions" in the Python language reference.
def cast_operands(cls):
    """
    Class decorator that adds operand casting to binary operations.
    
    Note: The decorator assumes that operation definitions are constant
          during runtime, that is, will not be re-assigned.
    """
    if getattr( cls.__class__, "__operand_casting__", False ):
        return cls

    # Simply wrap the meta-class's type creation method. On type creation,
    # wrap the new type object's methods.
    original_new = cls.__class__.__new__
    
    def operation_casting_new(meta_class, class_name, bases, class_dict, **kw_arguments):
        class_object = original_new( meta_class, class_name, bases, class_dict, **kw_arguments )
        
        if getattr( class_object.__class__, "__unbound_parameters__", False ):
            return class_object
        
        if "__operand_casting__" in class_object.__dict__:
            return class_object

        for operation_name in [ "__{0}__".format( op ) for op in binary_operation_names ]:
            # Only wrap operations in the actual class object, no in its bases.
            # (getattr() would retrieve attributes from base classes.)
            if operation_name in class_object.__dict__:
                operation = class_object.__dict__[ operation_name ]
                setattr( class_object, operation_name, wrap_operation( operation ) )
                
        setattr( class_object, "__operand_casting__", True )
        return class_object

    cls.__class__.__new__ = operation_casting_new
    setattr( cls.__class__, "__operand_casting__", True )
    return cls


binary_operation_names = [
       "eq", "neq",
       "add", "radd", "sub", "rsub",
       "mul", "rmul", "truediv", "rtruediv",
       "divmod", "rdivmod", "floordiv", "rfloordiv", "mod", "rmod"
       
   ]


from .profiling import renamed_function

def wrap_operation( operation ):
    # A function outside operation_casting_new()'s scope is required
    # to avoid variable binding problems.
    # (If defined inside the scope, 'operation' points at the
    #  last used value for _all_ wrappers.)
    def wrapped_operation( self, other ):
        if self.__class__ is other.__class__:
            return operation( self, other )
        
        try:
            return operation( self, self.__class__( other ) )
        except TypeError:
            return NotImplemented
    
    # Rename code object to reflect the wrapped operation's name. Otherwise
    # the profile lists all wrapped operations as 'wrapped_operation'.
    new_name = "{op}_casting_wrapper".format( op = operation.__name__ )    
    return renamed_function(
                      wrapped_operation,
                      new_name
                  )
