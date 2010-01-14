# -*- coding: utf-8 -*-
# $Id$

from fields import Field

from support.types import template
from support.operators import cast_operands
from support.profiling import profiling_name, prefix_operations

@cast_operands
@prefix_operations
@profiling_name( "Q<{_integral_domain}>" )
class FractionField( Field, metaclass=template("_integral_domain") ):
    # It is sufficient if the elements come from an integral domain
    # (a commutative ring with identity and no zero divisors).
    # For example, see Robinson, Derek J. S., "Abstract Algebra", p. 113.
    """
    Element from a field of formal quotients, that is, a congruence class
    of pairs (numerator, denominator) over an integral domain.
    
    Formal quotient means that equality will be checked by multiplication
    only; common factors will NOT be canceled out.
    """    
    def __init__(self, numerator, denominator=None):
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
        return bool( self.__numerator )
    

    def __eq__(self, other):
        # Use the basic definition of equivalence for comparison.
        return self.__numerator * other.__denominator \
                == other.__numerator * self.__denominator
    

    def __add__(self, other):
        numerator = self.__numerator * other.__denominator \
                    + self.__denominator * other.__numerator
        denominator = self.__denominator * other.__denominator
        return self.__class__( numerator, denominator )


    def __neg__(self):
        return self.__class__(
                    -self.__numerator,
                    self.__denominator
                )
    

    def __mul__(self, other):
        numerator = self.__numerator * other.__numerator
        denominator = self.__denominator * other.__denominator
        return self.__class__( numerator, denominator )
    

    def multiplicative_inverse(self):
        if not self:
            raise ZeroDivisionError
        
        return self.__class__(
                    self.__denominator,
                    self.__numerator
                )
    

    def __str__(self):
        if self.__denominator == self._integral_domain.one():
            return str( self.__numerator )
        else:
            return """({n} / {d})""".format(
                        n = self.__numerator,
                        d = self.__denominator
                    )


    @classmethod
    def zero(cls):
        return cls( cls._integral_domain.zero(), cls._integral_domain.one() )

    
    @classmethod
    def one(cls):
        return cls( cls._integral_domain.one(), cls._integral_domain.one() )
