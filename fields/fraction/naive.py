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
A naive implementation of fraction fields (rational fields over an
integral domain).

@package   fields.fraction.naive
@author    Peter Dinges <pdinges@acm.org>
"""

from fields import Field

from support.types import template
from support.operators import operand_casting
from support.profiling import profiling_name, local_method_names

@operand_casting
@local_method_names
@profiling_name( "Q<{_integral_domain}>" )
class FractionField( Field, metaclass=template("_integral_domain") ):
    """
    A field of formal quotients (fractions)
    @f$ \frac{\mathrm{numerator}}{\mathrm{denominator}} @f$ over an integral
    domain; the field elements support infix notation for field operations,
    and mixed argument types.

    This is a template class that must be instantiated with the underlying
    integral domain. For example:
    @code
    # Instantiate the template; Q is a class (here: the rational numbers)
    Q = FractionField( rings.integers.naive.Integers )
    x = Q(1, 2)    # Create a field element: one over two
    y = Q(2)       # Another field element: two, which is two over one
    z = x*y        # z is two over two; no canceling takes place
    z == Q(4, 4)   # This true because 4*2 == 2*4
    type(z) is Q   # This is also true
    @endcode

    A formal quotient is an equivalence class of pairs (numerator, denominator)
    whose entries come from an integral domain (a commutative ring with
    identity and no zero divisors). Two pairs @f$ \frac{u}{v} @f$ and
    @f$ \frac{s}{t} @f$ are considered equivalent if, and only if, @f$ u\cdot t
    = s\cdot v @f$. Observe that this comparison uses multiplication only;
    since the elements come from a ring and might have no multiplicative
    inverses, division does not work.
    
    @note  A consequence of omitted canceling is that the elements might grow
           large.
    
    @note  The class uses the operand_casting() decorator: @c other operands in
           binary operations will first be treated as FractionField elements.
           If that fails, the operation will be repeated after @p other was fed
           to the constructor __init__().  If that fails, too, then the
           operation returns @c NotImplemented (so that @p other.__rop__()
           might be invoked).
    
    @see   For example, Robinson, Derek J. S.,
           "An Introduction to Abstract Algebra", p. 113.
    """    
    def __init__(self, numerator, denominator=None):
        """
        Construct a new formal quotient (@p numerator, @p denominator).
        
        If the @p numerator is an element of this FractionField class, then
        the new element is a copy of @p numerator; @p denominator is ignored.
        Otherwise, a @c None denominator (the default) is interpreted as the
        multiplicative neutral element (one) in the underlying integral domain.
        
        @exception     ZeroDivisonError    if the denominator is zero (and not
                                           @c None, see above).
        """
        if isinstance(numerator, self.__class__):
            # Copy an instance
            self.__numerator = numerator.__numerator
            self.__denominator = numerator.__denominator
        
        else:
            if denominator is None:
                denominator = self._integral_domain.one()
            if not denominator:
                raise ZeroDivisionError
            self.__numerator = self._integral_domain( numerator )
            self.__denominator = self._integral_domain( denominator )


    def __bool__(self):
        """
        Test whether the formal quotient is non-zero: return @c True if, and
        only if, the numerator is non-zero. Return @c False if the numerator
        is zero.
        
        Implicit conversions to boolean (truth) values use this method, for
        example when @c x is an element of a FractionField:
        @code
        if x:
            do_something()
        @endcode
        """
        return bool( self.__numerator )
    

    def __eq__(self, other):
        """
        Test whether another formal quotient @p other is equivalent to @p self;
        return @c True if that is the case.  The infix operator @c == calls
        this method.
        
        Two fractions @f$ \frac{u}{v} @f$ and @f$ \frac{s}{t} @f$ are equivalent
        if, and only if, @f$ u\cdot t = s\cdot v @f$. 
        
        @note  Comparison may be expensive: it requires two multiplications in
               the underlying integral domain.
        """
        # Use the basic definition of equivalence for comparison.
        return self.__numerator * other.__denominator \
                == other.__numerator * self.__denominator
    

    def __add__(self, other):
        """
        Return the sum of @p self and @p other. The infix operator @c + calls
        this method.
        
        As usual, the sum of two fractions @f$ \frac{u}{v} @f$ and
        @f$ \frac{s}{t} @f$ is @f$ \frac{ u\cdot t + s\cdot v }{ v\cdot t } @f$.
        
        @note  Canceling of common factors is impossible, for the underlying
               integral domain contains non-units. Therefore, repeated addition
               results in large elements.
        """
        numerator = self.__numerator * other.__denominator \
                    + self.__denominator * other.__numerator
        denominator = self.__denominator * other.__denominator
        return self.__class__( numerator, denominator )


    def __neg__(self):
        """
        Return the additive inverse of @p self, which is @f$ \frac{-u}{v} @f$
        for a fraction @f$ \frac{u}{v} @f$. The negation operator @c -x
        (unary minus) calls this method.
        """
        return self.__class__(
                    -self.__numerator,
                    self.__denominator
                )
    

    def __mul__(self, other):
        """
        Return the product of @p self and @p other. The @c * infix operator
        calls this method.
        
        As usual, the product of two fractions @f$ \frac{u}{v} @f$ and
        @f$ \frac{s}{t} @f$ is @f$ \frac{ u\cdot s }{ v\cdot t } @f$.
        
        @note  Canceling of common factors is impossible, for the underlying
               integral domain contains non-units. Therefore, repeated
               multiplication results in large elements.
        """
        numerator = self.__numerator * other.__numerator
        denominator = self.__denominator * other.__denominator
        return self.__class__( numerator, denominator )
    

    def multiplicative_inverse(self):
        """
        Return the multiplicative inverse of @p self, which is
        @f$ \frac{v}{u} @f$ for a fraction @f$ \frac{u}{v} @f$.
        
        @exception ZeroDivisionError   if @p self is zero (has a zero numerator)
        
        @see   __bool__()
        """
        if not self:
            raise ZeroDivisionError
        
        return self.__class__(
                    self.__denominator,
                    self.__numerator
                )
    

    @classmethod
    def zero(cls):
        """
        Return the field's neutral element of addition (zero).
        
        Zero in a FractionField is a fraction @f$ \frac{0}{1} @f$, where
        @f$ 0 @f$ and @f$ 1 @f$ denote the zero and one of the underlying
        integral domain.
        """
        return cls( cls._integral_domain.zero(), cls._integral_domain.one() )

    
    @classmethod
    def one(cls):
        """
        Return the field's neutral element of multiplication (one).
        
        One (or unity) in a FractionField is a fraction @f$ \frac{1}{1} @f$,
        where @f$ 1 @f$ denotes the one of the underlying integral domain.
        """
        return cls( cls._integral_domain.one(), cls._integral_domain.one() )
