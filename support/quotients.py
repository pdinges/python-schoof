# -*- coding: utf-8 -*-
# $Id$

def representative_in_range( quotient_class, valid_range ):
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

from fields.finite.naive import FiniteField

def solve_congruence_equations( congruences ):
    # The Chinese remainder theorem
    # TODO: Assert relatively prime moduli
    common_modulus = product( [ c.modulus() for c in congruences ] )
    common_representative = 0
    for c in congruences:
        neutralizer = common_modulus // c.modulus()
        common_representative += c.remainder() * neutralizer  \
                                    * inverse_modulo( neutralizer, c.modulus() )
    
    # FIXME: This is not a field! Use QuotientRing.
    field = FiniteField( common_modulus )
    return field( common_representative )


def product(iterable):
    product = 1
    for item in iterable:
        product *= item
    return product


def inverse_modulo(representative, modulus):
    # Extended Euclidean algorithm
    b, bp = 1, 0
    c = modulus
    d = representative
    q, r = divmod(c, d)
    while r != 0:
        c, d = d, r
        t = bp
        bp = b
        b = t - q*b
        
        q, r = divmod(c, d)    
    return b
