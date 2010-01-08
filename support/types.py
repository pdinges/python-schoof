# -*- coding: utf-8 -*-
# $Id$

class TypeTemplate(type):
    """
    A template meta-class prototype; use function template() to create
    actual meta-class types. 
    
    Outline of usage and effects:
    > T = template("a", "b") -> Template meta-class with parameters "a" and "b";
      usable as meta-class for _any_ class
    > class C(metaclass=T) -> Template with parameters for C; type(C) = T<a,b>
    > C(4) = Template for C with parameter "a" set; type(C(4)) = T<a=3,b>.
      T<a=3,b> is a subtype of T<a,b>
    > class D(C) = Template for D with parameters "a" and "b"; type(D) = T<a,b>
    > class E(C, b=) = Template for E with parameter "b" set; type(E) = T<a,b=1>
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
                                      base.__name__,
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
    
    

def template( *parameters ):
    """
    Factory function to create template meta-classes.
    
    Usage example:
      class C(metaclass=template("a", "b")): pass
    """
    template_name = "TypeTemplate<{0}>".format( ", ".join( parameters ) )
    template_bases = tuple( [ TypeTemplate ] )
    template_dict = {   "__parameters__": parameters,
                        "__unbound_parameters__": parameters,
                        "__parameter_map__": {}
                     }
    return type( template_name, template_bases, template_dict )
