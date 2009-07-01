# -*- coding: utf-8 -*-
# $Id$

class FiniteField:
    """
    Finite field (currently limited to prime size).
    
    This class is unnecessary, strictly speaking. Its only purpose at the
    moment is to make the algorithms more verbose.
    """
    
    def __init__(self, size):
        # TODO: Add assertion that size is a prime power
        # TODO: Calculate characteristic and use correct class for elements
        self.__size = int(size)
    
    def __call__(self, representative):
        # TODO: Choose correct representation (size is prime or prime power)
        return FinitePrimeFieldElement( representative, self.__size )
    
    def __str__(self):
        return """finite field of {0} elements""".format( self.__size )


class FinitePrimeFieldElement:
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

    def __hash__(self):
        # FIXME: Remove this? It is unnecessary for our purpose.
        # Use tuple form for hashing.
        return hash((self.__remainder, self.__modulus)) 

    def __eq__(self, other):
        return self.__remainder == other.__remainder \
            and self.__modulus == other.__modulus

    def __neq__(self, other):
        return not self == other

    def __neg__(self):
        return self.__class__( -self.__remainder, self.__modulus )

    def __add__(self, other):
        assert self.__modulus == other.__modulus, \
            "elements have different modulus"
        return self.__class__(
                      self.__remainder + other.__remainder,
                      self.__modulus
                  )
    
    def __sub__(self, other):
        assert self.__modulus == other.__modulus, \
            "elements have different modulus"
        return self.__class__(
                      self.__remainder - other.__remainder,
                      self.__modulus
                  )

    def __mul__(self, other):
        assert self.__modulus == other.__modulus, \
            "elements have different modulus"
        return self.__class__(
                      self.__remainder * other.__remainder,
                      self.__modulus
                  )

    def __truediv__(self, other):
        return self * other.inverse()

    def __pow__(self, other):
        # This only makes sense for integer arguments.
        return self.__class__(
                      pow(self.__remainder, int(other), self.__modulus),
                      self.__modulus
                  )

    def inverse(self):
        # Extended euclidean algorithm, see Knuth, D. E.
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
