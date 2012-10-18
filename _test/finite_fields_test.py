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


import unittest

def generate_test_suites(finitefield_implementation, name_prefix):
  """
  Generate TestCase classes for the given finite field implementation and
  combine all tests to TestSuites. This groups the tests by implementation
  and category (instead of category alone) and allows flexible addition
  and removal of implementations.
  """

  # Test the implementation for one small and one large field. Large
  # means that operands require more than 64 bit; the tenth Mersenne
  # prime will do as field size.
  F = finitefield_implementation( 17 )
  G = finitefield_implementation( 2**89 - 1 )


  class ElementsTest(unittest.TestCase):
    """
    Test cases concerning the creation and comparison of
    elements of finite fields
    """
    #- Creation --------------------------------------------------------------- 
    def test_create(self):
        """Element creation"""
        self.assertIsNotNone( F(0) )
        self.assertIsNotNone( G(0) )
     
    def test_create_uncastable(self):
        """Element creation raises TypeError if uncastable"""
        def f():
            return G(F(1))
        def g():
            return F(G(4))
        self.assertRaises( TypeError, f )
        self.assertRaises( TypeError, g )
   
    def test_create_idempotent(self):
        """Element creation accepts elements of the same field"""
        self.assert_( F(F(1)) == F(1) )
        self.assert_( G(G(1)) == G(1) )
        self.assert_( F(F(7)) == F(7) )
        self.assert_( G(G(7)) == G(7) )
    
    
    #- Equality --------------------------------------------------------------- 
    def test_eq_true(self):
        """Equality: true statement"""
        self.assert_( F(3) == F(3) )
        self.assert_( G(3) == G(3) )
        
    def test_eq_false(self):
        """Equality: false statement"""
        self.failIf( F(3) == F(5) )
        self.failIf( G(3) == G(15) )

    def test_eq_casting_integers(self):
        """Equality: automatic casting of integers on the right hand side"""
        self.assert_( F(1) == 1 )
        self.assert_( G(6) == 6 )
        
    def test_eq_casting_integers_reversed(self):
        """Equality: automatic casting of integers on the left hand side"""
        self.assert_( 3 == F(3) )
        self.assert_( 5 == G(5) )
        
    def test_eq_uncastable(self):
        """Equality: uncastable resolves to false"""
        self.failIf( F(1) == G(1) )
        

    #- Inequality ------------------------------------------------------------- 
    def test_ne_true(self):
        """Inequality: true statement"""
        self.failIf( F(3) != F(3) )
        self.failIf( G(3) != G(3) )
        
    def test_ne_false(self):
        """Inequality: false statement"""
        self.assert_( F(3) != F(5) )
        self.assert_( G(3) != G(5) )

    def test_ne_casting_integers(self):
        """Inequality: automatic casting of integers on the right hand side"""
        self.assert_( F(1) != 2 )
        self.assert_( G(1) != 2 )
        
    def test_ne_casting_integers_reversed(self):
        """Inequality: automatic casting of integers on the left hand side"""
        self.assert_( 2 != F(1) )
        self.assert_( 2 != G(1) )
      
    def test_ne_uncastable(self):
        """Inequality: uncastable resolves to false"""
        self.assert_( F(1) != G(1) )


    #- Test for zero ---------------------------------------------------------- 
    def test_zero_true(self):
        """Test for zero: true"""
        self.failIf( F(0) )
        self.failIf( G(0) )

    def test_zero_false(self):
        """Test for zero: false"""
        self.assert_( F(23) )
        self.assert_( G(42) )


  class ArithmeticTest(unittest.TestCase):
    """Test cases for arithmetic operations over finite fields"""
    # These tests rely on working equality comparison and
    # not all elements being zero.

    #- Addition --------------------------------------------------------------- 
    def test_add_base(self):
        """Addition base case"""
        self.assert_( F(3) + F(5) == F(8) )
        self.assert_( G(3) + G(5) == G(8) )

    def test_add_wrap(self):
        """Addition with wrap-around"""
        self.assert_( F(7) + F(13) == F(3) )
        self.assert_( G(2**88) + G(2**88 + 1) == G(2) )

    def test_add_casting(self):
        """Addition: automatic casting of right summand"""
        self.assert_( F(7) + 2 == F(9) )
        self.assert_( G(7) + 2 == G(9) )
    
    def test_add_casting_reversed(self):
        """Addition: automatic casting of left summand"""
        self.assert_( 4 + F(12) == F(16) )
        self.assert_( 4 + G(12) == G(16) )

    
    #- Negation (unary minus) ------------------------------------------------- 
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


    #- Subtraction ------------------------------------------------------------ 
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

    def test_sub_casting(self):
        """Subtraction: automatic casting of subtrahend"""
        self.assert_( F(13) - 2 == F(11) )
        self.assert_( G(13) - 2 == G(11) )
    
    def test_sub_casting_reversed(self):
        """Subtraction: automatic casting of minuend"""
        self.assert_( 6 - F(4) == F(2) )
        self.assert_( 6 - G(4) == G(2) )


    #- Multiplication --------------------------------------------------------- 
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
        self.assert_( F(5).multiplicative_inverse() == F(7) )
        self.assert_( G(2**45).multiplicative_inverse() == G(2**44) )
    
    def test_mul_inverse_zero(self):
        """Multiplicative inverse of zero raises exception"""
        def f():
            return F(0).multiplicative_inverse()
        def g():
            return G(0).multiplicative_inverse()
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )
    
    def test_mul_casting(self):
        """Multiplication: automatic casting of right factor"""
        self.assert_( F(4) * 3 == F(12) )
        self.assert_( G(4) * 3 == G(12) )
    
    def test_mul_casting_reversed(self):
        """Multiplication: automatic casting of left factor"""
        self.assert_( 4 * F(3) == F(12) )
        self.assert_( 4 * G(3) == G(12) )
        
    
    #- Division --------------------------------------------------------------- 
    def test_truediv_base(self):
        """Division base case"""
        self.assert_( F(1) / F(13) == F(13).multiplicative_inverse() )
        self.assert_( G(1) / G(13) == G(13).multiplicative_inverse() )

    def test_truediv_zero(self):
        """Division by zero raises exception"""
        def f():
            return F(1) / F(0)
        def g():
            return G(127) / G(0)
        self.assertRaises( ZeroDivisionError, f )
        self.assertRaises( ZeroDivisionError, g )

    def test_truediv_casting(self):
        """Division: automatic casting of divisor"""
        self.assert_( F(12) / 3 == F(4) )
        self.assert_( G(12) / 3 == G(4) )
    
    def test_truediv_casting_reversed(self):
        """Division: automatic casting of dividend"""
        self.assert_( 12 / F(4) == F(3) )
        self.assert_( 12 / G(4) == G(3) )
    

    #- Exponentiation --------------------------------------------------------- 
    def test_pow_base(self):
        """Integer power base case"""
        self.assert_( F(2)**3 == F(8) )
        self.assert_( G(2)**3 == G(8) )
    
    def test_pow_wrap(self):
        """Integer power with wrap-around"""
        self.assert_( F(15)**2 == F(4) )
        self.assert_( G(2**45)**2 == G(2) )

    def test_pow_non_casting(self):
        """Integer power: no casting of exponent"""
        def f():
            return F(12) ** F(3)
        def g():
            return G(12) ** G(3)
        self.assertRaises( TypeError, f )
        self.assertRaises( TypeError, g )


  suites = []
  for test_class in [ ElementsTest, ArithmeticTest ]:
      test_class.__name__ = "{0}_{1}".format( name_prefix, test_class.__name__ )
      suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 
  return suites


#===============================================================================
# Implementation importing and TestSuites generation
#===============================================================================

import fields.finite.naive

implementations = [
    (fields.finite.naive.FiniteField, "Naive"),
]

all_suites = []
for implementation, prefix in implementations:
    all_suites.extend( generate_test_suites( implementation, prefix ) )


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
