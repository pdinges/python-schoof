# -*- coding: utf-8 -*-
# $Id$

import unittest

#- Primes --------------------------------------------------------------------- 

from support.primes import primes_range

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


from support.primes import inverse_primorial

class InversePrimorialTest(unittest.TestCase):
    """Test cases for the function @c support.primes.inverse_primorial"""
    
    def test_results(self):
        """Sample results"""
        self.assert_( inverse_primorial(30) == 5 )
        self.assert_( inverse_primorial(31) == 7 )

    def test_empty(self):
        """Empty (too small) input"""
        self.assert_( inverse_primorial(-1) == 2 )


#- Quotients ------------------------------------------------------------------ 

from rings.integers.naive import Integers
from rings.quotients.naive import QuotientRing
from support.quotients import solve_congruence_equations

class CongruenceEquationTest(unittest.TestCase):
    """
    Test cases for the Chinese Remainder Theorem function
    @c support.quotients.solve_congruence_equations
    """
    def setUp(self):
        Z3 = QuotientRing( Integers, 3 )
        Z5 = QuotientRing( Integers, 5 )
        self._remainders = [ Z3(2), Z5(1) ]
    
    def test_result_type(self):
        """Solution is congruence"""
        solution = solve_congruence_equations( self._remainders )
        self.assert_( hasattr( solution, "remainder" ) ) 
        self.assert_( hasattr( solution, "modulus" ) ) 

    def test_result_modulus(self):
        """Sample solution: modulus"""
        solution = solve_congruence_equations( self._remainders )
        self.assert_( solution.modulus() == 15 ) 

    def test_result_remainder(self):
        """Sample solution: remainder"""
        solution = solve_congruence_equations( self._remainders )
        self.assert_( solution.remainder() == 11 )
    
    def test_empty_equations(self):
        """Empty set of congruence equations"""
        def f():
            solve_congruence_equations( [] )
        self.assertRaises( ValueError , f )
    

from support.quotients import inverse_modulo

class InverseModuloTest(unittest.TestCase):
    """Test cases for the computation of inverses of quotient classes"""
    
    def test_result(self):
        """Sample results"""
        self.assert_( (inverse_modulo(3, 5) - 2) % 5 == 0 )
        self.assert_( (inverse_modulo(3, 7) - 5) % 7 == 0 )

    def test_non_unit(self):
        """Input without inverse"""
        def f():
            inverse_modulo(2, 6)
        self.assertRaises( ValueError, f )

    def test_zero_modulus(self):
        """Zero modulus"""
        def f():
            inverse_modulo(2, 0)
        self.assertRaises( ZeroDivisionError, f )


#===============================================================================
# TestSuites generation
#===============================================================================

all_suites = []
for test_class in [
               PrimesRangeTest,
               InversePrimorialTest,
               CongruenceEquationTest,
               InverseModuloTest,
           ]:
    all_suites.append( unittest.TestLoader().loadTestsFromTestCase( test_class ) ) 


if __name__ == "__main__":
    all_tests = unittest.TestSuite( all_suites )
    unittest.TextTestRunner().run( all_tests )
