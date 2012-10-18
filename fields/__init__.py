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
Field related classes and functions (field as in rational, real, or
complex numbers).

@package   fields
@author    Peter Dinges <pdinges@acm.org>
"""

class Field:
    """
    A base class for field elements that provides default operator overloading.
    
    For example, subtraction is defined as addition of the additive inverse.
    Derived classes therefore only have to implement the following operations
    to support the complete operator set:
    - __bool__(): Zero testing (@c True if not zero)
    - __eq__(): Equality testing with the @c == operator (@c True if equal)
    - __add__(): Addition with the @c + operator; @c self is the left summand
    - __neg__(): Negation with the @c - unary minus operator (the additive inverse)
    - __mul__(): Multiplication with the @c * operator; @c self is the
      left factor
    - multiplicative_inverse(): Reciprocal (the multiplicative inverse)
    
    The following operations are implemented in terms of above operations using
    the field axioms:
    - __neq__(): Inequality testing with the @c != operator
    - __radd__(): Addition with the @c + operator; @c self is the right summand
    - __sub__(): Subtraction with the @c - operator; @c self is the minuend
      (left element)
    - __rsub__(): Subtraction with the @c - operator; @c self is the
      subtrahend (right element)
    - __rmul__(): Multiplication with the @c * operator; @c self is the
      right factor
    - __truediv__(): Division with the @c / operator; @c self is the
      dividend (left element)
    - __rtruediv__(): Division with the @c / operator; @c self is the
      divisor (right element) 
    - __pow__(): Exponentiation with integers
    """
    
    #- Template Operations ---------------------------------------------------- 
    
    def __neq__(self, other):
        """
        Test whether another element @p other is different from @p self; return
        @c True if that is the case.  The infix operator @c != calls this
        method; for example:
        @code
        if self != other:
            do_something()
        @endcode
        """
        return not self.__eq__( other )
    
    def __radd__(self, other):
        """
        Return the sum of @p self and @p other.  The infix operator @c + calls
        this method if @p self is the right summand and @p other.__add__()
        returns @c NotImplemented. For example:
        @code
        result = other + self
        @endcode
        """
        return self.__add__( other )
    
    def __sub__(self, other):
        """
        Return the difference of @p self and @p other.  The infix operator @c -
        calls this method if @p self is the minuend (left element); for example:
        @code
        result = self - other
        @endcode
        """
        return self.__add__( -other )
    
    def __rsub__(self, other):
        """
        Return the difference of @p other and @p self.  The infix operator @c -
        calls this method if @p self is the subtrahend (right element) and
        @c other.__sub__() returns @c NotImplemented.  For example:
        @code
        result = other - self
        @endcode
        """
        # other - self == -(self - other)
        return -self.__sub__( other )
    
    def __rmul__(self, other):
        """
        Return the product of @p self and @p other.  The infix operator @c *
        calls this method if @p self is the right factor and @c other.__mul__()
        returns @c NotImplemented.  For example:
        @code
        result = other * self
        @endcode 
        """
        return self.__mul__( other )
    
    def __truediv__(self, other):
        """
        Return the quotient of @p self and @p other.  The infix operator @c /
        calls this method if @p self is the dividend; for example:
        @code
        result = self / other
        @endcode
        
        @exception ZeroDivisionError   if @p other is zero.
        @exception TypeError           if @p other lacks the
                                       multiplicative_inverse() method and
                                       cannot be cast to @p self's class.
        """
        if not other:
            raise ZeroDivisionError
        
        try:
            other = self.__class__(other)
            return self.__mul__( other.multiplicative_inverse() )
        
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, other):
        """
        Return the quotient of @p other and @p self.  The infix operator @c /
        calls this method if @p self is the divisor and @c other.__truediv__()
        returns @c NotImplemented.  For example
        @code
        result = other / self
        @endcode
        
        @exception ZeroDivisionError   if @p self is zero.
        """
        return self.multiplicative_inverse() * other

    def __pow__(self, n):
        """
        Return @p self taken to the @p n-th power.  The infix operator @c **
        calls this method; for example:
        @code
        result = self ** n
        @endcode
        
        @note  The implementation uses the most naive by-the-book method for
               exponentiation: the element is multiplied @p n-1 times with
               itself.  This is slow (and might skin your cat!).  However, the
               purpose of this code is to be easy to understand, not fast. 
        
        @param n   The exponent; it is expected to be a non-negative integer
                   type.  Negative integers and floats are unsupported.
        """
        # This only makes sense for integer arguments.
        result = self
        for i in range(1, int(n)):
            result = result * self
        
        return result


    #- Base Operations (Defined in Derived Classes) ---------------------------
    
    def __bool__(self):
        """
        Test whether the element is non-zero: return @c True if, and only if,
        it is non-zero. Otherwise return @c False.  Implicit conversions to
        boolean (truth) values use this method; for example when @c x is an
        element of a Field:
        @code
        if x:
            do_something()
        @endcode
        
        @exception NotImplementedError if this method is called; subclasses
                                       must implement this operation.
        """
        raise NotImplementedError
    
    def __eq__(self, other):
        """
        Test whether another element @p other is equal to @p self; return
        @c True if that is the case.  The infix operator @c == calls this
        method; for example:
        @code
        if self == other:
            do_something()
        @endcode
        
        @exception NotImplementedError if this method is called; subclasses
                                       must implement this operation.
        """
        raise NotImplementedError
    
    def __add__(self, other):
        """
        Return the sum of @p self and @p other.  The infix operator @c + calls
        this method if @p self is the left summand; for example:
        @code
        result = self + other
        @endcode
        
        @exception NotImplementedError if this method is called; subclasses
                                       must implement this operation.
        """
        raise NotImplementedError
    
    def __neg__(self):
        """
        Return the additive inverse of @p self.  The unary minus operator @c -x
        calls this method; for example:
        @code
        negated = -self
        @endcode

        @exception NotImplementedError if this method is called; subclasses
                                       must implement this operation.
        """
        raise NotImplementedError
    
    def __mul__(self, other):
        """
        Return the product of @p self and @p other.  The infix operator @c + calls
        this method if @p self is the left factor; for example:
        @code
        result = self * other
        @endcode
        
        @exception NotImplementedError if this method is called; subclasses
                                       must implement this operation.
        """
        raise NotImplementedError
    
    def multiplicative_inverse(self):
        """
        Return the multiplicative inverse of @p self.

        @exception NotImplementedError if this method is called; subclasses
                                       must implement this operation.
        """
        raise NotImplementedError
 