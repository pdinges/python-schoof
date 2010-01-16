# -*- coding: utf-8 -*-
# $Id$

from rings import CommutativeRing

from support.types import template
from support.operators import operand_casting
from support.profiling import profiling_name, local_method_names

# FIXME: Having ring and modulus as parameters is redundant. Obviously we have
#        ring == modulus.__class__ 

@operand_casting
@local_method_names
@profiling_name( "{_ring}/{_modulus}" )
class QuotientRing( CommutativeRing, metaclass=template( "_ring", "_modulus" ) ):
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
    
    The implementation emphasizes simplicity and omits possible
    optimizations.
    """
    def __init__(self, representative):
        if isinstance( representative, self.__class__ ):
            self.__remainder = representative.__remainder
        elif isinstance( representative, self._modulus.__class__ ):
            self.__remainder = representative % self._modulus
        else:
            m = self._modulus
            self.__remainder = m.__class__( representative ) % m

    def remainder(self):
        return self.__remainder
    
    def __eq__(self, other):
        return self.__remainder == other.remainder()

    def __bool__(self):
        return bool( self.__remainder )

    def __add__(self, other):
        return self.__class__(
                        self.__remainder + other.remainder()
                    )
    
    def __neg__(self):
        return self.__class__( -self.__remainder )

    def __mul__(self, other):
        return self.__class__(
                        self.__remainder * other.remainder()
                    )

    # TODO: Add division operations that make sense.
    #       Otherwise, move inversion to field element class.
    def __truediv__(self, other):
        return self * other.multiplicative_inverse()
        
    def __rtruediv__(self, other):
        return other * self.multiplicative_inverse()
    
    def multiplicative_inverse(self):
        if not self.__remainder:
            raise ZeroDivisionError
        # Extended Euclidean algorithm, see Knuth, D. E.
        # "The Art of Computer Programming", volume 1, second edition, p.14
        # FIXME: Clean up this mess.
        # TODO: Add assertions required for this algorithm to work.
        annulating_scalar = self._ring.one()
        previous_scalar = self._ring.zero()
        
        c, d = self._modulus, self.__remainder
        
        quotient, remainder = divmod( c, d )
        
        # FIXME: Stop and raise an exception if element has no inverse.
        while remainder:
            c, d = d, remainder
            t, previous_scalar = previous_scalar, annulating_scalar
            
            annulating_scalar = t -  quotient * annulating_scalar
            
            quotient, remainder = divmod(c, d)

        return self.__class__( annulating_scalar )

    def __str__(self):
        return "[{r} mod {m}]".format(
                r = self.__remainder,
                m = self._modulus
            )


    @classmethod
    def modulus(cls):
        return cls._modulus

    @classmethod
    def ring(cls):
        return cls._ring
    
    @classmethod
    def zero(cls):
        return cls( cls._ring.zero() )
    
    @classmethod
    def one(cls):
        return cls( cls._ring.one() )
