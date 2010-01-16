# -*- coding: utf-8 -*-
# $Id$

from rings import CommutativeRing

from support.types import template
from support.operators import operand_casting
from support.profiling import profiling_name, local_method_names

@operand_casting
@local_method_names
@profiling_name( "{_coefficient_field}[x]")
class Polynomials( CommutativeRing, metaclass=template( "_coefficient_field" ) ):
    """
    Polynomial in one indeterminate with coefficients from the
    provided field.
    
    Requiring the coefficients to come from a field is an unnecessary
    specialization. However, it is sufficient for our purposes and allows
    for (simple) division.
    """    

    def __init__(self, element_description, *further_coefficients):
        """
        Create a new polynomial from the given description.
        
        Valid descriptions are:
          - ListPolynomials over the same field
            (further_coefficients will be ignored)
          - iterable objects that provides the list of coefficients
            (again, further_coefficients will be ignored)
          - any number of function arguments; they will be combined
            into the list of coefficients 
        
        Note that the list must be in ascending order: first the constant,
        then the linear, quadratic, and cubic coefficients; and so on.
        """
        # List of coefficients is in ascending order without leading zeros.
        # Example: x^2 + 2x + 5 = [5, 2, 1]
        if isinstance(element_description, self.__class__):
            # A reference suffices because objects are immutable
            self.__coefficients = element_description.__coefficients
        
        else:
            if type(element_description) in [ list, tuple ]:
                coefficients = element_description
            else:
                coefficients = [ element_description ] + list(further_coefficients)  

            F = self._coefficient_field
            self.__coefficients = [ F(c) for c in coefficients ]

        self.__remove_leading_zeros()

    
    def coefficients(self):
        return self.__coefficients[:]


    def degree(self):
        # FIXME: The degree of the zero polynomial is minus infinity.
        return len( self.__coefficients ) - 1

    
    def __eq__(self, other):
        if self.degree() != other.degree():
            return False
        
        # zip() is OK because we have identical length
        for x, y in zip(self.__coefficients, other.__coefficients):
            if x != y:
                return False

        return True


    def __bool__(self):
        return bool( self.__coefficients )


    def __add__(self, other):
        zero = self._coefficient_field.zero()
        coefficient_pairs = self.__pad_and_zip(
                                    self.__coefficients,
                                    other.__coefficients,
                                    zero
                                )
        coefficient_sums = [ x + y for x, y in coefficient_pairs ]
        return self.__class__( coefficient_sums )
    
    
    def __neg__(self):
        return self.__class__(
                    [ -c for c in self.__coefficients ]
                )
    
    
    def __mul__(self, other):
        # Initialize result as list of all zeros
        zero = self._coefficient_field.zero()
        # Add 2 because degrees count from 0.
        result = [ zero ] * (self.degree() + other.degree() + 2)
        
        for i, x in enumerate(self.__coefficients):
            for j, y in enumerate(other.__coefficients):
                result[i + j]  +=  x * y 
        
        return self.__class__( result )


    def __divmod__(self, other):
        # Lists will be modified, so copy them
        dividend = self.__coefficients[:]
        divisor = other.__coefficients[:]
        n = other.degree()
        
        zero = self._coefficient_field.zero()
        quotient = [ zero ] * (self.degree() - n + 1)
        
        for k in reversed(range( 0, len(quotient) )):
            quotient[k] = dividend[n + k] / divisor[n]
            for j in range(k, n + k):
                dividend[j] -= quotient[k] * divisor[j - k]
    
        remainder = dividend[ 0 : n ]
        
        return self.__class__( quotient ), \
                self.__class__( remainder )

    
    def __floordiv__(self, other):
        return divmod(self, other)[0]

    
    def __mod__(self, other):
        return divmod(self, other)[1]
    

    def multiplicative_inverse(self):
        raise TypeError
    
    
    def __call__(self, point):
        return sum( [ c * point**i for i, c in enumerate(self.__coefficients) ] )
    
    
    def __remove_leading_zeros(self):
        while len( self.__coefficients ) > 0 \
                and not self.__coefficients[-1]:
            self.__coefficients.pop()
        
        
    def __str__(self):
        summands = [ "{0} * x**{1}".format(c, i+2) \
                        for i, c in enumerate( self.__coefficients[2:] ) if c ]
        
        # Write constant and linear term without exponents
        if len( self.__coefficients ) > 0 and self.__coefficients[0]:
            summands.insert( 0, str( self.__coefficients[0] ) )
        if len( self.__coefficients ) > 1 and self.__coefficients[1]:
            summands.insert( 1, "{0} * x".format( self.__coefficients[1] ) ) 
        
        return "( {0} )".format( " + ".join( reversed( summands ) ) )
        
        
    @classmethod
    def zero(cls):
        return cls( cls._coefficient_field.zero() )
    
    @classmethod
    def one(cls):
        return cls( cls._coefficient_field.one() )

    @classmethod
    def coefficient_field(cls):
        return cls._coefficient_field

    @staticmethod
    def __pad_and_zip(list1, list2, padding_element):
        max_length = max( len(list1), len(list2) )
        padded_list1 = list1 + ( [padding_element] * (max_length - len(list1)) )
        padded_list2 = list2 + ( [padding_element] * (max_length - len(list2)) )
        return zip( padded_list1, padded_list2 )
