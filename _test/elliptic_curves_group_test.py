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

from fields.finite.naive import FiniteField

def generate_test_suites(curve_implementation, infinity_implementation,  \
                          name_prefix):
  """
  Generate TestCase classes for the given implementations of elliptic curves
  and the point at infinity; combine them to TestSuites. This groups the tests
  by implementation and category (instead of category alone) and allows
  flexible addition and removal of implementations.
  """

  # Test the implementation for one small and one large field. Large
  # means that operands require more than 64 bit; the tenth Mersenne
  # prime will do as field size.
  F = FiniteField( 23 )
  G = FiniteField( 2**89 - 1 )

  # TODO: Add more test cases, especially larger ones
  E1 = curve_implementation(F, 1, 0)
  O = infinity_implementation()


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



  suites = []
  for test_class in [ PointsTest, GroupOperationTest, PointAtInfinityTest ]:
      test_class.__name__ = "{0}_{1}".format( name_prefix, test_class.__name__ )
      suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 
  return suites

#===============================================================================
# Implementation importing and TestSuites generation
#===============================================================================

import elliptic_curves.naive

implementations = [
    ( elliptic_curves.naive.EllipticCurve,
      elliptic_curves.naive.PointAtInfinity,
      "Naive" ),
]

all_suites = []
for curve_implementation, infinity_implementation, prefix in implementations:
    all_suites.extend(
            generate_test_suites(
                    curve_implementation,
                    infinity_implementation,
                    prefix
                )
        )


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
