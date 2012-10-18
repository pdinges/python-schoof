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
A naive implementation of polynomial rings with coefficients from a field.

@package   rings.polynomials.naive
@author    Peter Dinges <pdinges@acm.org>
"""

from rings import CommutativeRing

from support.types import template
from support.operators import operand_casting
from support.profiling import profiling_name, local_method_names

@operand_casting
@local_method_names
@profiling_name( "{_coefficient_field}[x]")
class Polynomials( CommutativeRing, metaclass=template( "_coefficient_field" ) ):
    """
    A ring of polynomials in one indeterminate with coefficients from the
    provided field; the polynomials support infix notation for ring operations,
    as well as mixed argument types.
    
    This is a template class that must be instantiated with the coefficient
    field.  Use it, for example, as follows:
    @code
    # Instantiate the template; GF7x is a class (here: polynomials over GF7)
    GF7 = fields.finite.naive.FiniteField( 7 )
    GF7x = Polynomials( GF7 )
    p = GF7x(1, 1)    # Create a polynomial: x + 1
    q = GF7x(-1, 1)   # Another polynomial: x - 1
    p * q == GF7x(-1, 0, 1)    # This is true: (x + 1)(x - 1) = x^2 - 1
    type(p) is GF7x   # This is also true

    # Use the polynomial 'x' for a more natural syntax
    x = GF7(0, 1)
    x**3 - 2*x + 1 == GF7x(1, -2, 0, 1)
    @endcode
    
    The polynomial ring operations are defined in terms of the coefficient
    field operations.  For everything to work as expected, the template
    argument must be a class whose instances implement the fields.Field
    interface.  Typically, this will be some specialization of
    fields.finite.naive.FiniteField.
    
    Rings, however, also work as a source of coefficients.  Only division
    requires that the leading coefficient is a unit. 

    @note  The implementation emphasizes simplicity over speed; it omits
           possible optimizations.
    
    @note  The class uses the operand_casting() decorator: @c other operands in
           binary operations will first be treated as Polynomial elements.
           If that fails, the operation will be repeated after @p other was fed
           to the constructor __init__().  If that fails, too, then the
           operation returns @c NotImplemented (so that @p other.__rop__()
           might be invoked).
    
    @see   For example, Robinson, Derek J. S.,
           "An Introduction to Abstract Algebra", p. 100.
    """    

    #- Instance Methods ----------------------------------------------------------- 
    
    def __init__(self, element_description, *further_coefficients):
        """
        Create a new polynomial from the given @p element_description.
        
        @param element_description
            Valid input values are:
            - A Polynomial over the same field: then the polynomial is copied
              and @p further_coefficients is ignored.
            - An iterable object (with an @c __iter__() method): then the
              polynomial coefficients are read from the iterable and, again,
              @p further_coefficients is ignored.  The list must be in
              ascending order: first the constant, then the linear, quadratic,
              and cubic coefficients; and so on.
            - Any number of arguments that can be interpreted as coefficient
              field elements; they will be combined
              into the list of coefficients
        
        @param further_coefficients    The list of variable positional
                                       arguments.
        
        For example, there are several ways to construct the polynomial
        @f$ x^3 + 4x^2 - 3x + 2@f$:
        @code
        # Suppose R is a Polynomials template specialization
        # List of coefficients
        p2 = R( [2, -3, 4, 1] )
        # Variable argument count
        p3 = R( 2, -3, 4, 1 )
        # Copy
        p1 = R( p2 )
        @endcode
        
        @note  Leading zeros will be ignored.
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
        """
        Return a copy of the list of coefficients.  The list is in ascending
        order: it starts with the constant coefficient, then the linear,
        quadratic, and cubic coefficients; and so on.  It ends with the leading
        coefficient.
        """
        return self.__coefficients[:]


    def leading_coefficient(self):
        """
        Return the leading coefficient, or zero if @p self is
        the zero polynomial.
        """
        if self.__coefficients:
            return self.__coefficients[-1]
        else:
            return self._coefficient_field.zero()


    def degree(self):
        """
        Return the degree of the polynomial.
        
        @note  The zero polynomial has degree @f$ -\infty @f$; however, this
               implementation returns the number @f$ -2^{30} @f$ to avoid
               special constructions that side-step Python's @c int objects.
               For practical purposes, this should suffice.
        """
        if not self.__coefficients:
            # FIXME: The degree of the zero polynomial is minus infinity.
            #        This will, however, do for now.
            return -( 2**30 )
        return len( self.__coefficients ) - 1

    
    def __bool__(self):
        """
        Test whether the polynomial is non-zero: return @c True if, and only
        if, at least one coefficient is non-zero. Return @c False if all
        coefficients are zero.
        
        Implicit conversions to boolean (truth) values use this method, for
        example when @c x is an element of Polynomials:
        @code
        if x:
            do_something()
        @endcode
        """
        return bool( self.__coefficients )


    def __eq__(self, other):
        """
        Test whether another polynomial @p other is equal to @p self; return
        @c True if that is the case.  The infix operator @c == calls
        this method.
        
        Two polynomials are equal if, and only if, all their coefficients are
        equal. 
        """
        if self.degree() != other.degree():
            return False
        
        # zip() is OK because we have identical length
        for x, y in zip(self.__coefficients, other.__coefficients):
            if x != y:
                return False

        return True


    def __add__(self, other):
        """
        Return the sum of @p self and @p other. The infix operator @c + calls
        this method.
        
        Polynomials add coefficient-wise without carrying: the sum of two
        polynomials @f$ \sum_{k} a_{k}x^{k} @f$ and
        @f$ \sum_{k} b_{k}x^{k} @f$ is the polynomial
        @f$ \sum_{k} (a_{k} + b_{k})x^{k} @f$.
        """
        zero = self._coefficient_field.zero()
        coefficient_pairs = self.__pad_and_zip(
                                    self.__coefficients,
                                    other.__coefficients,
                                    zero
                                )
        coefficient_sums = [ x + y for x, y in coefficient_pairs ]
        return self.__class__( coefficient_sums )
    
    
    def __neg__(self):
        """
        Return the additive inverse (the negative) of @p self.
        
        A polynomial is negated by negating its coefficients: the additive
        inverse of @f$ \sum_{k} a_{k}x^{k} @f$ is @f$ \sum_{k} -a_{k}x^{k} @f$.
        """
        return self.__class__(
                    [ -c for c in self.__coefficients ]
                )
    
    
    def __mul__(self, other):
        """
        Return the product of @p self and @p other. The infix operator @c *
        calls this method.
        
        Two polynomials are multiplied through convolution of their
        coefficients: for polynomials @f$ \sum_{k} a_{k}x^{k} @f$ and
        @f$ \sum_{k} b_{k}x^{k} @f$, their product is the polynomial
        @f$ \sum_{k} \sum_{j=0}^{k}(a_{j} + b_{k-j})x^{k} @f$.
        """
        # Initialize result as list of all zeros
        zero = self._coefficient_field.zero()
        # Add 2 because degrees count from 0.
        result = [ zero ] * (self.degree() + other.degree() + 2)
        
        for i, x in enumerate(self.__coefficients):
            for j, y in enumerate(other.__coefficients):
                result[i + j]  +=  x * y 
        
        return self.__class__( result )


    def __divmod__(self, other):
        """
        Return the quotient and remainder of @p self divided by @p other.
        
        The built-in method @c divmod() calls this method.  For the returned
        values @c quotient and @c remainder, we have
        @code
        self == quotient * other + remainder
        @endcode
        """
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
    
    
    def __call__(self, point):
        """
        Return the polynomial function's value at @p point.
        
        This method evaluates the polynomial by replacing the indeterminate
        with @p point and summing the powers: for a polynomial
        @f$ p(x) = \sum_{k} a_{k}x^{k} @f$, the value at @f$ c @f$ is
        @f$ p(c) = \sum_{k} a_{k}c^{k} @f$.
        """
        return sum( [ c * point**i for i, c in enumerate(self.__coefficients) ] )
    
    
    #- Class Methods----------------------------------------------------------- 
    
    @classmethod
    def coefficient_field(cls):
        """
        Return the coefficient field.
        """
        return cls._coefficient_field


    @classmethod
    def zero(cls):
        """
        Return the polynomial ring's neutral element of addition: the zero
        polynomial.
        """
        return cls( cls._coefficient_field.zero() )
    
    
    @classmethod
    def one(cls):
        """
        Return the polynomial ring's neutral element of multiplication: the
        constant polynomial one.
        """
        return cls( cls._coefficient_field.one() )


    #- Auxiliary Functions ---------------------------------------------------- 

    def __remove_leading_zeros(self):
        """
        Remove all leading zeros from the list of coefficients.  This might
        empty the list completely. 
        """
        while len( self.__coefficients ) > 0 \
                and not self.__coefficients[-1]:
            self.__coefficients.pop()


    @staticmethod
    def __pad_and_zip(list1, list2, padding_element):
        """
        Combine @p list1 and @p list1 into a single list of pairs.  If the
        lists have different lengths, pad the shorter list with
        @p padding_element: fill in elements until they have the same length.
        """
        max_length = max( len(list1), len(list2) )
        padded_list1 = list1 + ( [padding_element] * (max_length - len(list1)) )
        padded_list2 = list2 + ( [padding_element] * (max_length - len(list2)) )
        return zip( padded_list1, padded_list2 )
