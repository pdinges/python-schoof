# -*- coding: utf-8 -*-
# $Id$

from math import ceil, sqrt

def primes_range(lower_bound, upper_bound):
    # The sieve of Eratosthenes
    primes = set( range(2, upper_bound) )
    sieve_bound = ceil( sqrt(upper_bound) )
    for i in range(2, sieve_bound):
        if i in primes:
            multiples = [ i*j for j in range(2, ceil(upper_bound / i)) ]
            primes -= set(multiples)
    return sorted(list( primes - set(range(2, lower_bound)) ))
