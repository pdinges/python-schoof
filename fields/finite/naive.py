# -*- coding: utf-8 -*-
# $Id$

from fields.finite import FiniteField as SuperField

class FiniteField(SuperField):
    """
    Finite field, naive implementation (currently limited to prime size).
    """
    def __call__(self, representative):
        # TODO: Choose correct representation (size is prime or prime power)
        return FinitePrimeFieldElement( representative, self._size )

    def zero(self):
        return self( 0 )
    
    def one(self):
        return self( 1 )


from fields import DefaultImplementationElement

class FinitePrimeFieldElement(DefaultImplementationElement):
    """
    Element from a finite field of prime size, that is, a congruence
    class modulo a prime. It provides the arithmetic operations in the field.
    
    The implementation emphasizes simplicity and omits all possible
    speedups for simplicity and ease of understanding.
    """
    # TODO: Create meta-class that ensures uniqueness of objects with
    #       identical remainder and modulus. (For non-naive version.)
    def __init__(self, representative, modulus):
        self.__modulus = int(modulus)
        # The '%' operator on integers returns a number in range(0, modulus).
        self.__remainder = int(representative) % self.__modulus

    def __eq__(self, other):
        return self.__remainder == other.__remainder \
            and self.__modulus == other.__modulus

    def __add__(self, other):
        assert self.__modulus == other.__modulus, \
            "elements have different modulus"
        return self.__class__(
                      self.__remainder + other.__remainder,
                      self.__modulus
                  )
    
    def __neg__(self):
        return self.__class__( -self.__remainder, self.__modulus )

    def __mul__(self, other):
        assert self.__modulus == other.__modulus, \
            "elements have different modulus"
        return self.__class__(
                      self.__remainder * other.__remainder,
                      self.__modulus
                  )

    def multiplicative_inverse(self):
        # Extended Euclidean algorithm, see Knuth, D. E.
        # "The Art of Computer Programming", volume 1, second edition, p.14
        # FIXME: Clean up this mess.
        ap, b = 1, 1
        a, bp = 0, 0
        c = self.__modulus
        d = self.__remainder
        q, r = divmod(c, d)
        
        while r != 0:
            c, d = d, r
            t = bp
            bp = b
            b = t - q*b
            
            q, r = divmod(c, d)

        return self.__class__(b, self.__modulus)

    def __str__(self):
        return "[{r} mod {m}]".format(
                r = self.__remainder,
                m = self.__modulus
            )
