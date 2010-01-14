# -*- coding: utf-8 -*-
# $Id$

import types

def rename_code_object( function, filename, name, firstlineno ):
    code = function.__code__
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
                      filename,
                      name,
                      firstlineno,
                      code.co_lnotab,
                      code.co_freevars,
                      code.co_cellvars
                  )
    
    renamed_function = types.FunctionType(
                          renamed_code,
                          function.__globals__,
                          name,
                          function.__defaults__,
                          function.__closure__
                      )
    if type( function ) is types.FunctionType:
        return renamed_function
    elif type( function ) is types.MethodType:
        return types.MethodType( renamed_function, function.__self__)


def prefix_operations(cls):
    if getattr( cls.__class__, "__operation_renaming__", False ):
        return cls

    original_new = cls.__class__.__new__

    def prefixing_new(meta_class, class_name, bases, class_dict, **kw_arguments):
        class_object = original_new( meta_class, class_name, bases, class_dict, **kw_arguments )

        # Not necessarily: meta_class is class_object.__class__
        if getattr( class_object.__class__, "__unbound_parameters__", False ):
            return class_object
        
        if "__operation_renaming__" in class_object.__dict__:
            return class_object

        
        for operation_name, operation in [
                      ( "__new__", getattr( class_object.__class__, "__new__" ) ),
                      ( "__call__", getattr( class_object.__class__, "__call__" ) ),
                                          ]:
            if type(operation) not in ( types.FunctionType, types.MethodType ):
                continue

            new_name = "{cls}::<meta>{op}".format( cls = __profiling_str(class_object), op = operation_name )
            setattr(class_object.__class__, operation_name, rename_code_object(
                                           operation,
                                           operation.__code__.co_filename,
                                           new_name,
                                           operation.__code__.co_firstlineno
                                        )
                                    )

        
        for operation_name, operation in class_object.__dict__.items():
            if type(operation) not in ( types.FunctionType, types.MethodType ):
                continue
        
            new_name = "{cls}::{op}".format( cls = __profiling_str(class_object), op = operation_name )
            setattr(class_object, operation_name, rename_code_object(
                                           operation,
                                           operation.__code__.co_filename,
                                           new_name,
                                           operation.__code__.co_firstlineno
                                        )
                                    )
        setattr( class_object, "__operation_renaming__", True )
        return class_object
    
    cls.__class__.__new__ = prefixing_new
    setattr( cls.__class__, "__operation_renaming__", True )
    
    return cls


def __profiling_str(obj):
    # FIXME: Endless recursion for cyclic dependencies.
    if hasattr(obj, "__profiling_name__"):
        if hasattr( obj.__class__, "__parameter_map__" ):
            args = [ (k, __profiling_str(v)) for k,v in obj.__class__.__parameter_map__.items() ]
        else:
            args = []
            
        try:
            return obj.__profiling_name__.format( **dict( args ) )
        except KeyError:
            pass
    
    return str(obj)


def profiling_name(name):
    def class_wrapper(cls):
        setattr(cls, "__profiling_name__", name)
        return cls
    return class_wrapper
    