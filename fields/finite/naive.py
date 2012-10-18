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
A naive implementation of finite fields.

@package   fields.finite.naive
@author    Peter Dinges <pdinges@acm.org>
"""

from rings.quotients.naive import QuotientRing
from rings.integers.naive import Integers
from support.profiling import profiling_name

@profiling_name("GF<{_modulus}>")
class FiniteField(QuotientRing, _ring=Integers):
    """
    The finite field with @f$ p^k @f$ elements; the field operations on the
    element instances support the natural infix syntax and allow mixing in
    integer arguments.
    
    This is a template class that must be instantiated with the field size.
    For example:
    @code
    # Instantiate the template; GF23 is a class.
    GF23 = FiniteField(23)
    x = GF23(3)    # Create a field element: x is the quotient class (3 mod 23)
    y = GF23(-2)   # Equivalently: y = GF23(21) because 21 == -2  (mod 23)
    z = x**2 + 2*y - x/y   # z == 15 (mod 23); note that -2*11 == 1 (mod 23)
    type(x) is GF23        # This is True
    @endcode
    
    The implementation is held as simple as possible. Its focus lies on ease
    of understanding, not on performance. Thus it is badly suited for larger
    computations. The template inherits from
    @c rings.quotients.naive.QuotientRing and specializes the @c _ring template
    parameter to @c rings.integers.naive.Integers 
    
    @note      The field size must be a prime. The template will, however,
               accept compound numbers without hesitation. In this case, the
               class behaves like the quotient ring
               @f$ \mathbb{Z}/n\mathbb{Z} @f$.
    
    @see       rings.quotients.naive.QuotientRing
    
    @author    Peter Dinges <pdinges@acm.org>
    """

    @classmethod
    def characteristic(cls):
        """
        Return the field characteristic @f$ p @f$.
        """
        return cls._modulus
    
    @classmethod
    def power(cls):
        """
        Return the power @f$ k @f$ of the characteristic that yields the field
        size: @f$ q = p^k @f$, where @f$ p @f$ is the field characteristic.
        
        @note  In the current implementation, @f$ k @f$ is always 1.
        """
        return 1
    
    @classmethod
    def size(cls):
        """
        Return the number of elements in the field.
        """
        return cls.characteristic() ** cls.power()

    @classmethod
    def elements(cls):
        """
        Return a list of all field elements in ascending order
        @f$ (0, 1, 2, ..., p-1) @f$ (mod p).
        
        @note  The method populates the complete list, so this operation might
               be expensive for large field characteristics.
        """
        return [ cls(i) for i in range(0, cls.size()) ]
