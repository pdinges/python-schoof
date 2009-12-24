# -*- coding: utf-8 -*-
# $Id$

from rings.polynomials.naive import PolynomialRing

class CurvePolynomialRing:
    # Just some bivariate polynomials on the curve. The reduction is
    # an implementation detail.
    def __init__(self, elliptic_curve):
        self.__curve = elliptic_curve
        self.__polynomial_ring = PolynomialRing( elliptic_curve.field() )
        
        # Use y**2 = x**3 + A*x + B to eliminate any y-power greater than 1.
        A, B = elliptic_curve.parameters()
        self.__y2_reduction = self.__polynomial_ring(B, A, 0, 1)
        
    def y2_reduction(self):
        return self.__y2_reduction
    
    def indeterminates(self):
        R = self.__polynomial_ring
        x = self( R.indeterminate(), R.zero() )
        y = self( R.zero(), R.one() )   # Second argument is the factor of y(!)
        return x, y
    
    def __eq__(self, other):
        return self is other or (  \
                isinstance(other, self.__class__)  \
                and self.__curve == other.__curve  \
            )
    
    def __call__(self, element_description, y_factor = None):
        if isinstance(element_description, ReducedPolynomial)  \
            and element_description.source_ring() == self:
                return element_description
        
        else:
            if y_factor is None:
                y_factor = self.__polynomial_ring.zero()
            return ReducedPolynomial(
                        self,
                        self.__polynomial_ring( element_description ),
                        self.__polynomial_ring( y_factor )
                    )

    def one(self):
        R = self.__polynomial_ring
        return self( R.one(), R.zero() )

    def zero(self):
        R = self.__polynomial_ring
        return self( R.zero(), R.zero() )
    

import rings

class ReducedPolynomial(rings.DefaultImplementationElement):
    """
    Polynomials on an elliptic curve that automatically reduce powers of y.
    
    Not the most general solution, but probably the easiest to understand.
    Idea similar to Charlap and Robbins: not multivariate quotient ring,
    just reduction.
    """
    def __init__(self, reduced_polynomial_ring, x_factor, y_factor):
        self.__source_ring = reduced_polynomial_ring
        self.__x_factor = x_factor  # polynomial in x only
        self.__y_factor = y_factor  # y * polynomial in x

    def source_ring(self):
        return self.__source_ring
    
    def x_factor(self):
        return self.__x_factor
    
    def y_factor(self):
        return self.__y_factor
    
    def __eq__(self, other):
        try:
            # Ensure that the second operand is a reduced polynomial 
            other = self.__source_ring(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__eq__() instead.
            return NotImplemented

        return self.__x_factor == other.__x_factor \
                and self.__y_factor == other.__y_factor 


    def __add__(self, other):
        try:
            # Ensure that the second operand is a reduced polynomial 
            other = self.__source_ring(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__radd__() instead.
            return NotImplemented

        x = self.__x_factor + other.__x_factor
        y = self.__y_factor + other.__y_factor
        return self.__class__( self.__source_ring, x, y )
        

    def __neg__(self):
        return self.__class__(
                    self.__source_ring,
                    -self.__x_factor,
                    -self.__y_factor
                )
    
    
    def __mul__(self, other):
        try:
            # Ensure that the second operand is a reduced polynomial 
            other = self.__source_ring(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__rmul__() instead.
            return NotImplemented

        x = self.__x_factor * other.__x_factor
        xy = self.__x_factor * other.__y_factor
        yx = self.__y_factor * other.__x_factor
        y = xy + yx
        
        # Reduce y**2 to y2_reduction
        if self.__y_factor and other.__y_factor:
            #y = self.__y_factor - self.__y_factor # Zero of unknown type
            x += self.__y_factor * other.__y_factor * self.__source_ring.y2_reduction()

        return self.__class__( self.__source_ring, x, y )


    def __divmod__(self, other):
        if not other:
            raise ZeroDivisionError
        
        try:
            # Ensure that the second operand is a reduced polynomial 
            other = self.__source_ring(other)
        except TypeError:
            # This class does not know how to handle the second operand;
            # try other.__rdivmod__() instead.
            return NotImplemented

        if not self:
            return self.__source_ring.zero()
        
        if other.__y_factor and (self.__x_factor or other.__x_factor):
            # Ok, this is cheating. Multivariate polynomial division is,
            # however, quite complicated and unnecessary for our purpose.
            raise ValueError("multivariate division is unsupported")
        
        if other.__x_factor:
            qx, rx = divmod( self.__x_factor, other.__x_factor )
            qy, ry = divmod( self.__y_factor, other.__x_factor )
        else:
            # Case: self and other have only y factors
            qx, rx = divmod( self.__y_factor, other.__y_factor )
            zero = self.__source_ring.zero().x_factor()
            qy, ry = zero, zero
            # s(x) / (y * t(x))  =
            #      = (y**2 * s(x)) / (y * t(x) * [y**2-reduction to x])
            #qy, ry = divmod( self.__x_factor, other.__y_factor * self.__source_ring.y2_reduction() )
        
        quotient = self.__class__( self.__source_ring, qx, qy )
        remainder = self.__class__( self.__source_ring, rx, ry )
        
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

