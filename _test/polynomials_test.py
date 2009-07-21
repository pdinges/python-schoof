# -*- coding: utf-8 -*-
# $Id$

import unittest

from polynomials.naive import PolynomialRing


# Use integers as coefficients
class IntegerRing:
    def __call__(self, n):
        return int(n)
    
    def zero(self):
        return 0

Z = IntegerRing()
R = PolynomialRing( Z )


class ElementsTest(unittest.TestCase):
    """
    Test cases concerning the creation and comparison of polynomials
    """
    #- Creation --------------------------------------------------------------- 
    def test_create(self):
        self.assertIsNotNone( R(0) )
        self.assertIsNotNone( R(1, 2, 3, 4) )
    
    
    #- Equality --------------------------------------------------------------- 
    def test_eq_true(self):
        """Equality: true statement"""
        self.assert_( R(0, 3) == R(0, 3) )
        
    def test_eq_false(self):
        """Equality: false statement"""
        self.failIf( R(0, 3) == R(2, 5) )

    def test_eq_ignore_leading_zeros(self):
        self.assert_( R(0) == R(0, 0, 0) )
        self.assert_( R(1, -1, 3) == R(1, -1, 3, 0, 0) )


    #- Inequality ------------------------------------------------------------- 
    def test_neq_true(self):
        """Inequality: true statement"""
        self.failIf( R(0, 3) != R(0, 3) )
        
    def test_neq_false(self):
        """Inequality: false statement"""
        self.assert_( R(0, 3) != R(2, 5) )


    #- Degree ----------------------------------------------------------------- 
    def test_degree_base(self):
        """Degree base case"""
        self.assert_( R(0, 3).degree() == 1 )
        self.assert_( R(1, 2, 3, 4).degree() == 3 )

    def test_degree_constant(self):
        """Degree of constant polynomials"""
        self.assert_( R(2).degree() == 0 )
        self.assert_( R(-1).degree() == 0 )

    def test_degree_zero(self):
        """Degree of zero polynomial"""
        # TODO: Test for minus infinity
        pass

        

class ArithmeticTest(unittest.TestCase):
    """Test cases for arithmetic operations on polynomials"""
    # These tests rely on working equality comparison and
    # not all elements being zero.

    #- Addition --------------------------------------------------------------- 
    def test_add_base(self):
        """Addition base case"""
        self.assert_( R(1, 2, 3) + R(3, 2, 1) == R(4, 4, 4) )

    def test_add_different_length(self):
        """Addition with different lengths"""
        self.assert_( R(1) + R(0, 2, 3) == R(1, 2, 3) )

    
    #- Negation (unary minus) ------------------------------------------------- 
    def test_neg_base(self):
        """Negation (additive inverse) base case"""
        self.assert_( -R(-2, 3, 8) == R(2, -3, -8) )
        self.assert_( R(1, 3) + (-R(1, 3)) == R(0) )

    def test_neg_double(self):
        """Double negation"""
        self.assert_( -(-(R(17, 3, 9))) == R(17, 3, 9) )


    #- Subtraction ------------------------------------------------------------ 
    def test_sub_base(self):
        """Subtraction base case"""
        self.assert_( R(8, 5, 3) - R(2, 17, 1) == R(6, -12, 2) )

    def test_sub_wrap(self):
        """Subtraction with different lengths"""
        self.assert_( R(8) - R(2, 17, 1) == R(6, -17, -1) )

    def test_sub_as_add(self):
        """Subtraction as addition of negative"""
        self.assert_( R(5, 4) + (-R(2)) == R(5, 4) - R(2) )


    #- Multiplication --------------------------------------------------------- 
    def test_mul_base(self):
        """Multiplication base case"""
        self.assert_( R(3) * R(4, 0, 1) == R(12, 0, 3) )
        self.assert_( R(0, 1) * R(4, 0, 1) == R(0, 4, 0, 1) )

    def test_mul_zero(self):
        """Multiplication with wrap-around"""
        self.assert_( R(0) * R(7, 3, 2) == R(0) )

    def test_mul_inverse(self):
        """Multiplicative inverse raises an exception"""
        self.assertRaises( TypeError, R(1).multiplicative_inverse )
        
    
    #- Exponentiation --------------------------------------------------------- 
    def test_pow_base(self):
        """Integer power base case"""
        self.assert_( R(1, 1)**2 == R(1, 2, 1) )    

    
if __name__ == "__main__":
    unittest.main()
