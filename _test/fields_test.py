# -*- coding: utf-8 -*-
# $Id$

import unittest

from fields.naive import FiniteField


# Test the implementation for one small and one large field. Large
# means that operands require more than 64 bit; the tenth Mersenne
# prime will do as field size.
F = FiniteField(17)
G = FiniteField( 2**89 - 1 )


class ElementsTest(unittest.TestCase):
    """
    Test cases concerning creation and comparison of
    elements of finite fields.
    """
    # TODO: Implement
    pass


class ArithmeticTest(unittest.TestCase):
    """Test cases for arithmetic operations over finite fields."""
    # These tests rely on working equality comparison and
    # not all elements being zero.

    def test_add_base(self):
        """Addition base case"""
        self.assert_( F(3) + F(5) == F(8) )
        self.assert_( G(3) + G(5) == G(8) )

    def test_add_wrap(self):
        """Addition with wrap-around"""
        self.assert_( F(7) + F(13) == F(3) )
        self.assert_( G(2**88) + G(2**88 + 1) == G(2) )


    def test_neg_base(self):
        """Negation (additive inverse) base case"""
        self.assert_( -F(5) == F(-5) )
        self.assert_( F(13) + (-F(13)) == F(0) )
        self.assert_( -G(5) == G(-5) )
        self.assert_( G(13) + (-G(13)) == G(0) )

    def test_neg_double(self):
        """Double negation"""
        self.assert_( -(-(F(12))) == F(12) )
        self.assert_( -(-(G(12))) == G(12) )


    def test_sub_base(self):
        """Subtraction without wrap-around"""
        self.assert_( F(8) - F(5) == F(3) )
        self.assert_( G(8) - G(5) == G(3) )

    def test_sub_wrap(self):
        """Subtraction with wrap-around"""
        self.assert_( F(3) - F(13) == F(7) )
        self.assert_( G(2) - G(2**88 + 1) == G(2**88) )

    def test_sub_as_add(self):
        """Subtraction as addition of negative"""
        self.assert_( F(5) + (-F(13)) == F(5) - F(13) )
        self.assert_( G(5) + (-G(13)) == G(5) - G(13) )


    def test_mul_base(self):
        """Multiplication base case"""
        self.assert_( F(3) * F(5) == F(15) )
        self.assert_( G(3) * G(5) == G(15) )

    def test_mul_wrap(self):
        """Multiplication with wrap-around"""
        self.assert_( F(5) * F(7) == F(1) )
        self.assert_( G(2**88) * G(2) == G(1) )

    def test_mul_inverse(self):
        """Multiplicative inverse base case"""
        self.assert_( F(5).inverse == F(7) )
        self.assert_( G(2**45).inverse == G(2**44) )
    
    def test_mul_inverse_zero(self):
        """Multiplicative inverse of zero raises exception"""
        def f():
            return F(0).inverse
        def g():
            return G(0).inverse
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )
    
    
    def test_truediv_base(self):
        """Division base case"""
        self.assert_( F(1) / F(13) == F(13).inverse )
        self.assert_( G(1) / G(13) == G(13).inverse )

    def test_truediv_zero(self):
        """Division by zero raises exception"""
        def f():
            return F(1) / F(0)
        def g():
            return G(127) / G(0)
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )


    def test_pow_base(self):
        """Integer power base case"""
        self.assert_( F(2)**3 == F(8) )
        self.assert_( G(2)**3 == G(8) )
    
    def test_pow_wrap(self):
        """Integer power with wrap-around"""
        self.assert_( F(15)**2 == F(4) )
        self.assert_( G(2**45)**2 == G(2) )
    
    
if __name__ == "__main__":
    unittest.main()
