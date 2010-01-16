# -*- coding: utf-8 -*-
# $Id$

from rings import CommutativeRing
from rings.polynomials.naive import Polynomials

from support.types import template
from support.operators import operand_casting
from support.profiling import profiling_name, local_method_names

@operand_casting
@local_method_names
@profiling_name( "{_elliptic_curve}[x,y]" )
class CurvePolynomials( CommutativeRing, metaclass=template("_elliptic_curve") ):
    # Just some bivariate polynomials on the curve. The reduction is
    # an implementation detail.
    """
    Bivariate polynomials on the curve.
    
    This implementation automatically reduces the polynomial y^2
    to the polynomial x^3 + A*x + B. It is not the most general solution, 
    but probably the easiest to understand.  Idea similar to
    Charlap and Robbins: not multivariate quotient ring, just reduction.
    """
    def __init__(self, x_factor, y_factor=None):
        # x_factor: polynomial in x only
        # y_factor: polynomial in x [implicitly * y]
        if isinstance(x_factor, self.__class__):
            # Casting an object that already has this type means copying it.
            self.__x_factor = x_factor.__x_factor
            self.__y_factor = x_factor.__y_factor
        else:
            self.__x_factor = self.polynomial_ring()( x_factor )
            if y_factor is None:
                self.__y_factor = self.polynomial_ring().zero()
            else:
                self.__y_factor = self.polynomial_ring()( y_factor )

    def x_factor(self):
        return self.__x_factor
    
    def y_factor(self):
        return self.__y_factor
    
    def __eq__(self, other):
        return self.__x_factor == other.x_factor() \
                and self.__y_factor == other.y_factor() 

    def __add__(self, other):
        x = self.__x_factor + other.x_factor()
        y = self.__y_factor + other.y_factor()
        return self.__class__( x, y )

    def __neg__(self):
        return self.__class__(
                    -self.__x_factor,
                    -self.__y_factor
                )
    
    def __mul__(self, other):
        x = self.__x_factor * other.x_factor()
        xy = self.__x_factor * other.y_factor()
        yx = self.__y_factor * other.x_factor()
        y = xy + yx

        # Reduce y**2 to y2_reduction
        if self.__y_factor and other.y_factor():
            #y = self.__y_factor - self.__y_factor # Zero of unknown type
            x += self.__y_factor * other.y_factor() * self.y2_reduction()

        return self.__class__( x, y )

    def __divmod__(self, other):
        if not other:
            raise ZeroDivisionError
        
        if not self:
            return self.polynomial_ring().zero(), self.polynomial_ring().zero()
        
        if other.y_factor() and (self.__x_factor or other.x_factor()):
            # Ok, this is cheating. Multivariate polynomial division is,
            # however, quite complicated and unnecessary for our purpose.
            raise ValueError("multivariate division is unsupported")
        
        if other.x_factor():
            qx, rx = divmod( self.__x_factor, other.x_factor() )
            qy, ry = divmod( self.__y_factor, other.x_factor() )
        else:
            # Case: self and other have only y factors
            qx, rx = divmod( self.__y_factor, other.y_factor() )
            zero = self.polynomial_ring().zero().x_factor()
            qy, ry = zero, zero
            # s(x) / (y * t(x))  =
            #      = (y**2 * s(x)) / (y * t(x) * [y**2-reduction to x])
            #qy, ry = divmod( self.__x_factor, other.__y_factor * self.__source_ring.y2_reduction() )
        
        quotient = self.__class__( qx, qy )
        remainder = self.__class__( rx, ry )
        
        return quotient, remainder

    def __floordiv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]

    def __str__(self):
        result = "y * {0}".format(self.__y_factor) if self.__y_factor else ""
        result += " + " if self.__x_factor and self.__y_factor else ""
        result += "{0}".format(self.__x_factor) if self.__x_factor else ""
        return result

    @classmethod
    def curve(cls):
        return cls._elliptic_curve

    @classmethod
    def y2_reduction(cls):
        try:
            return cls.__y2_reduction
        except AttributeError:
            # Use y**2 = x**3 + A*x + B to eliminate any y-power greater than 1.
            A, B = cls._elliptic_curve.parameters()
            cls.__y2_reduction = cls.polynomial_ring()( B, A, 0, 1 )
            return cls.__y2_reduction

    @classmethod
    def polynomial_ring(cls):
        try:
            return cls.__polynomial_ring
        except AttributeError:
            cls.__polynomial_ring = Polynomials( cls._elliptic_curve.field() )
            return cls.__polynomial_ring

    @classmethod
    def one(cls):
        R = cls.polynomial_ring()
        return cls( R.one(), R.zero() )

    @classmethod
    def zero(cls):
        R = cls.polynomial_ring()
        return cls( R.zero(), R.zero() )
