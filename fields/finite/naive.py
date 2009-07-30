# -*- coding: utf-8 -*-
# $Id$

from rings.quotients.naive import QuotientRing
from rings.integers.naive import IntegerRing

class FiniteField(QuotientRing):
    """
    Finite field, naive implementation (currently limited to prime size).
    """
    def __init__(self, characteristic, power = 1):
        # TODO: Add assertions for primality and power
        self._characteristic = int( characteristic )
        self._power = int( power )
        
        if power > 1:
            # TODO: Use the ring polynomials modulo an irreducible polynomial  
            pass
        else:
            QuotientRing.__init__( self, IntegerRing(), characteristic )

    def characteristic(self):
        return self._characteristic

    def power(self):
        return self._power

    def __str__(self):
        if self._power > 1:
            count = "{0}^{1}".format( self._characteristic, self._power )
        else:
            count = str( self._characteristic )

        return """Finite field of {0} elements""".format( count ) 