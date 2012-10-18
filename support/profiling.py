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
Class decorators for more expressive call profiles.

The Python profiler in the @c cProfile module registers methods as elements
of the class that contains their source code.  Thus, @c cProfile merges calling
statistics of the defining class and subclasses that do not re-implement the
methods (such as template class specializations).  The decorator
@c local_method_names() addresses this problem.  Also, in case of nested template
classes (say, elliptic_curves.polynomials.naive.CurvePolynomials),
the template parameters bloat the type name; the decorator @c profiling_name()
alleviates the issue.

@package   support.profiling
@author    Peter Dinges <pdinges@acm.org>
"""

def profiling_name(name):
    """
    A class decorator that sets the @p name that will show up in profiles
    generated with the @c cProfile module.
    
    Usage example:
    @code
    @local_method_names
    @profiling_name( "GF<{_size}>" )
    class FiniteField( Field, metaclass=template( "_size" ) ):
        ...
    @endcode
    
    @param name    A string that contains the class name (which is usually
                   shorter than the original name).  For template classes, the
                   string may contain format-string variables for the
                   parameters.
    
    @note  The function requires the @c local_method_name() decorator to show
           an effect. 
    
    @see   The sources of rings.quotients.naive.QuotientRing for a usage
           example and support.types.template() for information about template
           classes.
    """
    def class_wrapper(cls):
        setattr(cls, "__profiling_name__", name)
        return cls
    return class_wrapper


from .types import is_incomplete

def local_method_names(cls):
    """
    A class decorator that makes the function names used by the @c cProfile
    module local to the class of use (rather than the class of definition).
    
    The @c cProfile module uses the name of a function's code object as the
    profile name.  Therefore, calls to methods in subclasses that do not
    re-implement the method are counted as calls to the parent class.  In
    template classes, this makes the call profile too coarse.
    
    Use profiling_name() to get shorter class names.

    @note  The decorator copies the code objects; it "flattens" the class.
           Therefore, re-assigning methods will annihilate the decorator
           effects for the method.

    @see   The sources of rings.quotients.naive.QuotientRing for a usage
           example and support.types.template() for information about template
           classes.
    """
    if getattr( cls.__class__, "__operation_renaming__", False ):
        return cls

    original_new = cls.__class__.__new__

    def prefixing_new(meta_class, class_name, bases, class_dict, **kw_arguments):
        class_object = original_new( meta_class, class_name, bases, class_dict, **kw_arguments )

        if is_incomplete( class_object ):
            return class_object

        if "__operation_renaming__" in class_object.__dict__:
            return class_object

        profiling_name = __profiling_str( class_object )
        __localize_method_names(
                    class_object.__class__,
                    [ "__new__", "__call__" ],
                    "{cls}::<meta>{{meth}}".format( cls = profiling_name )
                )
        
        __flatten_methods( class_object )
        __localize_method_names(
                    class_object,
                    __method_names( class_object ),
                    "{cls}::{{meth}}".format( cls = profiling_name )
                )
        
            
        setattr( class_object, "__operation_renaming__", True )
        return class_object
    
    cls.__class__.__new__ = prefixing_new
    setattr( cls.__class__, "__operation_renaming__", True )
    
    return cls



def rename_function( function, name, filename=None, firstlineno=-1 ):
    """
    Rename a function and its associated code object.
    
    This is handy when using the @c profile and @c cProfile modules:
    both retrieve the function names from the code object
    (the @c co_name attribute); @c __name__ is ignored.
    """
    # Renaming a function in the profile thus requires generating a new
    # code object. As CodeType.__doc__ notes, this is not for the
    # faint of heart.
    
    # Modify the unbound function object of methods
    if hasattr( function, "__func__" ):
        function = function.__func__

    try:
        code = function.__code__
    
    except AttributeError:
        message = "expected '{func}' to have an associated code object ('__code__' attribute)" 
        raise ValueError( message.format( function ) )
    
    # Copy old values if unspecified
    if filename is None:
        filename = code.co_filename
    if firstlineno == -1:
        firstlineno = code.co_firstlineno
    
    renamed_code = types.CodeType(
                      code.co_argcount,
                      code.co_kwonlyargcount,
                      code.co_nlocals,
                      code.co_stacksize,
                      code.co_flags,
                      code.co_code,
                      code.co_consts,
                      code.co_names,
                      code.co_varnames,
                      str( filename ),
                      str( name ),
                      int( firstlineno ),
                      code.co_lnotab,
                      code.co_freevars,
                      code.co_cellvars
                  )

    function.__name__ = str( name )
    function.__code__ = renamed_code


def __method_names( class_object ):
    """
    Return a dictionary with the methods defined in the class (not counting
    inherited methods).
    
    This function is not intended for direct use.
    """
    return [ key for key, value in class_object.__dict__.items() \
             if type( value ) in function_types ]


def __localize_method_names( class_object, method_names, format_string ):
    """
    Make all inherited (and not re-implemented) methods local to the class
    and rename them accordingly.  That way, the @c cProfile module
    distinguishes between calls the original and the inherited implementation.
    
    This function is not intended for direct use.
    """
    for method_name in method_names:
        method = __get_dict_item( class_object, method_name )
        method_copy = __copy_function( method )
        
        new_name = format_string.format( meth = method_name )
        rename_function( method_copy, new_name )
        
        setattr( class_object, method_name, method_copy )


def __flatten_methods( class_object ):
    """
    Copy all inherited (and not re-implemented) methods to the local
    class dictionary.
    
    This function is not intended for direct use.
    """
    for attribute_name in dir( class_object ):
        # Skip local attributes
        if attribute_name in class_object.__dict__:
            continue
        
        # Skip non-method attributes (for example class variables)
        method = __get_dict_item( class_object, attribute_name )
        if type( method ) not in function_types:
            continue 
        
        method_copy = __copy_function( __unwrap( method ) )
        setattr(class_object, attribute_name, method_copy )


def __get_dict_item( class_object, key ):
    """
    Return the class dictionary entry with key @p key; traverse the parent
    classes until a matching entry was found.  Otherwise raise an
    @c AttributeError.
    
    This function is not intended for direct use. 
    """
    for cls in class_object.__mro__:
        if key in cls.__dict__:
            return cls.__dict__[ key ]
    
    message = "object '{name}' has no attribute '{key}'"
    raise AttributeError(
                     message.format( name = class_object.__name__, key = key )
                 ) 


def __copy_function( function ):
    """
    Create a completely independent copy of @p function.
    
    The function also copies the code object of @p function.
    
    This function is not intended for direct use.
    """
    if type( function ) in [ staticmethod, classmethod ]:
        return type( function )( __copy_function( function.__func__ ) )
    
    if type( function ) not in [ types.FunctionType, types.MethodType ]:
        message = "expected function or method type (got {0})"
        raise ValueError( message.format( function ) )
    
    if type( function ) is types.MethodType:
        function = function.__func__

    code = function.__code__
    code_copy = types.CodeType(
                      code.co_argcount,
                      code.co_kwonlyargcount,
                      code.co_nlocals,
                      code.co_stacksize,
                      code.co_flags,
                      code.co_code,
                      code.co_consts,
                      code.co_names,
                      code.co_varnames,
                      code.co_filename,
                      code.co_name,
                      code.co_firstlineno,
                      code.co_lnotab,
                      code.co_freevars,
                      code.co_cellvars
                  )
    
    function_copy = types.FunctionType(
                          code_copy,
                          function.__globals__,
                          function.__name__,
                          function.__defaults__,
                          function.__closure__
                      )
    
    # Re-bind methods to their instance
    if type( function ) is types.MethodType:
        return types.MethodType( function_copy, function.__self__)

    return function_copy


def __unwrap( method ):
    """
    Return the original function inside a method wrapper.
    
    This function is not intended for direct use.
    
    @see   support.operators.operand_casting()
    """
    if hasattr( method, "__wrapped_method__" ):
        return __unwrap( getattr( method, "__wrapped_method__" ) )
    
    return method


def __profiling_str(obj):
    """
    Return the formatted name of @p obj as set by the @c profiling_name()
    decorator.  Fall back to __str__() if necessary.
    
    This function is not intended for direct use.
    """
    # FIXME: Endless recursion for cyclic dependencies.
    if isinstance(obj, type) and hasattr(obj, "__profiling_name__"):
        if hasattr( obj.__class__, "__parameter_map__" ):
            args = [ (k, __profiling_str(v)) for k,v in obj.__class__.__parameter_map__.items() ]
        else:
            args = []
            
        try:
            return obj.__profiling_name__.format( **dict( args ) )
        except KeyError:
            pass
    
    return str(obj)


import types

function_types = [
          types.FunctionType,
          types.MethodType,
          staticmethod,
          classmethod,
      ]
    