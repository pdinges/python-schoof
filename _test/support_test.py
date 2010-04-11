# -*- coding: utf-8 -*-
# $Id$

import unittest

#- Primes --------------------------------------------------------------------- 

from support.primes import primes_range, inverse_primorial

class PrimesRangeTest(unittest.TestCase):
    """Test cases for the function @c support.primes.primes_range"""
    
    def test_results(self):
        """Sample results"""
        self.assert_( list(primes_range(1, 10)) == [2, 3, 5, 7] )

    def test_lower_bound(self):
        """Inclusive lower bound"""
        self.assert_( list(primes_range(3, 10)) == [3, 5, 7] )

    def test_upper_bound(self):
        """Exclusive upper bound"""
        self.assert_( list(primes_range(1, 7)) == [2, 3, 5] )
    
    def test_empty(self):
        """Empty primes interval"""
        self.assert_( not primes_range(3, 2) )
         
    def test_iterable(self):
        """Iterable return type"""
        self.assert_( [2, 3, 5] == [ p for p in primes_range(2, 6) ] )


class InversePrimorialTest(unittest.TestCase):
    """Test cases for the function @c support.primes.inverse_primorial"""
    
    def test_results(self):
        """Sample results"""
        self.assert_( inverse_primorial(30) == 5 )
        self.assert_( inverse_primorial(31) == 6 )

    def test_empty(self):
        """Empty (too small) input"""
        self.assert_( inverse_primorial(-1) == 2 )


#===============================================================================
# TestSuites generation
#===============================================================================

all_suites = []
for test_class in [ PrimesRangeTest ]:
    all_suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
