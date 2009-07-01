# -*- coding: utf-8 -*-
# $Id$

class EllipticCurve:
    """
    Elliptic curve over a field of characteristic neither 2 nor 3
    """
    def __init__(self, field, A, B):
        # TODO: Add assertion about field characteristic
        self.__field = field
        self.__A = field(A)
        self.__B = field(B)

    def __call__(self, x, y):
        return CartesianPoint( self, self.__field(x), self.__field(y) )

    def field(self):
        return self.__field

    def parameters(self):
        return (self.__A, self.__B)
    
    def __str__(self):
        msg = "elliptic curve with parameters A={A} and B={B} over {F}"
        return msg.format( A = self.__A, B = self.__B, F = self.__field )


# FIXME: Should points inherit from an abstract base class?
#        That would make it complicated to mix in C++ classes.
# FIXME: How to call this class?
class CartesianPoint:
    """
    Point on an elliptic curve using cartesian coordinates as
    representation; supports additive notation for group operations 
    """
    def __init__(self, curve, x, y):
        # FIXME: Move this assertion to the elliptic curve class?
        A, B = curve.parameters()
        assert y ** 2 == x ** 3  +  A * x  +  B, \
            "point ({x}, {y}) is not on the curve".format(x=x, y=y)

        self.__curve = curve
        self.__x = x
        self.__y = y
        
        
    def __eq__(self, other):
        if other.is_infinite():
            return False
        else:
            return self.__x == other.__x and self.__y == other.__y
    
    def __neq__(self, other):
        return not self == other
    
    def __neg__(self):
        return self.__class__(self.__curve, self.__x, -self.__y)
        #return self.__curve(self.__x, -self.__y)
    
    def __add__(self, other):
        if other.is_infinite():
            return self
        elif self == -other:
            return PointAtInfinity()
        else:
            if self.__x == other.__x:
                A, B = self.__curve.parameters()
                F = self.__curve.field()
                l = (F(3) * self.__x ** 2  + A) / (F(2) * self.__y)
            else:
                l = (other.__y - self.__y) / (other.__x - self.__x)

            u = -self.__x - other.__x +  l ** 2
            v = -self.__y - l * (u - self.__x)
            
            return self.__class__(self.__curve, u, v)
    
    def __sub__(self, other):
        return self + (-other)
    
    def __mul__(self, n):
        """
        Multiplication with integers: adding the point n times to itself
        
        This method is used when self was the left factor.
        """
        if n == 0:
            return PointAtInfinity()
        
        point = self
        for i in range(1, int(n)):
            point += self 
        
        return point
    
    def __rmul__(self, other):
        """Multiplication with integers where self is the right factor"""
        return self * other
    
    def is_infinite(self):
        return False
    
    def __str__(self):
        return "({x}, {y})".format( x = self.__x, y = self.__y )


class PointAtInfinity:
    """
    Point at infinity on an elliptic curve, that is, the neutral element
    of the abelian group of points
    
    Note that this implementation is independent of the representation
    used for finite points.
    """
    def __add__(self, other):
        return other
    
    def __sub__(self, other):
        return -other
    
    def __mul__(self, other):
        return self
    
    def __rmul__(self, other):
        return self
    
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
