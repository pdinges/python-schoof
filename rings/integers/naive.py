# -*- coding: utf-8 -*-
# $Id$

"""
A wrapper that extends Python's built-in integer type @c int with the expected
ring interface.

@package   rings.integers.naive
@author    Peter Dinges <me@elwedgo.de>
"""

from support.profiling import profiling_name

@profiling_name("Z")
class Integers(int):
    """
    The ring of integers.  This wrapper class extends Python's built-in integer
    type @c int with the interface provided by the other ring classes.
    
    @see   rings.polynomials.naive.Polynomials,
           rings.quotients.naive.QuotientRing
    """
    
    @staticmethod
    def zero():
        """
        Return @c 0, the neutral element of integer addition.
        """
        return 0

    @staticmethod
    def one():
        """
        Return @c 1, the neutral element of integer multiplication.
        """
        return 1
