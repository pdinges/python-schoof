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
Auxiliary functions for computations related to prime numbers.

The algorithms and implementations are kept as simple as possible. They are
not meant for high performance computing, but for instructive purposes.

@package   support.primes
@author    Peter Dinges <pdinges@acm.org>
"""

from math import ceil, sqrt

def primes_range(lower_bound, upper_bound):
    """
    Return a list of all primes in the range [@p lower_bound, @p upper_bound).
    
    @note      The function returns an actual list, not a proper range object.
               Furthermore, it computes the complete list of primes up to
               @p upper_bound on each call. These characteristics make it badly
               suited for anything involving large ranges or large primes.

    @param     lower_bound     The minimum size for returned primes; typically
                               this is an integer, but any number object with
                               an integer interpretation works. 
    @param     upper_bound     The strict upper bound for returned primes: all
                               returned primes are strictly less than this
                               number.
    """
    # The sieve of Eratosthenes
    primes = set( range(2, upper_bound) )
    sieve_bound = ceil( sqrt(upper_bound) )
    for i in range(2, sieve_bound):
        if i in primes:
            multiples = [ i*j for j in range(2, ceil(upper_bound / i)) ]
            primes -= set(multiples)
    return sorted(list( primes - set(range(2, lower_bound)) ))


def inverse_primorial(n, shunned = 0):
    """
    Return the smallest prime @c p such that the product of all primes
    up to @c p (inclusive) is at least @p n. For example,
    @c inverse_primorial(30) is 5, and @c inverse_primorial(31) is 7. 
    
    @note      This function uses primes_range() to obtain a list of primes.
               See the notes there for use case limitations.

    @param     n   The number object that the product must exceed in size.
                   The object must have an integer interpretation.
    
    @return    The prime @c p such that the product of all primes up to @c p
               (inclusive) is at least @p n; if @p n is too small (less than 2)
               the result is 2.
    """
    product = 1
    # A much smaller upper bound should suffice; however, we play it safe.
    for prime in primes_range(2, int(n)+1):
        if prime != shunned:
            product *= prime
            if product >= n:
                return prime
    # Return the smallest prime if n is too small
    return 2
