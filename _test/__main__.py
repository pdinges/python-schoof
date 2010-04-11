# -*- coding: utf-8 -*-
# $Id$

import unittest

all_suites = []

#===============================================================================
# Collect all test suites 
#===============================================================================

#- Rings ---------------------------------------------------------------------- 
from . import polynomial_rings_test
all_suites.extend( polynomial_rings_test.all_suites )


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


#===============================================================================
# Run all tests
#===============================================================================
all_tests = unittest.TestSuite( all_suites )
unittest.TextTestRunner().run( all_tests )
