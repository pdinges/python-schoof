# -*- coding: utf-8 -*-
# $Id$

import unittest

import fields.finite.naive
import rings.integers.naive
import rings.polynomials.naive

def generate_test_suites(quotientring_implementation, name_prefix):
  """
  Generate TestCase classes for the given quotient ring implementation and
  combine all tests to TestSuites. This groups the tests by implementation
  and category (instead of category alone) and allows flexible addition
  and removal of implementations.
  """

  # The tests for quotient rings over the integers largely coincide with the
  # unit tests for FiniteFields.  However, we cannot rely on naive.FiniteField
  # to use naive.QuotientRing; therefore we repeat (most of) the tests. 
  F = quotientring_implementation( rings.integers.naive.Integers, 17 )
  G = quotientring_implementation( rings.integers.naive.Integers, 10 )
  
  P = rings.polynomials.naive.Polynomials( fields.finite.naive.FiniteField( 17 ) )
  R = quotientring_implementation( P, P(1, 0, 0, 1) )


  class ElementsTest(unittest.TestCase):
    """
    Test cases concerning the creation and comparison of residue classes.
    """
    #- Creation --------------------------------------------------------------- 
    def test_create(self):
        """Element creation"""
        self.assertIsNotNone( F(0) )
        self.assertIsNotNone( G(0) )
        self.assertIsNotNone( R(P(0)))
    
    def test_create_casting(self):
        """Element creation casts integers into ring elements"""
        self.assertIsNotNone( R(0) )
        self.assertIsNotNone( R( (1, 2, 3) ) )
        
    def test_create_uncastable(self):
        """Element creation raises TypeError if uncastable"""
        def f():
            return G(F(1))
        def g():
            return F(G(2))
        def h():
            return R(G(3))
        self.assertRaises( TypeError, f )
        self.assertRaises( TypeError, g )
   
    def test_create_idempotent(self):
        """Element creation accepts elements of the same field"""
        self.assert_( F(F(1)) == F(1) )
        self.assert_( G(G(7)) == G(7) )
        self.assert_( R((1, 2, 3)) == R(R((1, 2, 3))) )
    
    
    #- Equality --------------------------------------------------------------- 
    def test_eq_true(self):
        """Equality: true statement"""
        self.assert_( F(3) == F(3) )
        self.assert_( G(3) == G(3) )
        self.assert_( R((4, 2)) == R((4, 2)) )
        
    def test_eq_false(self):
        """Equality: false statement"""
        self.failIf( F(3) == F(5) )
        self.failIf( G(3) == G(15) )
        self.failIf( R((4, 2)) == R((2, 3)) )

    def test_eq_casting_ring_elements(self):
        """Equality: automatic casting of ring elements on the right hand side"""
        self.assert_( R((1, 5, 8)) == P(1, 5, 8) )
        
    def test_eq_casting_integers(self):
        """Equality: automatic casting of integers on the right hand side"""
        self.assert_( F(1) == 1 )
        self.assert_( G(6) == 6 )
        self.assert_( R(4) == 4 )
        
    def test_eq_casting_ring_elements_reversed(self):
        """Equality: automatic casting of ring elements on the left hand side"""
        self.assert_( P(3, 7, 0) == R((3, 7, 0)) )
        
    def test_eq_casting_integers_reversed(self):
        """Equality: automatic casting of integers on the left hand side"""
        self.assert_( 3 == F(3) )
        self.assert_( 5 == G(5) )
        self.assert_( 4 == R(4) )
        
    def test_eq_uncastable(self):
        """Equality: uncastable resolves to false"""
        self.failIf( F(1) == G(1) )
        self.failIf( F(3) == R(3) )
        

    #- Inequality ------------------------------------------------------------- 
    def test_ne_true(self):
        """Inequality: true statement"""
        self.failIf( F(3) != F(3) )
        self.failIf( G(3) != G(3) )
        self.failIf( R((7, 2)) != R((7, 2)) )
        
    def test_ne_false(self):
        """Inequality: false statement"""
        self.assert_( F(3) != F(5) )
        self.assert_( G(3) != G(5) )
        self.assert_( R((0, 9, 2)) != R((4, 8)) )

    def test_ne_casting_ring_elements(self):
        """Inquality: automatic casting of ring elements on the right hand side"""
        self.assert_( R((1, 5, 8)) != P(3, 2, 1) )
        
    def test_ne_casting_integers(self):
        """Inequality: automatic casting of integers on the right hand side"""
        self.assert_( F(1) != 2 )
        self.assert_( G(1) != 2 )
        self.assert_( R(1) != 2 )
        
    def test_ne_casting_ring_elements_reversed(self):
        """Equality: automatic casting of ring elements on the left hand side"""
        self.assert_( P(3, 2, 1) != R((1, 6, 6)) )
        
    def test_ne_casting_integers_reversed(self):
        """Inequality: automatic casting of integers on the left hand side"""
        self.assert_( 2 != F(1) )
        self.assert_( 2 != G(1) )
        self.assert_( 2 != R(1) )
      
    def test_ne_uncastable(self):
        """Inequality: uncastable resolves to false"""
        self.assert_( F(1) != G(1) )
        self.assert_( R(2) != F(2) )


    #- Test for zero ---------------------------------------------------------- 
    def test_zero_true(self):
        """Test for zero: true"""
        self.failIf( F(0) )
        self.failIf( G(0) )
        self.failIf( R(0) )
        self.failIf( R((1, 0, 0, 1)) )

    def test_zero_false(self):
        """Test for zero: false"""
        self.assert_( F(23) )
        self.assert_( G(42) )
        self.assert_( R((1, 0, 1)) )


  class ArithmeticTest(unittest.TestCase):
    """Test cases for arithmetic operations over quotient rings"""
    # These tests rely on working equality comparison and
    # not all elements being zero.

    #- Addition --------------------------------------------------------------- 
    def test_add_base(self):
        """Addition base case"""
        self.assert_( F(3) + F(5) == F(8) )
        self.assert_( G(3) + G(5) == G(8) )
        # Use the tuple syntax to create polynomial residue classes:
        # R( (0,1) ) == R( P(0,1) )
        self.assert_( R(1) + R((0, 1)) == R((1, 1)) )

    def test_add_wrap(self):
        """Addition with wrap-around"""
        self.assert_( F(7) + F(13) == F(3) )
        self.assert_( G(6) + G(8) == G(4) )
        # Polynomial addition has no carrying, so polynomials cannot wrap 

    def test_add_casting(self):
        """Addition: automatic casting of right summand"""
        self.assert_( F(7) + 2 == F(9) )
        self.assert_( G(7) + 2 == G(9) )
        self.assert_( R((0, 1)) + 2 == R((2, 1)) )
    
    def test_add_casting_reversed(self):
        """Addition: automatic casting of left summand"""
        self.assert_( 4 + F(12) == F(16) )
        self.assert_( 4 + G(2) == G(6) )
        self.assert_( 2 + R((0, 1)) == R((2, 1)) )

    
    #- Negation (unary minus) ------------------------------------------------- 
    def test_neg_base(self):
        """Negation (additive inverse) base case"""
        self.assert_( -F(5) == F(-5) )
        self.assert_( F(13) + (-F(13)) == F.zero() )
        self.assert_( -G(5) == G(-5) )
        self.assert_( G(3) + (-G(3)) == G.zero() )
        self.assert_( -R((2, 3)) == R((-2, -3)) )
        self.assert_( R((7, 1, 4)) + (-R((7, 1, 4))) == R.zero() )

    def test_neg_double(self):
        """Double negation"""
        self.assert_( -(-(F(12))) == F(12) )
        self.assert_( -(-(G(5))) == G(5) )
        self.assert_( -(-(R((3, 2)))) == R((3, 2)) )


    #- Subtraction ------------------------------------------------------------ 
    def test_sub_base(self):
        """Subtraction base case"""
        self.assert_( F(8) - F(5) == F(3) )
        self.assert_( G(8) - G(5) == G(3) )
        self.assert_( R((2, 1)) - R((1, 5)) == R((1, -4)) )

    def test_sub_wrap(self):
        """Subtraction with wrap-around"""
        self.assert_( F(3) - F(13) == F(7) )
        self.assert_( G(2) - G(4) == G(8) )
        # Polynomial addition has no carrying, so polynomials cannot wrap 

    def test_sub_as_add(self):
        """Subtraction as addition of negative"""
        self.assert_( F(5) + (-F(13)) == F(5) - F(13) )
        self.assert_( G(5) + (-G(7)) == G(5) - G(7) )
        self.assert_( R((3, 9)) + (-R((4, 6))) == R((3, 9)) - R((4, 6)) )

    def test_sub_casting(self):
        """Subtraction: automatic casting of subtrahend"""
        self.assert_( F(13) - 2 == F(11) )
        self.assert_( G(6) - 2 == G(4) )
        self.assert_( R((4, 4)) - 2 == R((2, 4)) )
    
    def test_sub_casting_reversed(self):
        """Subtraction: automatic casting of minuend"""
        self.assert_( 6 - F(4) == F(2) )
        self.assert_( 9 - G(4) == G(5) )
        self.assert_( 6 - R((4, 4)) == R((2, -4)) )


    #- Multiplication --------------------------------------------------------- 
    def test_mul_base(self):
        """Multiplication base case"""
        self.assert_( F(3) * F(5) == F(15) )
        self.assert_( G(3) * G(2) == G(6) )
        self.assert_( R((0, 1)) * R((1, 3)) == R((0, 1, 3)) )

    def test_mul_wrap(self):
        """Multiplication with wrap-around"""
        self.assert_( F(5) * F(7) == F(1) )
        self.assert_( G(6) * G(3) == G(8) )
        self.assert_( R((0, 2, 1)) * R((0, 1)) == R((-1, 0, 2)) )

    def test_mul_inverse(self):
        """Multiplicative inverse base case"""
        self.assert_( F(5).multiplicative_inverse() == F(7) )
        self.assert_( G(7).multiplicative_inverse() == G(3) )
        self.assert_( R((0, 0, 1)).multiplicative_inverse() == R((0, -1)))
    
    def test_mul_inverse_zero(self):
        """Multiplicative inverse of zero raises exception"""
        def f():
            return F(0).multiplicative_inverse()
        def g():
            return G(0).multiplicative_inverse()
        def h():
            # 2 is a zero divisor in Z/10Z
            return G(2).multiplicative_inverse()
        def k():
            return R(0).multiplicative_inverse()
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )
        self.assertRaises( ZeroDivisionError, h )
        self.assertRaises( ZeroDivisionError, k )
    
    def test_mul_casting(self):
        """Multiplication: automatic casting of right factor"""
        self.assert_( F(4) * 3 == F(12) )
        self.assert_( G(4) * 3 == G(12) )
        self.assert_( R((4, 0, 2)) * 3 == R((12, 0, 6)) )
    
    def test_mul_casting_reversed(self):
        """Multiplication: automatic casting of left factor"""
        self.assert_( 4 * F(3) == F(12) )
        self.assert_( 4 * G(3) == G(12) )
        self.assert_( 3 * R((4, 0, 2)) == R((12, 0, 6)) )
        
    
    #- Division --------------------------------------------------------------- 
    def test_truediv_base(self):
        """Division base case"""
        self.assert_( F(1) / F(13) == F(13).multiplicative_inverse() )
        self.assert_( G(1) / G(9) == G(9).multiplicative_inverse() )
        self.assert_( R(1) / R((0, 0, 1)) == R((0, 0, 1)).multiplicative_inverse() )

    def test_truediv_zero_divisor(self):
        """Division by non-units raises exception"""
        def f():
            return F(1) / F(0)
        def g():
            return G(1) / G(0)
        def h():
            return G(1) / G(2)
        def k():
            return R(1) / R((1, 1))
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )
        self.assertRaises( ZeroDivisionError, h )
        self.assertRaises( ZeroDivisionError, k )

    def test_truediv_casting(self):
        """Division: automatic casting of divisor"""
        self.assert_( F(12) / 3 == F(4) )
        self.assert_( G(6) / 3 == G(2) )
        self.assert_( R((2, 4, 2)) / 1 == R((2, 4, 2)) )
    
    def test_truediv_casting_reversed(self):
        """Division: automatic casting of dividend"""
        self.assert_( 12 / F(4) == F(3) )
        self.assert_( 6 / G(3) == G(2) )
        self.assert_( 1 / R((0, -1)) == R((0, 0, 1)) )
    

    #- Exponentiation --------------------------------------------------------- 
    def test_pow_base(self):
        """Integer power base case"""
        self.assert_( F(2)**3 == F(8) )
        self.assert_( G(2)**3 == G(8) )
        self.assert_( R((1, 1))**2 == R((1, 2, 1)) )
    
    def test_pow_wrap(self):
        """Integer power with wrap-around"""
        self.assert_( F(15)**2 == F(4) )
        self.assert_( G(3)**3 == G(7) )
        self.assert_( R((0, 1))**3 == R(-1) )

    def test_pow_non_casting(self):
        """Integer power: no casting of exponent"""
        def f():
            return F(12) ** F(3)
        def g():
            return G(12) ** G(3)
        def h():
            return R((0, 1)) ** R(2)
        self.assertRaises( TypeError, f )
        self.assertRaises( TypeError, g )
        self.assertRaises( TypeError, h )


  suites = []
  for test_class in [ ElementsTest, ArithmeticTest ]:
      test_class.__name__ = "{0}_{1}".format( name_prefix, test_class.__name__ )
      suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 
  return suites


#===============================================================================
# Implementation importing and TestSuites generation
#===============================================================================

import rings.quotients.naive

implementations = [
    (rings.quotients.naive.QuotientRing, "Naive"),
]

all_suites = []
for implementation, prefix in implementations:
    all_suites.extend( generate_test_suites( implementation, prefix ) )


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
