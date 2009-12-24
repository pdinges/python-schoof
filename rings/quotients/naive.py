# -*- coding: utf-8 -*-
# $Id$

class QuotientRing:
    def __init__(self, ring, modulus):
        self._ring = ring
        self._modulus = modulus
    
    def __eq__(self, other):
        return self is other or ( \
                isinstance(other, self.__class__)  \
                and self._ring == other._ring  \
                and self._modulus == other._modulus  \
            )
    
    def __call__(self, element_description):
        if isinstance(element_description, GenericQuotientClass)  \
            and element_description.source_ring() == self:
                return element_description
        
        return GenericQuotientClass( self, self._ring( element_description ) )

    def modulus(self):
        return self._modulus
    
    def ring(self):
        # TODO: Rename to representative_ring or something
        return self._ring
    
    def zero(self):
        return GenericQuotientClass( self, self._ring.zero() )
        
    def one(self):
        return GenericQuotientClass( self, self._ring.one() )
    

from rings import DefaultImplementationElement

class GenericQuotientClass(DefaultImplementationElement):
    """
    Element from a quotient ring, that is, a congruence class modulo
    a ring element. It uses the canonical mapping to implement the
    arithmetic operations in terms of the source ring operations.
    
    Elements of the source ring must provide the following operations:
      - equality (__eq__)
      - test for zero (__nonzero__)
      - addition (__add__)
      - negation (__neg__)
      - multiplication (__mul__)
      - the division algorithm (__divmod__) 
    
    The implementation emphasizes simplicity and omits all possible
    """
    def __init__(self, quotient_ring, representative):
        self.__source_ring = quotient_ring
        self.__remainder = representative % self.__source_ring.modulus()

    def source_ring(self):
        return self.__source_ring

    def remainder(self):
        return self.__remainder
    
    def modulus(self):
        return self.__source_ring.modulus()

    def __eq__(self, other):
        try:
            # Ensure that the second operand is a quotient class 
            other = self.__source_ring(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__eq__() instead.
            return NotImplemented

        return self.__remainder == other.__remainder

    def __bool__(self):
        return bool( self.__remainder )

    def __add__(self, other):
#        try:
#            if self.__source_ring == other.__source_ring:
#                return self.__class__(
#                                self.__source_ring,
#                                self.__remainder + other.__remainder
#                            )
#        except AttributeError:
#            return self + self.__source_ring( other )
#        
#        
        try:
            # Ensure that the second operand is a quotient class
            other = self.__source_ring(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__radd__() instead.
            return NotImplemented

        return self.__class__(
                      self.__source_ring,
                      self.__remainder + other.__remainder
                  )
    
    def __neg__(self):
        return self.__class__( self.__source_ring, -self.__remainder )

    def __mul__(self, other):
        try:
            # Ensure that the second operand is a quotient class 
            other = self.__source_ring(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__rmul__() instead.
            return NotImplemented

        return self.__class__(
                      self.__source_ring,
                      self.__remainder * other.__remainder
                  )

    def __truediv__(self, other):
        return self * other.multiplicative_inverse()
    
    
    def multiplicative_inverse(self):
        if not self.__remainder:
            raise ZeroDivisionError
        # Extended Euclidean algorithm, see Knuth, D. E.
        # "The Art of Computer Programming", volume 1, second edition, p.14
        # FIXME: Clean up this mess.
        # TODO: Add assertions required for this algorithm to work.
        annulating_scalar = self.__source_ring.ring().one()
        previous_scalar = self.__source_ring.ring().zero()
        
        c, d = self.__source_ring.modulus(), self.__remainder
        
        quotient, remainder = divmod( c, d )
        
        # FIXME: Stop and raise an exception if element has no inverse.
        while remainder:
            c, d = d, remainder
            t, previous_scalar = previous_scalar, annulating_scalar
            
            annulating_scalar = t -  quotient * annulating_scalar
            
            quotient, remainder = divmod(c, d)

        return self.__class__( self.__source_ring, annulating_scalar )


    def __str__(self):
        return "[{r} mod {m}]".format(
                r = self.__remainder,
                m = self.__source_ring.modulus()
            )
