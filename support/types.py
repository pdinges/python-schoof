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
A template meta-class system.

Template meta-classes offer high modularity and natural syntax for
mathematical objects; for instance, see rings.polynomials.naive.Polynomials
or fields.finite.naive.FiniteField

@package   support.types
@author    Peter Dinges <pdinges@acm.org>
"""

def template( *parameters ):
    """
    Factory function to create template meta-classes.  The function arguments
    are the names of the template parameters.  After specialization, the bound
    parameters are available as class attributes of the given names.
    
    Usage example:
    @code
    # Create a class template C with parameters "a" and "b"
    class C( metaclass=template("a", "b") ):
        pass
    
    # Instantiate the template with values 23 and 42; Cp is a class object.
    Cp = C(23, 42)
    isinstance(Cp, type) == True   # This holds
    Cp.a == 23
    Cp.b == 42
    
    # Construct Cp objects
    x = Cp()
    type(x) is Cp                  # This also holds
    @endcode
    
    @see TypeTemplate
    """
    template_name = "TypeTemplate<{0}>".format( ", ".join( parameters ) )
    template_bases = tuple( [ TypeTemplate ] )
    template_dict = {   "__parameters__": parameters,
                        "__unbound_parameters__": parameters,
                        "__parameter_map__": {}
                     }
    return type( template_name, template_bases, template_dict )


def is_incomplete( class_object ):
    """
    Test whether the template class @p class_object has any unbound parameters.
    
    @return    @c False if the template class is fully specialized; @c True
               otheriwse (that is, if it has unbound parameters).
    """
    return getattr( class_object.__class__, "__unbound_parameters__", False )


class TypeTemplate(type):
    """
    A template meta-class prototype; use the function @c template() to create
    actual meta-class types. 
    
    Outline of usage and effects:
    @code
    # Create a template meta-class 'T' with parameters "a" and "b".
    # The meta-class can be used for _any_ class.
    T = template("a", "b")
    
    # Create a class template with parameters "a" and "b" (these come from T)
    # The type of C is T<a,b>
    class C(metaclass=T):
        def __str__(self): return "C"
    
    # Partially specialize C by setting parameter a; this yields a class
    # template D with the single parameter "b"; type(D) is T<a=4,b> and
    # is a subtype of T<a,b>
    D = C(4)
    
    # Create a subclass template E with parameters "a" and "b"; use this to
    # re-implement methods from the class template C
    class E(C):
        def __str__(self): return "E"
    # Parameters can be bound while subclassing template classes
    class F(C, b=2):
        def __str__(self): return "F with b=2"
    @endcode
    
    @see   The sources of rings.quotients.naive.QuotientRing and
           fields.finite.naive.FiniteField for examples.
    """
    
    # Note: type objects are their own meta-classes.
    #       Both, __init__() and __new__(), behave like class methods;
    #       they are called in order __new__(), __init__() and must
    #       have identical signatures (even though __init__() ignores
    #       the keyword arguments).
    def __init__(meta_class, class_name, bases, class_dict, **kw_arguments):
        """
        Initialize a new type object.
        
        Behaves like a class method because type objects are their own
        meta-classes.
        """
        type.__init__(meta_class, class_name, bases, class_dict)

    
    def __new__(meta_class, class_name, bases, class_dict, **kw_arguments):
        """
        Create a new type object, for example through a 'class' statement.
        
        Behaves like a class method and is called before __init__().
        """
        if kw_arguments:
            # Assigning values to the parameters means specializing the
            # template. Therefore, derive a subclass from this meta-class
            # and make it create the actual type object.
            specialized_meta_class = meta_class.__specialize( kw_arguments )
            # Base classes must have the same specialized meta-class.
            specialized_bases = []
            for base in bases:
                if base.__class__ is meta_class:
                    specialized_bases.append(
                        specialized_meta_class.__new__(
                                      specialized_meta_class,
                                      base.__plain_name__,
                                      base.__bases__,
                                      base.__dict__
                              )
                        )
                else:
                    specialized_bases.append( base )
            
            return specialized_meta_class.__new__(
                              specialized_meta_class,
                              class_name,
                              tuple( specialized_bases ),
                              class_dict
                          )
        else:
            # No specialization. Create a type object.
            extended_name = meta_class.__template_name(
                                       class_name,
                                       meta_class.__parameters__,
                                       meta_class.__parameter_map__
                                   )
            extended_dict = meta_class.__parameter_map__.copy()
            extended_dict.update( class_dict )
            extended_dict[ "__plain_name__" ] = class_name
            return type.__new__(
                        meta_class,
                        extended_name,
                        bases,
                        extended_dict
                    )


    def __call__(self, *arguments, **kw_arguments):
        """
        Specialize the template or create an instance.
        
        Note that this bends python's usual semantics: calling a template
        class may return types and instances, rather than always returning
        instances.
        """
        unbound_parameters = self.__unbound_parameters__ 
        if unbound_parameters:
            # There still are unbound parameters, so calling the type object
            # means specializing it.
            if len(arguments) > len(unbound_parameters):
                    message = "{0} takes at most {1} arguments ({2} given)".format(
                                   self.__name__,
                                   len( unbound_parameters ),
                                   len( arguments )
                                )
                    raise TypeError( message )
            
            pos_parameters = unbound_parameters[ : len(arguments) ]
            ambiguous_parameters = set( pos_parameters ).intersection( set( kw_arguments.keys() ) )
            if ambiguous_parameters:
                message = "multiple values for parameters {0}"
                raise TypeError( message.format( tuple( ambiguous_parameters ) ) )

            parameter_map = kw_arguments.copy()
            parameter_map.update( zip( pos_parameters, arguments ) )
            
            return self.__class__.__new__(
                            self.__class__,
                            self.__plain_name__,
                            self.__bases__,
                            self.__dict__,
                            **parameter_map
                        )
        else:
            # All parameters are set; create an instance.
            return type.__call__( self, *arguments, **kw_arguments )

            
    @classmethod
    def __specialize(meta_class, kw_arguments):
        """
        Derive a sub-template of the given template meta-class by setting
        template parameters.
        """
        unbound_parameters = meta_class.__unbound_parameters__
        if set( kw_arguments.keys() ) <= set( unbound_parameters ):
            specialization_dict = meta_class.__dict__.copy()
            specialization_dict[ "__parameters__" ] = getattr( meta_class, "__parameters__" )
            remaining_parameters = [ p for p in unbound_parameters if p not in kw_arguments ]
            specialization_dict[ "__unbound_parameters__" ] = tuple( remaining_parameters )
            specialization_dict[ "__parameter_map__" ] = getattr( meta_class, "__parameter_map__" ).copy() 
            specialization_dict[ "__parameter_map__" ].update( kw_arguments )

            specialization_bases = tuple( [ meta_class ] )
            specialization_name = meta_class.__template_name(
                                         "TypeTemplate",
                                         specialization_dict[ "__parameters__" ],
                                         specialization_dict[ "__parameter_map__" ]
                                     )
            return type( specialization_name, specialization_bases, specialization_dict )
        
        # TODO: Add detail to messages
        elif set( kw_arguments.keys() ).intersection( meta_class.__parameter_map__.keys() ):
            message = "template parameter already set"
            raise TypeError( message )
        else:
            message = "not a template parameter"
            raise TypeError( message )
            
            
    @staticmethod
    def __template_name(class_name, parameters, parameter_map):
        """
        Return a C++ style template name, for example 'C<a=3,b>'.
        """
        parameter_strings = []
        for p in parameters:
            if p in parameter_map:
                parameter_strings.append( "{0}={1}".format( p, str( parameter_map[p] ) ) )
            else:
                parameter_strings.append( p )
                
        return "{0}<{1}>".format( class_name, ", ".join( parameter_strings ) )
