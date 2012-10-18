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

all_suites = []

#===============================================================================
# Collect all test suites 
#===============================================================================

#- Rings ---------------------------------------------------------------------- 
from . import polynomial_rings_test
all_suites.extend( polynomial_rings_test.all_suites )

from . import quotient_rings_test
all_suites.extend( quotient_rings_test.all_suites )


#- Fields --------------------------------------------------------------------- 
from . import finite_fields_test
all_suites.extend( finite_fields_test.all_suites )

from . import fraction_fields_test
all_suites.extend( fraction_fields_test.all_suites )


#- Elliptic Curves------------------------------------------------------------- 
from . import elliptic_curves_group_test
all_suites.extend( elliptic_curves_group_test.all_suites )


#- Support --------------------------------------------------------------------
from . import support_test
all_suites.extend( support_test.all_suites ) 


#- Algorithms -----------------------------------------------------------------
from . import algorithm_test
all_suites.extend( algorithm_test.all_suites )

#===============================================================================
# Run all tests
#===============================================================================
all_tests = unittest.TestSuite( all_suites )
unittest.TextTestRunner().run( all_tests )
