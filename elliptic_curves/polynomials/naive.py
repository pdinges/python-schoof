# -*- coding: utf-8 -*-
# Copyright (c) 2010--2012  Peter Dinges <pdinges@acm.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
A naive implementation of the ring of polynomials over an elliptic curve.

@package   elliptic_curves.polynomials.naive
@author    Peter Dinges <pdinges@acm.org>
"""

from rings import CommutativeRing
from rings.polynomials.naive import Polynomials

from support.types import template
from support.operators import operand_casting
from support.profiling import profiling_name, local_method_names

@operand_casting
@local_method_names
@profiling_name( "{_elliptic_curve}[x,y]" )
class CurvePolynomials( CommutativeRing, metaclass=template("_elliptic_curve") ):
    """
    A ring of polynomials over an elliptic curve; the polynomials support infix
    notation for ring operations, as well as mixed argument types.
    
    This is a template class that must be instantiated with the elliptic curve.
    Use it, for example, as follows:
    @code
    # Create the underlying elliptic curve
    E = elliptic_curves.naive.EllipticCurve( FiniteField(7), 3, 4 )
    # Instantiate the template; GF7E is a class (here: polynomials over E)
    GF7E = CurvePolynomials( E )

    # Use two coefficient lists as arguments; the polynomial is (list1) + y*(list2)
    s = GF7E( (4, 3, 0, 1) )  # The curve's defining polynomial
    y = GF7E( 0, (0, 1) )     # Another polynomial: y
    y**2 == s                 # The fundamental relation holds
    type(s) is GF7E           # This is also true

    # Use the polynomials 'x' and 'y' for a more natural syntax
    x = GF7( (0, 1), () )     # The empty tuple is just for emphasis
    y = GF7( (), (0, 1) )     # The empty tuple is just for emphasis
    y**2 == x**3 + 3**x + 4
    p = x**2 + 2* x + y*( 3 * x**5 + 6 * x**2 )  # A (pseudo) random polynomial
    @endcode
    
    The ring of polynomials over an elliptic curve @f$ E @f$ is
    @f$ \mathbb{F}[x,y]/(y^2 - x^3 - Ax - B) @f$, where @f$ \mathbb{F} @f$ is
    the field over which the curve was defined, and @f$ A, B @f$ are the curve
    parameters.  The quotient polynomial @f$ y^2 - x^3 - Ax - B @f$ expresses
    that the polynomial's domain is the set of points on @f$ E @f$; the
    (Cartesian) coordinates of the points @f$ (x, y) \in E @f$ are connected by
    the fundamental relation @f$ y^2 = x^3 + Ax + B @f$.
    
    @note  As a consequence of the fundamental relation, powers of @f$ y @f$
           greater than one can be reduced to a polynomial in  @f$ x @f$.  This
           is what this implementation does.  Since it does not provide full
           multivariate arithmetic, division (with remainder; see __divmod__())
           only works in the following cases:
           - The divisor is a polynomial in @f$ x @f$ alone; this works for all
             dividends.
           - Dividend and divisor are polynomials in @f$ y @f$ alone.
           
           Besides restricting arithmetic, the implementation emphasizes
           simplicity over speed; it omits possible optimizations.
    
    @note  The class uses the operand_casting() decorator: @c other operands in
           binary operations will first be treated as CurvePolynomial elements.
           If that fails, the operation will be repeated after @p other was fed
           to the constructor __init__().  If that fails, too, then the
           operation returns @c NotImplemented (so that @p other.__rop__()
           might be invoked).
    
    @see   Charlap, Leonard S. and Robbins, David P., "CRD Expositroy Report 31:
           An Elementary Introduction to Elliptic Curves", 1988, chapter 3
    """    

    #- Instance Methods ----------------------------------------------------------- 
    
    def __init__(self, x_factor, y_factor=None):
        """
        Create a new polynomial from the given coefficient lists @p x_factor
        and @p y_factor.
        
        Polynomials @f$ s @f$ over elliptic curves have a canonical form
        @f$ s(x, y) = a(x) + y\cdot b(x) @f$, where @f$ a, b @f$ are
        polynomials of @f$ x @f$ alone.  The parameter @p x_factor
        determines the coefficients of @f$ a @f$, @p y_factor determines the
        coefficients of @f$ b @f$.
        
        @param x_factor    An iterable that lists the coefficients of the
                           polynomial @f$ a @f$ in ascending order:
                           @p x_factor[0] is the constant,
                           @p x_factor[1] the linear, @p x_factor[2] the
                           quadratic coeffiecient; and so on.
        @param y_factor    Similar to @p x_factor, but for the polynomial
                           @f$ b @f$.
        
        For example, construct the polynomial @f$ x^3 + 4x - y\cdot(3x + 2) @f$
        as follows:
        @code
        # Suppose E is an is an EllipticCurve template specialization
        R = CurvePolynomials( E )
        p = R( (0, 4, 0, 1), (2, 3) )
        @endcode
        
        @note  Leading zeros in the coefficient lists will be ignored.
        """
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
        """
        Return the polynomial @f$ a @f$ from the canonical form
        @f$ s(x, y) = a(x) + y\cdot b(x) @f$ of @p self.
        
        @note  The returned polynomial is univariate.
        """
        return self.__x_factor
    
    
    def y_factor(self):
        """
        Return the polynomial @f$ b @f$ from the canonical form
        @f$ s(x, y) = a(x) + y\cdot b(x) @f$ of @p self.
        
        @note  The returned polynomial is univariate.
        """
        return self.__y_factor
    
    
    def leading_coefficient(self):
        """
        Return the leading coefficient, or zero if @p self is
        the zero polynomial.
        
        @note  The fundamental relation @f$ y^2 = x^3 + Ax + B @f$ forces the
               linear polynomials @f$ x @f$ and @f$ y @f$ to have different
               degrees.  Thus @f$ \deg(x) = 2 @f$ and @f$ \deg(y) = 3 @f$.
               The leading coefficient is the coefficient of the power with
               the highest degree; for @f$ x^4 + 2y^3 @f$ it is 2. (Ignore
               the reduction of @f$ y^2 @f$ for a moment.)
        """
        # Equality is impossible: we compare an odd and an even number.
        if (2 * self.__x_factor.degree()) > (3 + 2*self.__y_factor.degree()):
            return self.__x_factor.leading_coefficient()
        else:
            return self.__y_factor.leading_coefficient()
    
    
    def __bool__(self):
        """
        Test whether the polynomial is non-zero: return @c True if, and only
        if, at least one coefficient is non-zero. Return @c False if all
        coefficients are zero.
        
        Implicit conversions to boolean (truth) values use this method, for
        example when @c x is an element of Polynomials:
        @code
        if x:
            do_something()
        @endcode
        """
        return bool(self.__x_factor) or bool(self.__y_factor)
    
    
    def __eq__(self, other):
        """
        Test whether another polynomial @p other is equal to @p self; return
        @c True if that is the case.  The infix operator @c == calls
        this method.
        
        Two polynomials are equal if, and only if, all the coefficients of
        their canonical forms are equal. 
        """
        return self.__x_factor == other.x_factor() \
                and self.__y_factor == other.y_factor() 


    def __add__(self, other):
        """
        Return the sum of @p self and @p other. The infix operator @c + calls
        this method.
        
        Polynomials add coefficient-wise without carrying: the sum of two
        polynomials @f$ \sum_{k,l} a_{k,l}x^{k}y^{l} @f$ and
        @f$ \sum_{k,l} b_{k,l}x^{k}y^{l} @f$ is the polynomial
        @f$ \sum_{k,l} (a_{k,l} + b_{k,l})x^{k}y^{l} @f$.
        """
        x = self.__x_factor + other.x_factor()
        y = self.__y_factor + other.y_factor()
        return self.__class__( x, y )


    def __neg__(self):
        """
        Return the additive inverse (the negative) of @p self.
        
        A polynomial is negated by negating its coefficients: the additive
        inverse of @f$ \sum_{k,l} a_{k,l}x^{k}y^{l} @f$ is
        @f$ \sum_{k,l} -a_{k,l}x^{k}y^{l} @f$.
        """
        return self.__class__(
                    -self.__x_factor,
                    -self.__y_factor
                )
    
    
    def __mul__(self, other):
        """
        Return the product of @p self and @p other. The infix operator @c *
        calls this method.
        
        Two polynomials are multiplied through convolution of their
        coefficients; however that is overly complicated to write with sums.
        Instead, simply imagine mutliplying the canonical forms
        @f$ a(x) + y \cdot b(x) @f$ and @f$ c(x) + y \cdot d(x) @f$.
        
        @see   rings.polynomials.naive.Polynomials.__mul__() for an explanation
               of univariate polynomial multiplication.
        """
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
        """
        Return the quotient and remainder of @p self divided by @p other.
        
        The built-in method @c divmod() calls this method.  For the returned
        values @c quotient and @c remainder, we have
        @code
        self == quotient * other + remainder
        @endcode

        @note  Division has limited functionality in this implementation.  It
               only works in the following cases:
               - The divisor (@p other) is a polynomial in @f$ x @f$ alone; this
                 works for all dividends.
               - Dividend (@p self) and divisor (@p other) are polynomials in
                 @f$ y @f$ alone.
        """
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
        
        quotient = self.__class__( qx, qy )
        remainder = self.__class__( rx, ry )
        
        return quotient, remainder


    #- Class Methods----------------------------------------------------------- 
    
    @classmethod
    def curve(cls):
        """
        Return the elliptic curve over which the polynomial ring was defined.
        """
        return cls._elliptic_curve


    @classmethod
    def y2_reduction(cls):
        """
        Return the polynomial that may be substituted for @f$ y^2 @f$.  For an
        elliptic curve with parameters @f$ A, B @f$, this is the polynomial
        @f$ x^3 + Ax + B @f$.
        """
        try:
            return cls.__y2_reduction
        except AttributeError:
            # Use y**2 = x**3 + A*x + B to eliminate any y-power greater than 1.
            A, B = cls._elliptic_curve.parameters()
            cls.__y2_reduction = cls.polynomial_ring()( B, A, 0, 1 )
            return cls.__y2_reduction

    
    @classmethod
    def polynomial_ring(cls):
        """
        Return the ring of (univariate) polynomials that is source of the
        polynomials @f$ a @f$ and @f$ b @f$ in the canonical form
        @f$ s(x, y) = a(x) + y \cdot b(x) @f$.
        """
        try:
            return cls.__polynomial_ring
        except AttributeError:
            cls.__polynomial_ring = Polynomials( cls._elliptic_curve.field() )
            return cls.__polynomial_ring


    @classmethod
    def zero(cls):
        """
        Return the polynomial ring's neutral element of addition: the zero
        polynomial.
        """
        R = cls.polynomial_ring()
        return cls( R.zero(), R.zero() )

    
    @classmethod
    def one(cls):
        """
        Return the polynomial ring's neutral element of multiplication: the
        constant polynomial one.
        """
        R = cls.polynomial_ring()
        return cls( R.one(), R.zero() )
