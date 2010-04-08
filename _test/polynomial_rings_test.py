# -*- coding: utf-8 -*-
# $Id$

import unittest

from rings.integers.naive import Integers
from fields.finite.naive import FiniteField

from support.rings import gcd

def generate_test_suites(polynomialring_implementation, name_prefix):
  """
  Generate TestCase classes for the given ring of polynomials implementation
  and combine them to a TestSuite. This groups the tests by implementation
  and category (instead of category alone) and allows flexible addition
  and removal of implementations.
  """

  Z = Integers
  F = FiniteField( 17 )
  # Strictly speaking, we assume the coefficients to come from a field.
  # Most things, however, should work equally well over the ring of integers.
  R = polynomialring_implementation( Z )
  S = polynomialring_implementation( F )

  class ElementsTest(unittest.TestCase):
    """
    Test cases concerning the creation and comparison of polynomials
    """
    #- Creation --------------------------------------------------------------- 
    def test_create(self):
        """Element creation"""
        self.assertIsNotNone( R( Z(0) ) )
        self.assertIsNotNone( S( F(0) ) )
        self.assertIsNotNone( R( Z(1), Z(2), Z(3), Z(4) ) )
        self.assertIsNotNone( S( F(1), F(2), F(3), F(4) ) )
     
    def test_create_casting(self):
        """Element creation casts integers into field elements"""
        self.assert_( R( Z(1) ) == R(1) )
        self.assert_( S( F(1) ) == S(1) )
        self.assert_( R( Z(7), Z(13) ) == R(7, 13) )
        self.assert_( S( F(7), F(13) ) == S(7, 13) )

    def test_create_uncastable(self):
        """Element creation raises TypeError if uncastable"""
        def f():
            return R( S(1) )
        self.assertRaises( TypeError, f )
   
    def test_create_idempotent(self):
        """Element creation accepts elements of the same ring"""
        self.assert_( R(R(1)) == R(1) )
        self.assert_( S(S(1)) == S(1) )
        self.assert_( R(R(7, 13)) == R(7, 13) )
        self.assert_( S(S(7, 13)) == S(7, 13) )
    
    
    #- Equality --------------------------------------------------------------- 
    def test_eq_true(self):
        """Equality: true statement"""
        self.assert_( R(0, 3) == R(0, 3) )
        self.assert_( S(0, 3) == S(0, 3) )
        
    def test_eq_false(self):
        """Equality: false statement"""
        self.failIf( R(0, 3) == R(2, 5) )
        self.failIf( S(0, 3) == S(2, 5) )

    def test_eq_ignore_leading_zeros(self):
        self.assert_( R(0) == R(0, 0, 0) )
        self.assert_( S(0) == S(0, 0, 0) )
        self.assert_( R(1, -1, 3) == R(1, -1, 3, 0, 0) )
        self.assert_( S(1, -1, 3) == S(1, -1, 3, 17, 34, 0) )

    def test_eq_casting_field_elements(self):
        """Equality: automatic casting of field elements on the right hand side"""
        self.assert_( R(3) == Z(3) )
        self.assert_( S(3) == F(3) )
        
    def test_eq_casting_integers(self):
        """Equality: automatic casting of integers on the right hand side"""
        self.assert_( R(1) == 1 )
        self.assert_( S(1) == 1 )
        
    def test_eq_casting_field_elements_reversed(self):
        """Equality: automatic casting of field elements on the left hand side"""
        self.assert_( Z(3) == R(3) )
        self.assert_( F(3) == S(3) )

    def test_eq_casting_integers_reversed(self):
        """Equality: automatic casting of integers on the left hand side"""
        self.assert_( 1 == R(1) )
        self.assert_( 1 == S(1) )
        
    def test_eq_uncastable(self):
        """Equality: uncastable resolves to false"""
        self.failIf( R(1) == S(1) )
        

    #- Inequality ------------------------------------------------------------- 
    def test_ne_true(self):
        """Inequality: true statement"""
        self.failIf( R(0, 3) != R(0, 3) )
        self.failIf( S(0, 3) != S(0, 3) )
        
    def test_ne_false(self):
        """Inequality: false statement"""
        self.assert_( R(0, 3) != R(2, 5) )
        self.assert_( S(0, 3) != S(2, 5) )

    def test_ne_casting_field_elements(self):
        """Inequality: automatic casting of field elements on the right hand side"""
        self.assert_( R(1) != Z(2) )
        self.assert_( S(1) != F(2) )
        
    def test_ne_casting_integers(self):
        """Inequality: automatic casting of integers on the right hand side"""
        self.assert_( R(1) != 2 )
        self.assert_( S(1) != 2 )
        
    def test_ne_casting_field_elements_reversed(self):
        """Inequality: automatic casting of field elements on the left hand side"""
        self.assert_( Z(2) != R(1) )
        self.assert_( F(2) != S(1) )
      
    def test_ne_casting_integers_reversed(self):
        """Inequality: automatic casting of integers on the left hand side"""
        self.assert_( 2 != R(1) )
        self.assert_( 2 != S(1) )
      
    def test_ne_uncastable(self):
        """Inequality: uncastable resolves to false"""
        self.assert_( R(1) != S(1) )


    #- Test for zero ---------------------------------------------------------- 
    def test_zero_true(self):
        """Test for zero: true"""
        self.failIf( R(0) )
        self.failIf( S(0) )

    def test_zero_false(self):
        """Test for zero: false"""
        self.assert_( R(42) )
        self.assert_( S(42) )
        self.assert_( R(0, 0, 7) )
        self.assert_( S(0, 0, 7) )
    

    #- Degree ----------------------------------------------------------------- 
    def test_degree_base(self):
        """Degree base case"""
        self.assert_( R(0, 3).degree() == 1 )
        self.assert_( S(0, 3).degree() == 1 )
        self.assert_( R(1, 2, 3, 4).degree() == 3 )
        self.assert_( S(1, 2, 3, 4).degree() == 3 )

    def test_degree_constant(self):
        """Degree of constant polynomials"""
        self.assert_( R(2).degree() == 0 )
        self.assert_( S(2).degree() == 0 )
        self.assert_( R(-1).degree() == 0 )
        self.assert_( S(-1).degree() == 0 )

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
        self.assert_( S(1, 2, 3) + S(3, 2, 1) == S(4, 4, 4) )

    def test_add_different_length(self):
        """Addition with different lengths"""
        self.assert_( R(1) + R(0, 2, 3) == R(1, 2, 3) )
        self.assert_( S(1) + S(0, 2, 3) == S(1, 2, 3) )

    def test_add_casting_field_elements(self):
        """Addition: automatic casting of field elements as right summand"""
        self.assert_( R(1, 2) + Z(2) == R(3, 2) )
        self.assert_( S(1, 2) + F(2) == S(3, 2) )
    
    def test_add_casting_integers(self):
        """Addition: automatic casting of integers as right summand"""
        self.assert_( R(1, 2) + 2 == R(3, 2) )
        self.assert_( S(1, 2) + 2 == S(3, 2) )
    
    def test_add_casting_field_elements_reversed(self):
        """Addition: automatic casting of field elements as left summand"""
        self.assert_( Z(2) + R(1, 2) == R(3, 2) )
        self.assert_( F(2) + S(1, 2) == S(3, 2) )

    def test_add_casting_integers_reversed(self):
        """Addition: automatic casting of integers as left summand"""
        self.assert_( 2 + R(1, 2) == R(3, 2) )
        self.assert_( 2 + S(1, 2) == S(3, 2) )

    def test_add_uncastable(self):
        """Addition: raise TypeError if uncastable"""
        def f():
            return R(1) + S(2)
        self.assertRaises( TypeError, f )
    
    
    #- Negation (unary minus) ------------------------------------------------- 
    def test_neg_base(self):
        """Negation (additive inverse) base case"""
        self.assert_( -R(-2, 3, 8) == R(2, -3, -8) )
        self.assert_( -S(-2, 3, 8) == S(2, -3, -8) )
        self.assert_( R(1, 3) + (-R(1, 3)) == R(0) )
        self.assert_( S(1, 3) + (-S(1, 3)) == S(0) )

    def test_neg_double(self):
        """Double negation"""
        self.assert_( -(-(R(17, 3, 9))) == R(17, 3, 9) )
        self.assert_( -(-(S(17, 3, 9))) == S(17, 3, 9) )


    #- Subtraction ------------------------------------------------------------ 
    def test_sub_base(self):
        """Subtraction base case"""
        self.assert_( R(8, 5, 3) - R(2, 17, 1) == R(6, -12, 2) )
        self.assert_( S(8, 5, 3) - S(2, 17, 1) == S(6, -12, 2) )

    def test_sub_wrap(self):
        """Subtraction with different lengths"""
        self.assert_( R(8) - R(2, 17, 1) == R(6, -17, -1) )
        self.assert_( S(8) - S(2, 17, 1) == S(6, -17, -1) )

    def test_sub_as_add(self):
        """Subtraction as addition of negative"""
        self.assert_( R(5, 4) + (-R(2)) == R(5, 4) - R(2) )
        self.assert_( S(5, 4) + (-S(2)) == S(5, 4) - S(2) )

    def test_sub_casting_field_elements(self):
        """Subtraction: automatic casting of field elements as subtrahend"""
        self.assert_( R(5, 2) - Z(2) == R(3, 2) )
        self.assert_( S(5, 2) - F(2) == S(3, 2) )
    
    def test_sub_casting_integers(self):
        """Subtraction: automatic casting of integers as subtrahend"""
        self.assert_( R(5, 2) - 2 == R(3, 2) )
        self.assert_( S(5, 2) - 2 == S(3, 2) )
    
    def test_sub_casting_field_elements_reversed(self):
        """Subtraction: automatic casting of field elements as minuend"""
        self.assert_( Z(2) - R(1, 2) == R(1, -2) )
        self.assert_( F(2) - S(1, 2) == S(1, -2) )

    def test_sub_casting_integers_reversed(self):
        """Subtraction: automatic casting of integers as minuend"""
        self.assert_( 2 - R(1, 2) == R(1, -2) )
        self.assert_( 2 - S(1, 2) == S(1, -2) )

    def test_sub_uncastable(self):
        """Subtraction: raise TypeError if uncastable"""
        def f():
            return R(1) - S(2)
        self.assertRaises( TypeError, f )
    

    #- Multiplication --------------------------------------------------------- 
    def test_mul_base(self):
        """Multiplication base case"""
        self.assert_( R(3) * R(4, 0, 1) == R(12, 0, 3) )
        self.assert_( S(3) * S(4, 0, 1) == S(12, 0, 3) )
        self.assert_( R(0, 1) * R(4, 0, 1) == R(0, 4, 0, 1) )
        self.assert_( S(0, 1) * S(4, 0, 1) == S(0, 4, 0, 1) )

    def test_mul_zero(self):
        """Multiplication with zero"""
        self.assert_( R(0) * R(7, 3, 2) == R(0) )
        self.assert_( S(0) * S(7, 3, 2) == S(0) )

    def test_mul_inverse(self):
        """Multiplicative inverse raises an exception"""
        self.assertRaises( TypeError, R(1).multiplicative_inverse )
        self.assertRaises( TypeError, S(1).multiplicative_inverse )
    
    def test_mul_casting_field_elements(self):
        """Multiplication: automatic casting of field elements as right factor"""
        self.assert_( R(1, 2) * Z(3) == R(3, 6) )
        self.assert_( S(1, 2) * F(3) == S(3, 6) )
    
    def test_mul_casting_integers(self):
        """Multiplication: automatic casting of integers as right factor"""
        self.assert_( R(1, 2) * 3 == R(3, 6) )
        self.assert_( S(1, 2) * 3 == S(3, 6) )
    
    def test_mul_casting_field_elements_reversed(self):
        """Multiplication: automatic casting of field elements as left factor"""
        self.assert_( Z(3) * R(1, 2) == R(3, 6) )
        self.assert_( F(3) * S(1, 2) == S(3, 6) )
        
    def test_mul_casting_integers_reversed(self):
        """Multiplication: automatic casting of integers as left factor"""
        self.assert_( 3 * R(1, 2) == R(3, 6) )
        self.assert_( 3 * S(1, 2) == S(3, 6) )
        
    def test_mul_uncastable(self):
        """Multiplication: raise TypeError if uncastable"""
        def f():
            return R(1) * S(2)
        self.assertRaises( TypeError, f )
    

    #- Division --------------------------------------------------------------- 
    def test_divmod_base(self):
        """Division base case"""
        q, r = divmod( S(-1, 0, 1, 2, -1, 4), S(1, 0, 1) )
        self.assert_( q == S(2, -2, -1, 4) )
        self.assert_( r == S(-3, 2) )

    def test_divmod_casting_field_elements(self):
        """Division: automatic casting of field elements as divisor"""
        q, r = divmod( S(3, 4), F(2) )
        # Coefficients in S come from a field; division by units is always OK.
        self.assert_( q == S(10, 2) )
        self.assert_( r == S(0) )
    
    def test_divmod_casting_integers(self):
        """Division: automatic casting of integers as divisor"""
        q, r = divmod( S(3, 4), 2 )
        # Coefficients in S come from a field; division by units is always OK.
        self.assert_( q == S(10, 2) )
        self.assert_( r == S(0) )
    
    def test_divmod_casting_field_elements_reversed(self):
        """Division: automatic casting of field elements as dividend"""
        q, r = divmod( F(3), S(1, 1) )
        self.assert_( q == S(0) )
        self.assert_( r == S(3) )
    
    def test_divmod_casting_integers_reversed(self):
        """Division: automatic casting of integers as dividend"""
        q, r = divmod( 3, S(1, 1) )
        self.assert_( q == S(0) )
        self.assert_( r == S(3) )
    
    def test_floordiv_base(self):
        """Division rounded to floor"""
        q = S(-1, 0, 1, 2, -1, 4) // S(1, 0, 1)
        self.assert_( q == S(2, -2, -1, 4) )

    def test_floordiv_casting_field_elements(self):
        """Division rounded to floor: automatic casting of field elements as divisor"""
        self.assert_( S(3, 4) // F(2) == S(10, 2) )
    
    def test_floordiv_casting_integers(self):
        """Division rounded to floor: automatic casting of integers as divisor"""
        self.assert_( S(3, 4) // 2 == S(10, 2) )
    
    def test_floordiv_casting_field_elements_reversed(self):
        """Division rounded to floor: automatic casting of field elements as dividend"""
        self.assert_( F(3) // S(1,1) == S(0) )
    
    def test_floordiv_casting_integers_reversed(self):
        """Division rounded to floor: automatic casting of integers as dividend"""
        self.assert_( 3 // S(1,1) == S(0) )
    
    def test_mod_base(self):
        """Modulo operation: base case"""
        r = S(-1, 0, 1, 2, -1, 4) % S(1, 0, 1)
        self.assert_( r == S(-3, 2) )

    def test_mod_casting_field_elements(self):
        """Modulo operation: automatic casting of field elements as divisor"""
        self.assert_( S(3, 4) % F(2) == S(0) )
    
    def test_mod_casting_integers(self):
        """Modulo operation: automatic casting of integers as divisor"""
        self.assert_( S(3, 4) % 2 == S(0) )
    
    def test_mod_casting_field_elements_reversed(self):
        """Modulo operation: automatic casting of field elements as modulus"""
        self.assert_( F(5) % S(1,1) == S(5) )
    
    def test_mod_casting_integers_reversed(self):
        """Modulo operation: automatic casting of integers as modulus"""
        self.assert_( 5 % S(1,1) == S(5) )
    
    def test_mod_uncastable(self):
        """Divsion: raise TypeError if uncastable"""
        def f():
            return divmod( R(1), S(2) )
        self.assertRaises( TypeError, f )
    
    
    #- Exponentiation --------------------------------------------------------- 
    def test_pow_base(self):
        """Integer power base case"""
        self.assert_( R(1, 1)**2 == R(1, 2, 1) )    
        self.assert_( S(1, 1)**2 == S(1, 2, 1) )    

    def test_pow_non_casting(self):
        """Integer power: only integer exponents"""
        def f():
            return S(1, 1) ** F(3)
        self.assertRaises( TypeError, f )


    #- Greatest Common Divisor-------------------------------------------------
    # TODO: Move these tests to the unit test of support.rings 
    def test_gcd_base(self):
        """GCD base case"""
        self.assert_( gcd( S(1, 2, 1),  S(1, 1) ) == S(1, 1) )    
        # GCDs differ by a constant multiple, so make the result monic
        d = gcd( S(0, -1, 0, 1), S(1, 2, 1) ) 
        self.assert_(  d // d.leading_coefficient() == S(1, 1) )    
  
    def test_gcd_relatively_prime(self):
        """GCD of relatively prime elements"""
        self.assert_( gcd( S(-1, 0, 1), S(0, 1) ).degree() == 0 )
        
    def test_gcd_casting_field_elements(self):
        """GCD: automatic casting of field elements"""
        self.assert_( gcd( S(2, 4), F(2) ) == S( 2 ) )
    
    def test_gcd_casting_integers(self):
        """GCD: automatic casting of integers"""
        self.assert_( gcd( S(2, 4), 2 ) == S( 2 ) )
    
    def test_gcd_uncastable(self):
        """GCD: raise TypeError if uncastable"""
        def f():
            print( gcd( S(2, 3), R(1, 2) ) )
            return gcd( S(2, 3), R(1, 2) )
        self.assertRaises( TypeError, f )
  
  
  suites = []
  for test_class in [ ElementsTest, ArithmeticTest ]:
      test_class.__name__ = "{0}_{1}".format( name_prefix, test_class.__name__ )
      suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 
  return suites

    
#===============================================================================
# Implementation importing and TestSuites generation
#===============================================================================

import rings.polynomials.naive

implementations = [
    (rings.polynomials.naive.Polynomials, "Naive"),
]

all_suites = []
for implementation, prefix in implementations:
    all_suites.extend( generate_test_suites( implementation, prefix ) )


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
