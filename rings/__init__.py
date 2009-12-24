# -*- coding: utf-8 -*-
# $Id$

class DefaultCommutativeElement:
    """
    Base class for elements from a commutative ring; it provides default
    operator overloading.
    
    For example, subtraction is defined as addition of the additive inverse.
    Derived classes therefore only have to implement these operations if a
    shortcut is available.
    """
    # TODO: Raise NotImplementedError on required operations?
    
    def __neq__(self, other):
        return not self.__eq__( other )
    
    def __radd__(self, other):
        # Additive subgroup is commutative:
        # other + self == self + other
        return self.__add__( other )
    
    def __sub__(self, other):
        return self.__add__( -other )
    
    def __rsub__(self, other):
        # Additive subgroup is commutative:
        # other - self == -( self - other )
        return -self.__sub__( other )
    
    def __rmul__(self, other):
        # Commutative ring:
        # other * self == self * other
        return self.__mul__( other )

    def __rdivmod__(self, other):
        # TODO: Factor casting into a single function. 
        return divmod( self.source_ring()( other ), self )
    
    def __rfloordiv__(self, other):
        return divmod( other, self )[0]
    
    def __rmod__(self, other):
        return divmod( other, self )[1]
    
    def __pow__(self, other):
        # This only makes sense for integer arguments.
        result = self
        for i in range(1, int(other)):
            result = result * self
        
        return result
