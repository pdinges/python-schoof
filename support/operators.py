# -*- coding: utf-8 -*-
# Copyright (c) 2010--2012  Peter Dinges <pdinges@acm.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
A class decorator for operand casting in binary operations.  Use it to support
mixed mode operations in arithmetic objects, for example, to be able to add
regular integers to finite field elements.

@package   support.operators
@author    Peter Dinges <pdinges@acm.org>
"""

def operand_casting(cls):
    """
    Class decorator that adds operand casting to binary operations.
    
    The decorator offers an easy way to support mixed mode operations in
    arithmetic objects.  For example, it allows polynomials to interpret
    integer constants as constant polynomials without adding overhead to the
    operator methods like __add__() etc.
    
    @note  The decorator assumes that operation definitions remain constant
           during runtime, that is, will not be re-assigned after
           template specialization.
    
    @see   The sources of rings.polynomials.naive.Polynomials
           for a usage example.
    """
    #   @f( arg )
    #   class A: pass
    # resolves to
    #   class A: pass
    #   A = f( arg )( A )
    # See section "Function definitions" in the Python language reference.
    if getattr( cls.__class__, "__operand_casting__", False ):
        return cls

    # Simply wrap the meta-class's type creation method. On type creation,
    # wrap the new type object's methods.
    original_new = cls.__class__.__new__
    
    def operation_casting_new(meta_class, class_name, bases, class_dict, **kw_arguments):
        class_object = original_new( meta_class, class_name, bases, class_dict, **kw_arguments )
        
        # Modify only fully specialized templates. 
        if getattr( class_object.__class__, "__unbound_parameters__", False ):
            return class_object
        
        for operation_name in [ "__{0}__".format( op ) for op in __binary_operation_names ]:
            # Only wrap operations in the actual class object, not in its bases.
            # (getattr() would retrieve attributes from base classes.)
            if operation_name in class_object.__dict__:
                operation = class_object.__dict__[ operation_name ]
                setattr( class_object, operation_name, __casting_wrapped( operation ) )
                
        return class_object

    cls.__class__.__new__ = operation_casting_new
    setattr( cls.__class__, "__operand_casting__", True )
    return cls


# Wrap these operations
__binary_operation_names = [
       "eq", "neq",
       "add", "radd", "sub", "rsub",
       "mul", "rmul", "truediv", "rtruediv",
       "divmod", "rdivmod", "floordiv", "rfloordiv", "mod", "rmod"
       
   ]


from .profiling import rename_function

def __casting_wrapped( operation ):
    """
    Return the wrapped @p operation (without nesting the wrappers).
    
    This function is not intended for direct use; rather, employ
    @c operand_casting()
    """
    if hasattr( operation, "__wrapped_method__" ):
        return operation
    
    # A function outside operation_casting_new()'s scope is required
    # to avoid variable binding problems.
    # (If defined inside the scope, 'operation' points at the
    #  last used value for _all_ wrappers.)
    def casting_wrapper( self, other ):
        if self.__class__ is other.__class__:
            return operation( self, other )
        
        try:
            return operation( self, self.__class__( other ) )
        except TypeError:
            return NotImplemented
    
    # Rename the code object to reflect the wrapped operation's name.
    # Otherwise, the profile lists all wrapped operations
    # as 'wrapped_operation'.
    rename_function(
              casting_wrapper,
              "{op}_casting_wrapper".format( op = operation.__name__ )
          )
    setattr( casting_wrapper, "__wrapped_method__", operation )
    return casting_wrapper
