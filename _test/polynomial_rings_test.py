# -*- coding: utf-8 -*-
# $Id$

import sys
import unittest

from rings.integers.naive import IntegerRing
from fields.finite.naive import FiniteField

def generate_test_classes(polynomialring_implementation, name_prefix):
  """
  Generate TestCase classes for the given finite field implementation
  and add them to the module. This groups the tests by implementation
  and category (instead of category alone) and allows flexible addition
  and removal of implementations.
  """

  Z = IntegerRing()
  F = FiniteField( 17 )
  R = polynomialring_implementation( Z )
  S = polynomialring_implementation( F )

  class ElementsTest(unittest.TestCase):
    """
    Test cases concerning the creation and comparison of polynomials
    """
    #- Creation --------------------------------------------------------------- 
    def test_create(self):
        """Element creation"""
        self.assertIsNotNone( R(0) )
        self.assertIsNotNone( R(1, 2, 3, 4) )
     
    def test_create_idempotent(self):
        """Element creation accepts elements of the same field"""
        self.assert_( R(R(1)) == R(1) )
        self.assert_( R(R(7, 13)) == R(7, 13) )
    
    def test_create_uncastable(self):
        """Element creation raises exception if uncastable"""
        def f():
            return R( S(1) )
        self.assertRaises( TypeError, f )
   
    
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

    def test_eq_casting(self):
        """Equality: automatic casting of right hand side"""
        self.assert_( R(1) == 1 )
        
    def test_eq_casting_reversed(self):
        """Equality: automatic casting of left hand side"""
        self.assert_( 1 == R(1) )


    #- Inequality ------------------------------------------------------------- 
    def test_neq_true(self):
        """Inequality: true statement"""
        self.failIf( R(0, 3) != R(0, 3) )
        
    def test_neq_false(self):
        """Inequality: false statement"""
        self.assert_( R(0, 3) != R(2, 5) )

    def test_neq_casting(self):
        """Inequality: automatic casting of right hand side"""
        self.assert_( R(1) != 2 )
        
    def test_neq_casting_reversed(self):
        """Inequality: automatic casting of left hand side"""
        self.assert_( 2 != R(1) )
      

    #- Test for zero ---------------------------------------------------------- 
    def test_zero_true(self):
        """Test for zero: true"""
        self.failIf( R(0) )

    def test_zero_false(self):
        """Test for zero: false"""
        self.assert_( R(42) )
        self.assert_( R(0, 0, 7) )
    

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

    def test_add_casting(self):
        """Addition: automatic casting of right summand"""
        self.assert_( R(1, 2) + 2 == R(3, 2) )
    
    def test_add_casting_reversed(self):
        """Addition: automatic casting of left summand"""
        self.assert_( 2 + R(1, 2) == R(3, 2) )

    
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

    def test_sub_casting(self):
        """Subtraction: automatic casting of subtrahend"""
        self.assert_( R(5, 2) - 2 == R(3, 2) )
    
    def test_sub_casting_reversed(self):
        """Subtraction: automatic casting of minuend"""
        self.assert_( 2 - R(1, 2) == R(1, -2) )


    #- Multiplication --------------------------------------------------------- 
    def test_mul_base(self):
        """Multiplication base case"""
        self.assert_( R(3) * R(4, 0, 1) == R(12, 0, 3) )
        self.assert_( R(0, 1) * R(4, 0, 1) == R(0, 4, 0, 1) )

    def test_mul_zero(self):
        """Multiplication with zero"""
        self.assert_( R(0) * R(7, 3, 2) == R(0) )

    def test_mul_inverse(self):
        """Multiplicative inverse raises an exception"""
        self.assertRaises( TypeError, R(1).multiplicative_inverse )
    
    def test_mul_casting(self):
        """Multiplication: automatic casting of right factor"""
        self.assert_( R(1, 2) * 3 == R(3, 6) )
    
    def test_mul_casting_reversed(self):
        """Multiplication: automatic casting of left factor"""
        self.assert_( 3 * R(1, 2) == R(3, 6) )
        

    #- Division --------------------------------------------------------------- 
    def test_divmod_base(self):
        """Division base case"""
        q, r = divmod( S(-1, 0, 1, 2, -1, 4), S(1, 0, 1) )
        self.assert_( q == S(2, -2, -1, 4) )
        self.assert_( r == S(-3, 2) )

    def test_divmod_casting(self):
        """Division: automatic casting of divisor"""
        q, r = divmod( S(3, 4), 2 )
        # Coefficients in S come from a field; division by units is always OK.
        self.assert_( q == S(10, 2) )
        self.assert_( r == S(0) )
    
    def test_divmod_casting_reversed(self):
        """Division: automatic casting of dividend"""
        q, r = divmod( 3, S(1, 1) )
        self.assert_( q == S(0) )
        self.assert_( r == S(3) )
    
    def test_floordiv_base(self):
        """Division rounded to floor"""
        q = S(-1, 0, 1, 2, -1, 4) // S(1, 0, 1)
        self.assert_( q == S(2, -2, -1, 4) )

    def test_floordiv_casting(self):
        """Division rounded to floor: automatic casting of divisor"""
        self.assert_( S(3, 4) // 2 == S(10, 2) )
    
    def test_floordiv_casting_reversed(self):
        """Division rounded to floor: automatic casting of dividend"""
        self.assert_( 3 // S(1,1) == S(0) )
    
    def test_mod_base(self):
        """Modulo operation: base case"""
        r = S(-1, 0, 1, 2, -1, 4) % S(1, 0, 1)
        self.assert_( r == S(-3, 2) )

    def test_mod_casting(self):
        """Modulo operation: automatic casting of divisor"""
        self.assert_( S(3, 4) % 2 == S(0) )
    
    def test_mod_casting_reversed(self):
        """Modulo operation: automatic casting of modulus"""
        self.assert_( 5 % S(1,1) == S(5) )
    
    
    #- Exponentiation --------------------------------------------------------- 
    def test_pow_base(self):
        """Integer power base case"""
        self.assert_( R(1, 1)**2 == R(1, 2, 1) )    


  
  for test_class in [ ElementsTest, ArithmeticTest ]:
      test_class.__name__ = "{0}_{1}".format( name_prefix, test_class.__name__ ) 
      setattr( sys.modules[__name__], test_class.__name__, test_class )

    
#===============================================================================
# Implementation importing and TestCase class generation
#===============================================================================

import rings.polynomials.naive

implementations = [
    (rings.polynomials.naive.PolynomialRing, "Naive"),
]

for implementation, prefix in implementations:
    generate_test_classes( implementation, prefix )

    
if __name__ == "__main__":
    unittest.main()
