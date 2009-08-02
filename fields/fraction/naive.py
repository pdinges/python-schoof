# -*- coding: utf-8 -*-
# $Id$

from fields.fraction import FractionField as SuperField

class FractionField(SuperField):
    def __call__(self, numerator, denominator=None):
        if isinstance(numerator, FormalQuotient)  \
            and numerator.source_field() == self:
                return numerator
        
        else:
            if not denominator:
                denominator = self._integral_domain.one()
            
            return FormalQuotient(
                        self,
                        self._integral_domain( numerator ),
                        self._integral_domain( denominator )
                    )
    
    def zero(self):
        return self( self._integral_domain.zero(), self._integral_domain.one() )
    
    def one(self):
        return self( self._integral_domain.one(), self._integral_domain.one() )
    
    
from fields import DefaultImplementationElement

class FormalQuotient(DefaultImplementationElement):
    """
    Element from a field of formal quotients, that is, a congruence class
    of pairs (numerator, denominator) over an integral domain.
    
    Formal quotient means that equality will be checked by multiplication
    only; common factors will NOT be canceled out.
    """
    def __init__(self, fraction_field, numerator, denominator):
        self.__source_field = fraction_field
        self.__numerator = numerator
        self.__denominator = denominator
    
    def source_field(self):
        return self.__source_field
    
    def __eq__(self, other):
        try:
            # Ensure that the second operand is a formal quotient 
            other = self.__source_field(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__eq__() instead.
            return NotImplemented

        # Use the basic definition of equivalence for comparison.
        return self.__numerator * other.__denominator \
                == other.__numerator * self.__denominator
    
    def __add__(self, other):
        try:
            # Ensure that the second operand is a formal quotient 
            other = self.__source_field(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__radd__() instead.
            return NotImplemented

        numerator = self.__numerator * other.__denominator \
                    + self.__denominator * other.__numerator
        denominator = self.__denominator * other.__denominator
        return self.__class__( self.__source_field, numerator, denominator )

    def __neg__(self):
        return self.__class__(
                    self.__source_field,
                    -self.__numerator,
                    self.__denominator
                )
    
    def __mul__(self, other):
        try:
            # Ensure that the second operand is a formal quotient 
            other = self.__source_field(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__rmul__() instead.
            return NotImplemented

        numerator = self.__numerator * other.__numerator
        denominator = self.__denominator * other.__denominator
        return self.__class__( self.__source_field, numerator, denominator )
    
    def multiplicative_inverse(self):
        return self.__class__(
                    self.__source_field,
                    self.__denominator,
                    self.__numerator
                )
    
    def __str__(self):
        if self.__denominator == self.__source_field.one():
            return str( self.__numerator )
        else:
            return """({n} / {d})""".format(
                        n = self.__numerator,
                        d = self.__denominator
                    )
