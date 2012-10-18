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
A naive implementation of an elliptic curve with points
using Cartesian coordinates as representation.

@package   elliptic_curves.naive
@author    Peter Dinges <pdinges@acm.org>
"""

from support.types import template
from support.profiling import profiling_name, local_method_names

@local_method_names
@profiling_name( "E<{_field}>" )
class EllipticCurve( metaclass=template("_field", "_A", "_B") ):
    """
    An elliptic curve; the points support additive infix notation for group
    operations, as well as multiplication by integers.
    
    This is a template class that must be instantiated with the field and the
    parameters @c A and @c B.  Use it, for example, as follows:
    @code
    # Instantiate the elliptic curve template as y^2 = x^3 + 3x + 4 over GF(7)
    E = EllipticCurve( FiniteField(7), 3, 4 )

    # Create two points and add them
    P = E(1, 1)
    Q = E(2, 5)
    
    P + Q == E(6, 0)   # Point addition
    3*P == E(0, 5)     # Multiplication by integers
    
    O = PointAtInfinity()
    P == P + O         # The point at infinity is the neutral element
    type(P) is E       # This is also true
    @endcode
    
    An elliptic curve is the set of all points @f$ E = \bigl\{ (x, y) \mid y^2
    = x^3 + Ax + B \bigr\} \cup \{\mathcal{O}\} @f$, where @f$ \mathcal{O} @f$
    is a special element, the point at infinity.  The points form an abelian
    group with the point at infinity as neutral element.
    
    The relation @f$ y^2 = x^3 + Ax + B @f$ between the (Cartesian) coordinates
    of the points @f$ (x, y) \in E @f$ is called the fundamental relation.

    @see   Charlap, Leonard S. and Robbins, David P., "CRD Expositroy Report 31:
           An Elementary Introduction to Elliptic Curves", 1988, chapter 1
    """
    
    #- Instance Methods ----------------------------------------------------------- 
    
    def __init__(self, x, y):
        """
        Construct a new point on the elliptic curve with coordinates @p x
        and @p y.
        
        The coordinates must be connected by the fundamental relation
        @f$ y^2 = x^3 + Ax + B @f$.
        
        @param x   The first coordinate of the point.  It will be interpreted
                   as an element of field(), which might result in a ValueError
                   or TypeError.
        @param y   The second coordinate of the point.  It will be interpreted
                   as an element of field(), which might result in a ValueError
                   or TypeError.
        
        @exception AssertionError  if the fundamental relation does not hold.
        @exception ValueError      if an argument cannot be cast as element
                                   of field(). 
        @exception TypeError       same as @c ValueError. 
        """
        self.__x = self._field( x )
        self.__y = self._field( y )

        A, B = self.parameters()
        x, y = self.__x, self.__y
        assert y ** 2 == x ** 3  +  A * x  +  B, \
            "point ({x}, {y}) is not on the curve".format(x=x, y=y)
    
    
    def x(self):
        """
        Return the first (Cartesian) coordinate of the point @f$ (x,y) @f$
        on the curve.
        
        @note  The fundamental relation links the coordinates:
               @f$ y^2 = x^3 + Ax + B @f$.
        """
        return self.__x
    
    
    def y(self):
        """
        Return the second (Cartesian) coordinate of the point @f$ (x,y) @f$
        on the curve.
        
        @note  The fundamental relation links the coordinates:
               @f$ y^2 = x^3 + Ax + B @f$.
        """
        return self.__y
    
    
    def is_infinite(self):
        """
        Test whether the point is infinite or not: always return @c False for
        the point is finite.  The point at infinity returns @c True.
        """
        return False

    
    def __bool__(self):
        """
        Test whether the point is infinite or not: always return @c True, for
        the point is finite.  The point at infinity returns @c False.
        
        Implicit conversions to boolean (truth) values use this method, for
        example when @c P is an element of EllipticCurve:
        @code
        if P:
            do_something()
        @endcode
        """
        return True
    
        
    def __eq__(self, other):
        """
        Test whether another point @p other is equal to @p self; return
        @c True if that is the case.  The infix operator @c == calls
        this method.
        
        Two points are equal if, and only if, both of their (Cartesian)
        coordinates are equal or if they both are infinite.
        """
        if other.is_infinite():
            return False
        else:
            return self.__x == other.x() and self.__y == other.y()
    
    
    def __neq__(self, other):
        """
        Test whether another point @p other is different from @p self; return
        @c True if that is the case.  The infix operator @c != calls
        this method.
        
        Two points are different if, and only if, they differ in at least one
        of their (Cartesian) coordinates. 
        """
        return not self == other
    
    
    def __add__(self, other):
        """
        Return the sum of @p self and @p other.  The infix operator @c + calls
        this method.
        
        The geometric interpretation of point addition is to draw a line between
        the points and mirror the point at the third intersection of line and
        curve on the y-axis.  However, the justification why this works is
        rather complicated.  Please see some introductory text for the formulas
        and the respective proofs.
        
        @note  Addition on elliptic curves is commutative.  The neutral element
               is the point at infinity (compare PointAtInfinity).
        
        @see   For example Washington, Lawrence C. "Elliptic Curves:
               Number Theory and Cryptography", second edition, CRC Press 2008,
               chapter 2.
        """
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
        """
        Generic addition of points @p self and @p other: the points are neither
        identical nor inverses.
        
        @note  This method should not be called directly.  Instead use the
               infix operator @c +, which calls __add__(). 
        
        @note  Putting the cases in separate methods makes call profiles more
               expressive.
        
        @see __add__()
        """
        gamma = (other.y() - self.__y) / (other.x() - self.__x)
        u = -self.__x - other.x() +  gamma ** 2
        v = -self.__y - gamma * (u - self.__x)
        
        return self.__class__(u, v)


    def __double__(self):
        """
        Point doubling: add a point to itself.
        
        @note  This method should not be called directly.  Instead use the
               infix operator @c +, which calls __add__().
        
        @note  Putting the cases in separate methods makes call profiles more
               expressive.
        
        @see __add__()
        """
        A, B = self.parameters()
        delta = (3 * self.__x ** 2  + A) / (2 * self.__y)
        u = -self.__x - self.__x +  delta ** 2
        v = -self.__y - delta * (u - self.__x)
        
        return self.__class__(u, v)
    
    
    def __neg__(self):
        """
        Return the additive inverse (the negative) of @p self.
        
        The additive inverse of a point @f$ (x,y) @f$ on the curve is
        @f$ (x, -y) @f$.
        """
        return self.__class__(self.__x, -self.__y)
    
    
    def __sub__(self, other):
        """
        Return the difference between @p self and @p other.  The infix operator
        @c - calls this method.
        
        This is the same as @p self + (-other).
        
        @see   __add__()
        """
        return self + (-other)
    
    
    def __mul__(self, n):
        """
        Multiplication with integers: adding @p n copies of the point @p self;
        the infix operator @c * calls this method.
        
        This method is used when self was the left factor.

        @param n   A number object that can be interpreted as an integer.  It
                   determines how often the point will be added to itself.
        
        @exception ValueError  if @p n cannot be cast to @c int().
        @exception TypeError   same as @c ValueError.  
        """
        n = int(n)
        if n == 0:
            return PointAtInfinity()
        
        point = self
        for i in range(1, n):
            point += self
        
        return point
    
    def __rmul__(self, other):
        """
        Multiplication with integers: adding @p n copies of the point @p self;
        the infix operator @c * calls this method.
        
        This method is used when self was the right factor.

        @param n   A number object that can be interpreted as an integer.  It
                   determines how often the point will be added to itself.
        
        @exception ValueError  if @p n cannot be cast to @c int().
        @exception TypeError   same as @c ValueError.  
        """
        # Multiplication with integers is always commutative.
        return self * other
    
    
    #- Class Methods----------------------------------------------------------- 
    
    @classmethod
    def field(cls):
        """
        Return the field over which the curve was defined.
        """
        return cls._field
    
    
    @classmethod
    def parameters(cls):
        """
        Return the parameter pair @f$ (A, B) @f$ of the curve.
        
        The parameters determine the fundamental relation
        @f$ y^2 = x^3 + Ax + B @f$.
        """
        return (cls._A, cls._B)
    
    
    @classmethod
    def is_singular(cls):
        """
        Test whether the curve is singular or not: return @c True if, and
        only if, the curve is singular.
        
        A curve is singular if the polynomial @f$ x^3 + Ax + B @f$ has
        repeated roots.
        """
        # A curve is singular if and only if its determinant is 0
        # (in fields of characteristic neither 2 nor 3).
        return not 4 * cls._A**3  + 27 * cls._B ** 2



class PointAtInfinity:
    """
    Point at infinity on an elliptic curve, that is, the neutral element
    of the abelian group of points; it supports additive infix notation for
    group operations, as well as multiplication by integers.
    
    @note  This implementation is independent of the representation
           used for finite points.
    """
    def is_infinite(self):
        """
        Test whether the point is infinite or not: always return @c True, for
        this is the point at infinity.  Finite points return @c False.
        """
        return True
    
    
    def __bool__(self):
        """
        Test whether the point is infinite or not: always return @c False, for
        the point is infinite.  Finite points return @c True.
        
        Implicit conversions to boolean (truth) values use this method, for
        example when @c P is the point at infinity:
        @code
        if not P:
            do_something()
        @endcode
        """
        return False
    
    
    def __eq__(self, other):
        """
        Test whether another point @p other is equal to @p self; return
        @c True if that is the case.  The infix operator @c == calls
        this method.
        
        Two points are equal if, and only if, both of their (Cartesian)
        coordinates are equal or they both are infinite.
        """
        return other.is_infinite()


    def __neq__(self, other):
        """
        Test whether another point @p other is different from @p self; return
        @c True if that is the case.  The infix operator @c != calls
        this method.
        
        Two points are different if, and only if, they differ in at least one
        of their (Cartesian) coordinates. 
        """
        return not other.is_infinite()
    

    def __add__(self, other):
        """
        Return the sum of @p self and @p other.  The infix operator @c + calls
        this method if @p self is the left summand.
        
        The point at infinity is the neutral element of an elliptic curve.
        Hence the returned value will always be @p other.

        @see   For example Washington, Lawrence C. "Elliptic Curves:
               Number Theory and Cryptography", second edition, CRC Press 2008,
               chapter 2.
        """
        return other


    def __radd__(self, other):
        """
        Return the sum of @p self and @p other; see __add__().
        """       
        return other
    
    
    def __neg__(self):
        """
        Return the additive inverse of the point at infinity, which is again
        the point at infinity.
        """
        return self
    
    
    def __sub__(self, other):
        """
        Return the difference between @p self and @p other; since the point at
        infinity is the netural element, the result will be @c -other.  The
        infix operator @c - calls this method.

        @see   elliptic_curves.naive.__neg__()
        """
        return -other


    def __rsub__(self, other):
        """
        Return the difference between @p other and @p self; since the point at
        infinity is the netural element, the result will be @c other.  The
        infix operator @c - calls this method.
        """
        return other

    
    def __mul__(self, other):
        """
        Multiplication with integers: adding @p n copies of the point @p self;
        the infix operator @c * calls this method.
        
        @return    @p self if @p other is a type that can be interpreted as
                   @c int because the point at infinity because is the neutral
                   element of addition.  If @p other is not an integer type,
                   then the return value is @c NotImplemented.
        """
        if isinstance(other, int):
            return self
        else:
            return NotImplemented
    
    
    def __rmul__(self, other):
        """
        Multiplication with integers; see __mul__().
        """       
        if isinstance(other, int):
            return self
        else:
            return NotImplemented
    

    def __str__(self):
        return "(infinity)"
