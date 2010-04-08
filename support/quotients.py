# -*- coding: utf-8 -*-
# $Id$

"""
Auxiliary functions to handle congruences and quotient classes.

The algorithms and implementations are kept as simple as possible. They are
not meant for high performance computing, but for instructive purposes.

@package   support.quotients
@author    Peter Dinges <me@elwedgo.de>
"""

def representative_in_range( quotient_class, valid_range ):
    """
    Return the unique representative of @p quotient_class in @p valid_range.
    
    @param     quotient_class  A QuotientClass over the Integers.
    @param     valid_range     The range() object describing the interval in
                               which to the returned representative must lie. 
    
    @raise     ValueError      either if there is no representative in
                               @p valid_range, or if there are multiple.
    """
    if len(valid_range) > quotient_class.modulus():
        raise ValueError("solution not unique")
    
    # range[0] is the first element, that is, the lower bound
    q, r = divmod( valid_range[0], quotient_class.modulus() )
    shifted_range = range(r, r + len(valid_range))
    
    if quotient_class.remainder() in shifted_range:
        return q * quotient_class.modulus()  + quotient_class.remainder()
    elif quotient_class.remainder() + quotient_class.modulus() in shifted_range:
        return (q+1) * quotient_class.modulus()  + quotient_class.remainder()
    else:
        # FIXME: Really use exceptions?
        raise ValueError("no solution")


#------------------------------------------------------------------------------ 

from functools import reduce
from operator import mul

from rings.integers.naive import Integers
from rings.quotients.naive import QuotientRing

from support.rings import gcd

def solve_congruence_equations( congruences ):
    """
    Return a quotient class that simultaneously solves the list of
    @p congruences; this is the Chinese Remainder Theorem.
    
    All representatives of the returned congruence have the remainders of
    @p congruences when taken modulo the respective moduli. The result is a
    congruence modulo the product of all moduli. Thus the function returns a
    number @f$ z \mod \prod_{i} m_i @f$ such that
    @f{align*}{
     z &\equiv a_1 \mod m_1 \\
     \vdots \\
     z &\equiv a_k \mod m_k
    @f}
    
    @note The moduli @f$ m_i @f$ of all congruences must be relatively prime.
    
    @param     congruences     An iterable of objects of QuotientClass over the
                               Integers. Every pair of two different moduli
                               must have a greatest common divisor (gcd()) of 1.
    
    @return    A QuotientClass over the Integers solving the @p congruences.
    """
    # The Chinese remainder theorem
    if __debug__:
        # This test is expensive; remove it in optimized execution
        pairs = [ (c1, c2) for c1 in congruences for c2 in congruences if c1 != c2 ]
        pairwise_gcds = [ gcd( c1.modulus(), c2.modulus() ) for c1, c2 in pairs ]
    
        assert set( pairwise_gcds ) == set([ 1 ]), \
            "the Chinese Remainder Theorem requires relatively prime moduli"
    
    common_modulus = reduce( mul, [ c.modulus() for c in congruences ] )
    common_representative = 0
    for c in congruences:
        neutralizer = common_modulus // c.modulus()
        common_representative += c.remainder() * neutralizer  \
                                    * inverse_modulo( neutralizer, c.modulus() )
    
    quotient_ring = QuotientRing( Integers, common_modulus )
    return quotient_ring( common_representative )


from support.rings import extended_euclidean_algorithm

def inverse_modulo(representative, modulus):
    """
    Return an element @c n such that @c n * representative has remainder one
    if divided by @p modulus.
    
    In residue class rings, this is the multiplicative inverse.
    """ 
    return extended_euclidean_algorithm( representative, modulus )[0]
