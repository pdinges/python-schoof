# -*- coding: utf-8 -*-
# $Id$

import unittest

from fields.naive import FiniteField
from elliptic_curves.naive import EllipticCurve, PointAtInfinity


# Test the implementation for one small and one large field. Large
# means that operands require more than 64 bit; the tenth Mersenne
# prime will do as field size.
F = FiniteField(23)
G = FiniteField( 2**89 - 1 )

# TODO: Add more test cases, especially larger ones
E1 = EllipticCurve(F, 1, 0)
O = PointAtInfinity()


# TODO: Add test cases for point creation (on the curve or not)


class PointsTest(unittest.TestCase):
    """
    Test cases for creating and comparing points on elliptic curves 
    """
    #- Equality --------------------------------------------------------------- 
    def test_eq_true(self):
        """Equality: true statement"""
        self.assert_( E1(9, 5) == E1(9, 5) )
        
    def test_eq_false(self):
        """Equality: false statement"""
        self.failIf( E1(9, 5) == E1(13, 5) )


    #- Inequality ------------------------------------------------------------- 
    def test_neq_true(self):
        """Inequality: true statement"""
        self.failIf( E1(9, 5) != E1(9, 5) )
        
    def test_neq_false(self):
        """Inequality: false statement"""
        self.assert_( E1(9, 5) != E1(13, 5) )


    #- Finiteness ------------------------------------------------------------- 
    def test_infinite(self):
        """Test for infinity"""
        self.failIf( E1(9, 5).is_infinite() )


class GroupOperationTest(unittest.TestCase):
    """
    Test cases for the group operation on elliptic curves
    """
    #- Addition --------------------------------------------------------------- 
    def test_add_base(self):
        """Addition base case"""
        self.assert_( E1(9,5) + E1(13, 5) == E1(1, 18) )

    def test_add_infinity(self):
        """Addition of neutral element (point at infinity)"""
        self.assert_( E1(11, 10) + O == E1(11, 10) )

    def test_add_double(self):
        """Point duplication"""
        self.assert_( E1(11, 10) + E1(11, 10) == E1(13, 18) )
        

    #- Additive inverse (unary minus) ----------------------------------------- 
    def test_neg_base(self):
        """Negation (additive inverse) base case"""
        self.assert_( -E1(9, 5) == E1(9, -5) )
        self.assert_( E1(9, 5) + (-E1(9, 5)) == O)
        
    def test_neg_double(self):
        """Double negation"""
        self.assert_( -(-E1(9, 5)) == E1(9, 5) )

    
    #- Subtraction ------------------------------------------------------------ 
    def test_sub_base(self):
        """Subtraction base case"""
        self.assert_( E1(9, 5) - E1(13, -5) == E1(1, 18) )


    #- Multiplication with integers (repeated addition) ----------------------- 
    def test_mul_base(self):
        """Multiplication with integers (point as left factor) base case"""
        P = E1(11, 10)
        self.assert_( P * 2 == P + P )
        self.assert_( P * 5 == P + P + P + P + P )
        self.assert_( P * 6 == P + P + P + P + P + P )

    def test_mul_zero(self):
        """Multiplication with zero (point as left factor)"""
        self.assert_( E1(11, 10) * 0 == O )

    def test_rmul_base(self):
        """Multiplication with integers (point as right factor)"""
        P = E1(11, 10)
        self.assert_( 2 * P == P + P )
        self.assert_( 5 * P == P + P + P + P + P )
        self.assert_( 6 * P == P + P + P + P + P + P )

    def test_rmul_zero(self):
        """Multiplication with zero (point as right factor)"""
        self.assert_( 0 * E1(11, 10) == O )
        

class PointAtInfinityTest(unittest.TestCase):
    """
    Test cases for the point at infinity
    """
    def test_eq(self):
        """Equality"""
        self.assert_( O == O )
        self.failIf( O == E1(9, 5) )
        
    def test_neq(self):
        """Inequality"""
        self.failIf( O != O )
        self.assert_( O != E1(9, 5) )
        
    def test_infinite(self):
        """Test for infinity"""
        self.assert_( O.is_infinite() )
    
    def test_add(self):
        """Addition"""
        self.assert_( O + E1(11, 10) == E1(11, 10) )
        self.assert_( O + O == O)

    def test_neg(self):
        """Negation (additive inverse)"""
        self.assert_( O == (-O) )

    def test_mul(self):
        """Multiplication with integers"""
        self.assert_( O * 7 == O )
        self.assert_( 7 * O == O)


if __name__ == "__main__":
    unittest.main()
