# -*- coding: utf-8 -*-
# $Id$

from rings.quotients.naive import QuotientRing
from rings.integers.naive import Integers
from support.profiling import profiling_name

@profiling_name("GF<{_modulus}>")
class FiniteField(QuotientRing, _ring=Integers):
    """
    Finite field, naive implementation (currently limited to prime size).
    """
    @classmethod
    def __iter__(cls):
        # FIXME: Does not work for the class object, only for instances.
        return elements(cls)

    @classmethod
    def characteristic(cls):
        return cls._modulus
    
    @classmethod
    def power(cls):
        return 1
    
    @classmethod
    def size(cls):
        return cls.characteristic() ** cls.power()

#    TODO: Make this a class description method.
#    def __str__(self):
#        if self._power > 1:
#            count = "{0}^{1}".format( self.characteristic(), self.power() )
#        else:
#            count = str( self.characteristic() )
#
#        return """Finite field of {0} elements""".format( count ) 

    @classmethod
    def elements(cls):
        return [ cls(i) for i in range(0, cls.size()) ]


def elements(field):
    for i in range( 0, field.size() ):
        yield field(i)
