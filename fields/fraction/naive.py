# -*- coding: utf-8 -*-
# $Id$

from fields.fraction import FractionField as SuperField

class FractionField(SuperField):
    def __call__(self, numerator, denominator):
        # TODO: Conversion of numerator and denominator? Assert elements of
        # integral domain?
        return FormalQuotientElement(numerator, denominator)
    
    
from fields import DefaultImplementationElement

class FormalQuotientElement(DefaultImplementationElement):
    """
    Element from a field of formal quotients, that is, a congruence class
    of pairs (numerator, denominator) over an integral domain.
    
    Formal quotient means that equality will be checked by multiplication
    only; common factors will NOT be canceled out.
    """
    def __init__(self, numerator, denominator):
        self.__numerator = numerator
        self.__denominator = denominator
        
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
        return self.__class__( -self.__numerator, self.__denominator )
    
    def __mul__(self, other):
        numerator = self.__numerator * other.__numerator
        denominator = self.__denominator * other.__denominator
        return self.__class__( numerator, denominator )
    
    def multiplicative_inverse(self):
        return self.__class__( self.__denominator, self.__numerator )
    
    def __str__(self):
        return "({0:s} / {1:s})".format(
                    self.__numerator,
                    self.__denominator
                )
