# -*- coding: utf-8 -*-
# $Id$

import unittest

from rings.integers.naive import Integers
from rings.polynomials.naive import Polynomials

def generate_test_suites(fractionfield_implementation, name_prefix):
  """
  Generate TestCase classes for the given field of fractions implementation
  and combine all tests to TestSuites. This groups the tests by implementation
  and category (instead of category alone) and allows flexible addition
  and removal of implementations.
  """

  Z = Integers
  P = Polynomials( Z )
  
  Q = fractionfield_implementation( Z )
  R = fractionfield_implementation( P )

  class ElementsTest(unittest.TestCase):
    """
    Test cases concerning the creation and comparison of
    elements of the field of fractions
    """
    #- Creation --------------------------------------------------------------- 
    def test_create(self):
        """Element creation"""
        self.assertIsNotNone( Q(0) )
        self.assertIsNotNone( Q(1, 1) )
        self.assertIsNotNone( R(P(0)) )
        self.assertIsNotNone( R(P(1), P(2)) )
    
    def test_create_default_denominator(self):
        """Element creation with default (unity) denominator"""
        self.assert_( Q(1) == Q(1, 1) )
        self.assert_( Q(3) == Q(3, 1) )
        self.assert_( R(P(1)) == R(P(1), P(1)) )
        self.assert_( R(P(3, 1)) == R(P(3, 1), P(1)) )
        
    def test_create_zero_denominator(self):
        """Element creation with zero denominator raises exception"""
        def f():
            return Q(1, 0)
        def g():
            return R( P(1), P(0) )
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )
    
    def test_create_idempotent(self):
        """Element creation accepts elements of the same field"""
        self.assert_( Q(Q(1)) == Q(1) )
        self.assert_( Q(Q(7, 13)) == Q(7, 13) )
        self.assert_( R(R(P(1))) == R(P(1)) )
        self.assert_( R(R(P(7, 2), P(13))) == R(P(7, 2), P(13)) )
    
    def test_create_uncastable(self):
        """Element creation raises exception if uncastable"""
        def f():
            return Q( R(1) )
        self.assertRaises( TypeError, f )
    
    
    #- Equality --------------------------------------------------------------- 
    def test_eq_true_identical(self):
        """Equality: true statement (identical fractions)"""
        self.assert_( Q(1, 2) == Q(1, 2) )
        self.assert_( R(P(1, 4), P(2)) == R(P(1, 4), P(2)) )

    def test_eq_true_equivalent(self):
        """Equality: true statement (equivalent fractions)"""
        self.assert_( Q(1, 2) == Q(3, 6) )
        self.assert_( R(P(3, 2), P(4)) == R(P(6, 4), P(8)) )
        
    def test_eq_false(self):
        """Equality: false statement"""
        self.failIf( Q(1, 2) == Q(3, 4) )
        self.failIf( R(P(1, 1), P(2)) == R(P(3)) )

    def test_eq_casting(self):
        """Equality: automatic casting of right hand side"""
        self.assert_( Q(1) == 1 )
        self.assert_( R(P(1)) == P(1) )
        self.assert_( R(P(1)) == 1 )    # Now with 50% more casting!
        
    def test_eq_casting_reversed(self):
        """Equality: automatic casting of left hand side"""
        self.assert_( 1 == Q(1) )
        self.assert_( P(1) == R(P(1)) )
        self.assert_( 1 == R(P(1)) )


    #- Inequality ------------------------------------------------------------- 
    def test_neq_true(self):
        """Inequality: true statement"""
        self.assert_( Q(1, 2) != Q(3, 4) )
        self.assert_( R(P(4, 3), P(7, 1)) != R(3, 4) )
      
    def test_neq_true_identical(self):
        """Inequality: false statement (identical fractions)"""
        self.failIf( Q(1, 2) != Q(1, 2) )
        self.failIf( R(P(4, 3), P(1, 2)) != R(P(4, 3), P(1, 2)) )

    def test_neq_true_equivalent(self):
        """Inequality: false statement (equivalent fractions)"""
        self.failIf( Q(1, 2) != Q(7, 14) )
        self.failIf( R(P(1, 2), P(3, 1)) != R(P(4, 8), P(12, 4)) )

    def test_neq_casting(self):
        """Inequality: automatic casting of right hand side"""
        self.assert_( Q(1) != 2 )
        self.assert_( R(P(1)) != P(2) )
        self.assert_( R(P(1)) != 2 )
        
    def test_neq_casting_reversed(self):
        """Inequality: automatic casting of left hand side"""
        self.assert_( 2 != Q(1) )
        self.assert_( P(2) != R(P(1)) )
        self.assert_( 2 != R(P(1)) )
      
      
    #- Test for zero ----------------------------------------------------------
    def test_zero_true(self):
        """Test for zero: true"""
        self.failIf( Q(0) )
        self.failIf( Q(0, 3) )
        self.failIf( R(P(0)) )
        self.failIf( R(P(0), P(8, 3)) )

    def test_zero_false(self):
        """Test for zero: false"""
        self.assert_( Q(1) )
        self.assert_( Q(2, 3) )
        self.assert_( R(P(1)) )
        self.assert_( R(P(2, 2), P(3)) )


  class ArithmeticTest(unittest.TestCase):
    """Test cases for arithmetic operations over fields of fractions"""
    # These tests rely on working equality comparison and
    # not all elements being zero.

    #- Addition --------------------------------------------------------------- 
    def test_add_base(self):
        """Addition base case"""
        self.assert_( Q(1, 2) + Q(3, 2) == Q(2) )
        self.assert_( R(P(1, 2), P(2)) + R(P(3, 2), P(2)) == R(P(2, 2)) )

    def test_add_denominators(self):
        """Addition with different denominators"""
        self.assert_( Q(1, 2) + Q(3, 4) == Q(5, 4) )
        p = R(P(-1, 1), P(2))
        q = R(P(-1, 3), P(1, 1))
        self.assert_( p + q == R(P(-3, 6, 1), P(2, 2)) )

    def test_add_casting(self):
        """Addition: automatic casting of right summand"""
        self.assert_( Q(1, 2) + 2 == Q(5, 2) )
        self.assert_( R(P(1, 2), P(1, 1)) + 2 == R(P(3, 4), P(1, 1)) )
    
    def test_add_casting_reversed(self):
        """Addition: automatic casting of left summand"""
        self.assert_( 2 + Q(1, 2) == Q(5, 2) )
        self.assert_( 2 + R(P(1, 2), P(1, 1)) == R(P(3, 4), P(1, 1)) )
    

    #- Negation (unary minus) ------------------------------------------------- 
    def test_neg_base(self):
        """Negation (additive inverse) base case"""
        self.assert_( Q(13) + (-Q(13)) == Q(0) )
        self.assert_( Q(13, 7) + (-Q(13, 7)) == Q(0) )
        self.assert_( R(P(1, 3)) + (-R(P(1, 3))) == R(P(0)) )
        self.assert_( R(P(1, 3), P(1, 1)) + (-R(P(1, 3), P(1, 1))) == R(P(0)) )

    def test_neg_numerator(self):
        """Negation: numerator"""
        self.assert_( -Q(5) == Q(-5) )
        self.assert_( -Q(7, 8) == Q(-7, 8) )
        self.assert_( -R(P(5, 2)) == R(-P(5, 2)) )
        self.assert_( -R(P(5, 2), P(1, 2)) == R(-P(5, 2), P(1, 2)) )

    def test_neg_denominator(self):
        """Negation: denominator"""
        self.assert_( -Q(5) == Q(5, -1) )
        self.assert_( -Q(7, 8) == Q(7, -8) )
        self.assert_( -R(P(5, 2)) == R(P(5, 2), -P(1)) )
        self.assert_( -R(P(5, 2), P(1, 2)) == R(P(5, 2), -P(1, 2)) )

    def test_neg_double(self):
        """Double negation"""
        self.assert_( -(-(Q(12))) == Q(12) )
        self.assert_( -(-(R(P(1, 2)))) == R(P(1, 2)) )

    def test_neg_canceling(self):
        """Negation of numerator and denominator cancels out"""
        self.assert_( Q(9, 4) == Q(-9, -4) )
        self.assert_( R(P(1, 9), P(4)) == R(-P(1, 9), -P(4)) )


    #- Subtraction ------------------------------------------------------------ 
    def test_sub_base(self):
        """Subtraction base case"""
        self.assert_( Q(8) - Q(5) == Q(3) )
        self.assert_( R(P(8, 1)) - R(P(5)) == R(P(3, 1)) )

    def test_sub_denominators(self):
        """Subtraction with different denominators"""
        self.assert_( Q(5, 3) - Q(2, 6) == Q(16, 12) )
        p = R(P(5, 3), P(0, 1))
        q = R(P(2, 6), P(2))
        self.assert_( p - q == R(P(10, 4, -6), P(0, 2)) )

    def test_sub_as_add(self):
        """Subtraction as addition of negative"""
        self.assert_( Q(5) + (-Q(13)) == Q(5) - Q(13) )
        self.assert_( Q(2, 5) + (-Q(3, 14)) == Q(2, 5) - Q(3, 14) )
        p = R(P(5, 3), P(0, 1))
        q = R(P(2, 6), P(2))
        self.assert_( p + (-q) == p - q )

    def test_sub_casting(self):
        """Subtraction: automatic casting of subtrahend"""
        self.assert_( Q(5, 2) - 2 == Q(1, 2) )
        self.assert_( R(P(5, 3), P(0, 1)) - 2 == R(P(5, 1), P(0, 1)) )
    
    def test_sub_casting_reversed(self):
        """Subtraction: automatic casting of minuend"""
        self.assert_( 2 - Q(1, 2) == Q(3, 2) )
        self.assert_( 2 - R(P(5, 3), P(0, 1)) == R(P(-5, -1), P(0, 1)) )
    

    #- Multiplication --------------------------------------------------------- 
    def test_mul_base(self):
        """Multiplication base case"""
        self.assert_( Q(3) * Q(5) == Q(15) )
        self.assert_( R(P(-1, 1)) * R(P(1, 1)) == R(P(-1, 0, 1)) )

    def test_mul_denominators(self):
        """Multiplication with different denominators"""
        self.assert_( Q(5, 3) * Q(2, 7) == Q(10, 21) )
        p = R(P(1, 1), P(-2, 2))
        q = R(P(2), P(2, 2))
        self.assert_( p * q == R(P(2, 2), P(-4, 0, 4)) )

    def test_mul_inverse(self):
        """Multiplicative inverse base case"""
        self.assert_( Q(5).multiplicative_inverse() == Q(1, 5) )
        self.assert_( Q(1, 5).multiplicative_inverse() == Q(5) )
        self.assert_( R(P(3, 2)).multiplicative_inverse() == R(P(1), P(3, 2)) )
    
    def test_mul_inverse_zero(self):
        """Multiplicative inverse of zero raises exception"""
        def f():
            return Q(0).multiplicative_inverse()
        def g():
            return R(P(0)).multiplicative_inverse()
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )
    
    def test_mul_casting(self):
        """Multiplication: automatic casting of right factor"""
        self.assert_( Q(1, 2) * 3 == Q(3, 2) )
        self.assert_( R(P(2), P(1, 1)) * P(-1, 1) == R(P(-2, 2), P(1, 1)) )
    
    def test_mul_casting_reversed(self):
        """Multiplication: automatic casting of left factor"""
        self.assert_( 3 * Q(1, 2) == Q(3, 2) )
        self.assert_( P(-1, 1) * R(P(2), P(1, 1)) == R(P(-2, 2), P(1, 1)) )
    
    
    #- Division --------------------------------------------------------------- 
    def test_truediv_base(self):
        """Division base case"""
        self.assert_( Q(1) / Q(13, 6) == Q(13, 6).multiplicative_inverse() )
        self.assert_( Q(3, 5) / Q(7, 9) == Q(27, 35) )
        self.assert_( R(P(1)) / R(P(4, 2), P(1, 7)) ==
                        R(P(4, 2), P(1, 7)).multiplicative_inverse() )
        self.assert_( R(P(1, 1), P(2, 2)) / R(P(0, 1), P(-1, 1)) ==
                        R(P(-1, 0, 1), P(0, 2, 2)) )

    def test_truediv_zero(self):
        """Division by zero raises exception"""
        def f():
            return Q(1, 4) / Q(0)
        def g():
            return R(P(4, 5), P(1, 1)) / R(P(0))
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )

    def test_truediv_casting(self):
        """Division: automatic casting of divisor"""
        self.assert_( Q(1, 2) / 3 == Q(1, 6) )
        self.assert_( R(P(1, 2), P(3)) / P(2) == R(P(1, 2), P(6)) )
        self.assert_( R(P(1, 2), P(3)) / 2 == R(P(1, 2), P(6)) )
    
    def test_truediv_casting_reversed(self):
        """Division: automatic casting of dividend"""
        self.assert_( 3 / Q(2) == Q(3, 2) )
        self.assert_( P(2) / R(P(1, 2), P(3)) == R(P(6), P(1, 2)) )
        self.assert_( 2 / R(P(1, 2), P(3)) == R(P(6), P(1, 2)) )
    
    
    #- Exponentiation --------------------------------------------------------- 
    def test_pow_base(self):
        """Integer power base case"""
        self.assert_( Q(2)**3 == Q(8) )
        self.assert_( Q(2, 3)**3 == Q(8, 27) )
        self.assert_( R(P(1, 1))**2 == R(P(1, 2, 1)) )
        self.assert_( R(P(-1, 1), P(1, 1))**2 == R(P(1, -2, 1), P(1, 2, 1)) )
    


  suites = []
  for test_class in [ ElementsTest, ArithmeticTest ]:
      test_class.__name__ = "{0}_{1}".format( name_prefix, test_class.__name__ )
      suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 
  return suites


#===============================================================================
# Implementation importing and TestSuites generation
#===============================================================================

import fields.fraction.naive

implementations = [
    (fields.fraction.naive.FractionField, "Naive"),
]

all_suites = []
for implementation, prefix in implementations:
    all_suites.extend( generate_test_suites( implementation, prefix ) )


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
