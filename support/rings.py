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
Auxiliary functions and algorithms for rings and their elements.

The algorithms and implementations are kept as simple as possible. They are
not meant for high performance computing, but for instructive purposes.

@package   support.rings
@author    Peter Dinges <pdinges@acm.org>
"""

def extended_euclidean_algorithm(u, v):
    """
    Return a tuple @c (m, n, d) such that @c u*m + v*n = d, where @c d is the
    greatest common divisor of @p u and @p v.
    
    The implementation does not enforce the use of integers for @p u and @p v.
    Thus, elements from other rings that support the @c divmod() operations as
    well as the operators @c //, @c * and @c - should work as well.

    @note      If @p u and @p v are Polynomials, then the returned gcd
               polynomial is not necessarily a monic polynomial; that means the
               gcd may have a leading coefficient other than one. To check
               whether two polynomials are relatively prime, test whether the
               result has degree() zero.
    
    @exception ZeroDivisionError   if one of @p u or @p v is zero.
    
    @see       Knuth, D. E., "The Art of Computer Programming",
               volume 2, second edition, p. 342  
    """
    if not (u and v):
        raise ZeroDivisionError( "cannot determine the gcd of zero" )
    
    # It does not matter which one is larger: if v > u, then the first shift
    # switches u and v.
    larger_remainder, lesser_remainder = u, v
    
    try:
        # u and v might not be integers after all, so ask for the right scalars
        larger_scalar, lesser_scalar = u.__class__.one(), u.__class__.zero()
    except AttributeError:
        larger_scalar, lesser_scalar = 1, 0
    
    while lesser_remainder:
        quotient, next_remainder = divmod( larger_remainder, lesser_remainder )
        next_scalar = larger_scalar - quotient * lesser_scalar 
        
        # Shift roles
        larger_remainder, larger_scalar = lesser_remainder, lesser_scalar
        lesser_remainder, lesser_scalar = next_remainder, next_scalar

    # larger_remainder is the gcd;
    # larger_scalar is the factor for the linear combination
    other_scalar = ( larger_remainder  -  u * larger_scalar ) // v
    return ( larger_scalar, other_scalar, larger_remainder )


def gcd(u, v):
    """
    Determine the greatest common divisor of @p u and @p v.
    
    @note      If @p u and @p v are Polynomials, then the returned polynomial
               is not necessarily monic; that means it may have a leading
               coefficient other than one. To check whether two polynomials are
               relatively prime, test whether the result has degree() zero.
    
    @see       extended_euclidean_algorithm() for a description of working
               input types.
    """
    return extended_euclidean_algorithm( u, v )[2]

