# -*- coding: utf-8 -*-
# $Id$

class FractionField:
    """
    Field of fractions over an integral domain, base class.
    """
    def __init__(self, integral_domain):
        # It is sufficient if the elements come from an integral domain
        # (a commutative ring with identity and no zero divisors).
        # For example, see Robinson, Derek J. S., "Abstract Algebra", p. 113.
        self._integral_domain = integral_domain
        
    def __call__(self, numerator, denominator):
        raise NotImplementedError
    
    def __str__(self):
        name = """Field of fractions over the {0}"""
        return name.format( self._integral_domain )
