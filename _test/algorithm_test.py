# -*- coding: utf-8 -*-
# $Id$

import unittest

from fields.finite.naive import FiniteField
from elliptic_curves.naive import EllipticCurve

def generate_test_suites(frobenius_trace_implementation, name_prefix):
  """
  Generate and combine TestCase classes for the given algorithm for computing
  the trace of the Frobenius endomorphism of elliptic curves over finite
  fields. This groups the tests by implementation and category (instead of
  category alone) and allows flexible addition and removal of implementations.
  """

  class FrobeniusTraceTest(unittest.TestCase):
    """
    Test cases for computing the trace of the Frobenius endomorphism on
    elliptic curves over finite fields
    
    This class assumes correct EllipticCurve and FiniteField implementations.
    """

    def test_5_1_1(self):
        """y^2 = x^3 + x + 1 over GF<5>"""
        # From section 4.1 in Washington, L. C.,
        # "Elliptic Curve --- Number Theory and Cryptography", second edition,
        # CRC Press, 2008
        self.assert_( self._count_points(5, 1, 1) == 9 )
        
    def test_7_0_2(self):
        """y^2 = x^3 + 2 over GF<7>"""
        # From section 4.1 in Washington, L. C.,
        # "Elliptic Curve --- Number Theory and Cryptography", second edition,
        # CRC Press, 2008
        self.assert_( self._count_points(7, 0, 2) == 9 )
    
    def test_23_7_16(self):
        """y^2 = x^3 + 7x + 16 over GF<23>"""
        # From http://www.certicom.com/ecc_tutorial/ecc_twopoints.html
        self.assert_( self._count_points( 23, 7, 16 ) == 22 )
        
    def _count_points(self, p, A, B):
        curve = EllipticCurve( FiniteField(p), A, B )
        trace = frobenius_trace_implementation( curve )
        return p + 1 - trace


  suites = []
  for test_class in [ FrobeniusTraceTest ]:
      test_class.__name__ = "{0}_{1}".format( name_prefix, test_class.__name__ )
      suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 
  return suites


#===============================================================================
# Implementation importing and TestSuites generation
#===============================================================================

import naive_schoof
import reduced_computation_schoof

implementations = [
    (naive_schoof.frobenius_trace, "Naive"),
    (reduced_computation_schoof.frobenius_trace, "Reduced"),
]

all_suites = []
for implementation, prefix in implementations:
    all_suites.extend( generate_test_suites( implementation, prefix ) )


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
