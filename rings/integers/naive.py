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


"""
A wrapper that extends Python's built-in integer type @c int with the expected
ring interface.

@package   rings.integers.naive
@author    Peter Dinges <pdinges@acm.org>
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
