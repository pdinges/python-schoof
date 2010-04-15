# -*- coding: utf-8 -*-
# $Id$

from support.types import template
from support.profiling import profiling_name, local_method_names

@local_method_names
@profiling_name( "E<{_field}>" )
class EllipticCurve( metaclass=template("_field", "_A", "_B") ):
    """
    Point on an elliptic curve using cartesian coordinates as
    representation; supports additive notation for group operations.
    """
    def __init__(self, x, y):
        self.__x = self._field( x )
        self.__y = self._field( y )

        A, B = self.parameters()
        x, y = self.__x, self.__y
        assert y ** 2 == x ** 3  +  A * x  +  B, \
            "point ({x}, {y}) is not on the curve".format(x=x, y=y)
    
    def x(self):
        return self.__x
    
    def y(self):
        return self.__y
        
    def __eq__(self, other):
        if other.is_infinite():
            return False
        else:
            return self.__x == other.x() and self.__y == other.y()
    
    def __neq__(self, other):
        return not self == other
    
    def __neg__(self):
        return self.__class__(self.__x, -self.__y)
    
    def __add__(self, other):
        if other.is_infinite():
            return self
        elif self == -other:
            return PointAtInfinity()
        else:
            if self.__x == other.x():
                return self.__double__()
            else:
                return self.__generic_add__( other )
                
    def __generic_add__(self, other):
        gamma = (other.y() - self.__y) / (other.x() - self.__x)
        u = -self.__x - other.x() +  gamma ** 2
        v = -self.__y - gamma * (u - self.__x)
        
        return self.__class__(u, v)

    def __double__(self):
        A, B = self.parameters()
        delta = (3 * self.__x ** 2  + A) / (2 * self.__y)
        u = -self.__x - self.__x +  delta ** 2
        v = -self.__y - delta * (u - self.__x)
        
        return self.__class__(u, v)
    
    def __sub__(self, other):
        return self + (-other)
    
    def __mul__(self, n):
        """
        Multiplication with integers: adding the point n times to itself
        
        This method is used when self was the left factor.
        """
        n = int(n)
        if n == 0:
            return PointAtInfinity()
        
        point = self
        for i in range(1, n):
            point += self
        
        return point
    
    def __rmul__(self, other):
        """Multiplication with integers where self is the right factor"""
        # Multiplication with integers is always commutative.
        return self * other
    
    def is_infinite(self):
        return False
    
    def __str__(self):
        return "({x}, {y})".format( x = self.__x, y = self.__y )
    
    @classmethod
    def field(cls):
        return cls._field
    
    @classmethod
    def parameters(cls):
        return (cls._A, cls._B)
    
    @classmethod
    def is_singular(cls):
        # A curve is singular if and only if its determinant is 0
        # (in fields of characteristic neither 2 nor 3).
        return not 4 * cls._A**3  + 27 * cls._B ** 2

#    TODO: Move class description to metaclass
#    def __str__(self):
#        msg = "elliptic curve with parameters A='{A}' and B='{B}' over {F}"
#        return msg.format( A = self.__A, B = self.__B, F = self.__field )


# TODO: Make this a singleton
class PointAtInfinity:
    """
    Point at infinity on an elliptic curve, that is, the neutral element
    of the abelian group of points
    
    Note that this implementation is independent of the representation
    used for finite points.
    """
    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other
    
    def __sub__(self, other):
        return -other

    def __rsub__(self, other):
        return other
    
    def __mul__(self, other):
        if isinstance(other, int):
            return self
        else:
            return NotImplemented
    
    def __rmul__(self, other):
        if isinstance(other, int):
            return self
        else:
            return NotImplemented
    
    def __neg__(self):
        return self
    
    def __eq__(self, other):
        return other.is_infinite()

    def __neq__(self, other):
        return not other.is_infinite()
    
    def is_infinite(self):
        return True
    
    def __str__(self):
        return "(infinity)"
