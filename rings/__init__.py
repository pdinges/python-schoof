# -*- coding: utf-8 -*-
# $Id$

class DefaultImplementationElement:
    """
    Base class for ring elements that provides default operator overloading.
    
    For example, subtraction is defined as addition of the additive inverse.
    Derived classes therefore only have to implement these operations if a
    shortcut is available.
    """
    # TODO: Raise NotImplementedError on required operations?
    
    def __neq__(self, other):
        return not self.__eq__( other )
    
    def __radd__(self, other):
        return self.__add__( other )
    
    def __sub__(self, other):
        return self.__add__( -other )
    
    def __rsub__(self, other):
        return -self.__sub__( other )
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __pow__(self, other):
        # This only makes sense for integer arguments.
        result = self
        for i in range(1, int(other)):
            result = result * self
        
        return result
