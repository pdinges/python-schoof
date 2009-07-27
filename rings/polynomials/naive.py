# -*- coding: utf-8 -*-
# $Id$

class PolynomialRing:
    """
    Ring of polynomials in one indeterminate with coefficients from the
    provided field.
    
    Requiring the coefficients to come from a field is an unnecessary
    specialization. However, it is sufficient for our purposes and allows
    for (simple) division.
    """    
    def __init__(self, coefficient_field):
        self._coefficient_field = coefficient_field
    
    def coefficient_field(self):
        return self._coefficient_field
        
    def __call__(self, *coefficient_list):
        """
        Create a new polynomial from the given list of coefficients.
        
        Note that the list must be ordered ascending: first the constant,
        then the linear, quadratic and cubic coefficients; and so on.
        """
        converted_coefficients = [ self._coefficient_field(c) for c in coefficient_list ]
        return ListPolynomial( self, converted_coefficients )
    
    def zero(self):
        return ListPolynomial( self, [ self._coefficient_field.zero() ] )
    
    def one(self):
        return ListPolynomial( self, [ self._coefficient_field.one() ] )    
    
    def __str__(self):
        # Requires the names of indeterminates and the field.
        name  = """Ring of polynomials in one indeterminate """ \
                + """with coefficients in the {0}"""
        return name.format( self._coefficient_field )


from rings import DefaultImplementationElement

class ListPolynomial(DefaultImplementationElement):
    """
    Polynomial with coefficients from a field.

    The implementation emphasizes simplicity and omits all possible
    speedups for simplicity and ease of understanding. It uses simple lists
    to store the coefficients.
    """
    def __init__(self, polynomial_ring, coefficient_list):
        # List of coefficients in ascending order without leading zeros.
        # Example: x^2 + 2x + 5 = [5, 2, 1]
        self.__source_ring = polynomial_ring
        self.__coefficients = coefficient_list
        self.__remove_leading_zeros()

    
    def degree(self):
        # FIXME: The degree of the zero polynomial is minus infinity.
        return len( self.__coefficients ) - 1
    
    
    def __bool__(self):
        # At least one non-zero coefficient present
        return len( self.__coefficients ) > 0
    
    
    def __eq__(self, other):
        if self.degree() != other.degree():
            return False
        
        # zip() is OK because we have identical length
        for x, y in zip(self.__coefficients, other.__coefficients):
            if x != y:
                return False

        return True
    
    
    def __add__(self, other):
        coefficient_pairs = self.__pad_and_zip(
                                    self.__coefficients,
                                    other.__coefficients,
                                    self.__source_ring.coefficient_field().zero()
                                )
        coefficient_sums = [ x + y for x, y in coefficient_pairs ]
        return self.__class__( self.__source_ring, coefficient_sums )
    
    
    def __neg__(self):
        return self.__class__(
                    self.__source_ring,
                    [ -c for c in self.__coefficients ]
                )
    
    
    def __mul__(self, other):
        # Initialize result as list of all zeros
        zero = self.__source_ring.coefficient_field().zero()
        result = [ zero ] * (self.degree() + other.degree() + 2)
        
        for i, x in enumerate(self.__coefficients):
            for j, y in enumerate(other.__coefficients):
                result[i + j]  +=  x * y 
        
        return self.__class__( self.__source_ring, result )
    
    
    def __divmod__(self, other):
        dividend = self.__coefficients[:]
        divisor = other.__coefficients[:]
        n = other.degree()
        
        zero = self.__source_ring.coefficient_field().zero()
        quotient = [ zero ] * (self.degree() - n + 1)
        
        for k in reversed(range( 0, len(quotient) )):
            quotient[k] = dividend[n + k] / divisor[n]
            for j in range(k, n + k):
                dividend[j] -= quotient[k] * divisor[j - k]
    
        remainder = dividend[ 0 : n ]
        
        return self.__class__(self.__source_ring, quotient), \
                self.__class__(self.__source_ring, remainder)
    
    
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
        summands = [ "{0} * x**{1}".format(c, i) \
                        for i, c in enumerate( self.__coefficients ) ]
        
        # Write constant and linear term without exponents
        summands[0] = str( self.__coefficients[0] )
        if len( self.__coefficients ) > 1:
            summands[1] = "{0} * x".format( self.__coefficients[1] ) 
        
        return "( {0} )".format( " + ".join( reversed( summands ) ) )
        
        
    @staticmethod
    def __pad_and_zip(list1, list2, padding_element):
        max_length = max( len(list1), len(list2) )
        padded_list1 = list1 + ( [padding_element] * (max_length - len(list1)) )
        padded_list2 = list2 + ( [padding_element] * (max_length - len(list2)) )
        return zip( padded_list1, padded_list2 )
