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

import cProfile
import pstats

import callgraph

class CallGraphTest(unittest.TestCase):
    """Test cases for CallGraph and the related classes Function and Call"""
    
    def setUp(self):
        """Provide a callgraph for a known execution profile""" 
        self._stats = pstats.Stats( self._generate_profile() )
        self._callgraph = callgraph.CallGraph( self._stats )
        
        # Index for getting the (filename, line number, name) triple by name.
        self._name_to_fln = {}
        for fln in self._stats.stats.keys():
            self._name_to_fln[ fln[2] ] = fln


    #- Node Retrieval ---------------------------------------------------------
    def test_complete_iteration(self):
        """Iterate over all functions"""
        callgraph_functions = set( [
            (f.filename(), f.line_number(), f.name()) for f in self._callgraph
         ] )
        self.assert_( callgraph_functions == set( self._stats.stats.keys() ) )
        
    def test_fln_index(self):
        """Function access by (filename, line number, name) triple"""
        for fln in self._name_to_fln.values():
            self.assert_( self._callgraph.function( fln ) ) 


    #- Adding and Removing Nodes ---------------------------------------------- 
    
    # TODO Add test cases for adding nodes.
    
    def test_add_stats_adds_times(self):
        """Adding other pstats.Stats adds times"""
        # Sample some data
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        
        f_itime = function_f.inline_time()
        f_ctime = function_f.cumulative_time()
        k_itime = function_k.inline_time()
        k_ctime = function_k.cumulative_time()
        
        self._callgraph.add( self._stats )
        
        self.assertAlmostEqual( function_f.inline_time(), 2 * f_itime )
        self.assertAlmostEqual( function_f.cumulative_time(), 2 * f_ctime )
        self.assertAlmostEqual( function_k.inline_time(), 2 * k_itime )
        self.assertAlmostEqual( function_k.cumulative_time(), 2 * k_ctime )
    
    def test_add_stats_adds_callcounts(self):
        """Adding other pstats.Stats adds call counts"""
        # Sample some data
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        
        f_pccount = function_f.primitive_callcount()
        f_tccount = function_f.total_callcount()
        k_pccount = function_k.primitive_callcount()
        k_tccount = function_k.total_callcount()
        
        self._callgraph.add( self._stats )
        
        self.assert_( function_f.primitive_callcount() == 2 * f_pccount )
        self.assert_( function_f.total_callcount() == 2 * f_tccount )
        self.assert_( function_k.primitive_callcount() == 2 * k_pccount )
        self.assert_( function_k.total_callcount() == 2 * k_tccount )
    
    def test_add_calls_merges(self):
        """Adding parallel Calls"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        
        # The profile of the added call is arbitrary and of no importance.
        self._callgraph._add_call( function_f, function_g, 2, 2, 0.1, 0.1 )
        
        self.assert_( len( function_f.outgoing_calls() ) == 1 )
        self.assert_( len( function_g.incoming_calls() ) == 1 )
        
    
    def test_remove_calls(self):
        """Remove Calls"""
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        calls = function_k.incoming_calls().copy()
        callers = [ c.caller() for c in calls ]
        
        for call in calls:
            self._callgraph._remove_call( call )
        
        self.assert_( not function_k.incoming_calls() )
        for caller in callers:
            self.assert_( not calls.intersection( caller.outgoing_calls() ) )

    def test_remove_function(self):
        """Remove Functions"""
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        self._callgraph._remove_function( function_k )
        self.assert_( function_k not in self._callgraph )

    
    #- Nodes in General -------------------------------------------------------
    
    # TODO Add test cases for CallGraphNode objects.
    
    
    #- Function Nodes ---------------------------------------------------------
    
    # TODO Add test cases for Function nodes.
    
    
    #- Call Nodes -------------------------------------------------------------
    
    # TODO Add test cases for Call nodes.


    #- Namespaces -------------------------------------------------------------
    def test_namespace_global_only(self):
        """Namespaces: have global namespace only"""
        self.assert_( list( self._callgraph.namespaces() ) == [""] )
        
    def test_namespace_global_functions(self):
        """Namespaces: list of functions in global namespace"""
        stats_functions = [ fln[2] for fln in self._stats.stats.keys() ]
        callgraph_functions = [ f.name() for f in self._callgraph.namespace("") ]
        self.assert_( set( stats_functions ) == set( callgraph_functions ) )
    
    # TODO Add test cases for functions in proper namespaces.
    
    
    #- Properties of the Complete Profile ------------------------------------- 
    def test_total_time(self):
        """Calculate total execution time"""
        self.assertAlmostEqual( self._callgraph.total_time(), self._stats.total_tt )


    #- Function Operation: Treating as Built-In -------------------------------
    def test_builtin_removes_function(self):
        """Treating functions as built-in removes them from the graph"""
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        self._callgraph.treat_as_builtin( function_l )
        self.assert_( function_l not in self._callgraph )

    def test_builtin_removes_outgoing_calls(self):
        """Treating functions as built-in removes calls from callers"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        
        l_callees = set( function_l.callees() )
        
        self._callgraph.treat_as_builtin( function_l )
        
        self.assert_( function_l not in function_h.callees() )
        self.assert_( not l_callees.intersection( function_h.callees() ) )
        self.assert_( function_l not in function_k.callees() )
        self.assert_( not l_callees.intersection( function_k.callees() ) )

    def test_builtin_adds_inline_times(self):
        """Treating functions as built-in adds execution time to callers"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        
        h_itime = function_h.inline_time()
        k_itime = function_k.inline_time()
        # We know there is only one outgoing call; see _generate_profile()
        # This is the cumulative execution for calls of l() by h() and k()
        hl_ctime = list( function_h.outgoing_calls() )[0].cumulative_time()
        kl_ctime = list( function_k.outgoing_calls() )[0].cumulative_time()
        
        self._callgraph.treat_as_builtin( function_l )
        
        self.assertAlmostEqual( function_h.inline_time(), h_itime + hl_ctime )
        self.assertAlmostEqual( function_k.inline_time(), k_itime + kl_ctime )

    def test_builtin_preserves_cumulative_times(self):
        """Treating functions as built-in preserves cumulative times"""
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        
        k_ctime = function_k.cumulative_time()
        
        self._callgraph.treat_as_builtin( function_l )
        
        self.assert_( function_k.cumulative_time() == k_ctime )

    def test_builtin_preserves_caller_callcounts(self):
        """Treating functions as built-in preserves call counts of callers"""
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        
        k_pccount = function_k.primitive_callcount()
        k_tccount = function_k.total_callcount()
        
        self._callgraph.treat_as_builtin( function_l )
        
        self.assert_( function_k.primitive_callcount() == k_pccount )
        self.assert_( function_k.total_callcount() == k_tccount )

    def test_builtin_preserves_callee_callcounts(self):
        """Treating functions as built-in preserves call counts of callees"""
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        
        l_pccount = function_l.primitive_callcount()
        l_tccount = function_l.total_callcount()
        
        self._callgraph.treat_as_builtin( function_k )
        
        self.assert_( function_l.primitive_callcount() == l_pccount )
        self.assert_( function_l.total_callcount() == l_tccount )
    
    
    #- Function Operation: Treating as Inlined --------------------------------
    def test_inline_removes_function(self):
        """Treating functions as inlined removes them from the graph"""
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        self._callgraph.treat_as_inlined( function_g )
        self.assert_( function_g not in self._callgraph )
    
    def test_inline_removes_incoming_calls(self):
        """Treating functions as inlined removes their incoming calls"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        icalls = function_g.incoming_calls().copy()
        
        self._callgraph.treat_as_inlined( function_g )
        
        self.assert_( not icalls.intersection( function_f.outgoing_calls() ) )

    def test_inline_merges_outgoing_calls(self):
        """Treating functions as inlined merges their outgoing calls"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        g_callees = set( function_g.callees() )
        
        self._callgraph.treat_as_inlined( function_g )
        
        self.assert_( g_callees.issubset( function_f.callees() ) )
    
    def test_inline_preserves_callcounts(self):
        """Treating functions as inlined preserves the call counts"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )

        f_pcalls = function_f.primitive_callcount()
        f_tcalls = function_f.total_callcount()

        self._callgraph.treat_as_inlined( function_g )
        
        self.assert_( function_f.primitive_callcount() == f_pcalls )
        self.assert_( function_f.total_callcount() == f_tcalls )
    
    def test_inline_preserves_times(self):
        """Treating functions as inlined preserves the timings"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        
        f_itime = function_f.inline_time()
        f_ctime = function_f.cumulative_time()
        # We know there is only one outgoing call; see _generate_profile()
        # This is the inline execution for calls of g() by f()  
        fg_itime = list( function_f.outgoing_calls() )[0].inline_time()
        
        self._callgraph.treat_as_inlined( function_g )

        self.assertAlmostEqual( function_f.inline_time(), f_itime + fg_itime )
        self.assertAlmostEqual( function_f.cumulative_time(), f_ctime )


    #- Function Operation: Treating as Same -----------------------------------
    def test_merge_removes_functions(self):
        """Merging functions removes them from the call graph"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        
        self._callgraph.treat_as_same( function_h, function_k )
        
        self.assert_( function_h not in self._callgraph )
        self.assert_( function_k not in self._callgraph )
        
    def test_merge_adds_function(self):
        """Merging functions adds a new function"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        merged = self._callgraph.treat_as_same( function_h, function_k )
        self.assert_( merged in self._callgraph )
    
    def test_merge_unifies_incoming_calls(self):
        """Merging functions unifies their incoming calls"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        
        merged = self._callgraph.treat_as_same( function_h, function_k )
        
        self.assert_( len( function_l.callers() ) == 1 )
        self.assert_( function_l.callers().pop() == merged )
    
    def test_merge_unifies_outgoing_calls(self):
        """Merging functions unifies their outgoing calls"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        function_l = self._callgraph.function( self._name_to_fln["l"] )
        
        merged = self._callgraph.treat_as_same( function_h, function_k )
        
        self.assert_( len( merged.callees() ) == 1 )
        self.assert_( merged.callees().pop() == function_l )
    
    def test_merge_adds_inline_times(self):
        """Merging functions adds up their inline execution times"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        
        h_itime = function_h.inline_time()
        k_itime = function_k.inline_time()

        merged = self._callgraph.treat_as_same( function_h, function_k )

        self.assertAlmostEqual( merged.inline_time(), h_itime + k_itime )
    
    def test_merge_adds_inline_offsets(self):
        """Merging functions adds up their inline execution time offsets"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        
        f_itime = function_f.inline_time()
        g_itime = function_g.inline_time()

        merged = self._callgraph.treat_as_same( function_f, function_g )

        self.assertAlmostEqual( merged.inline_time(), f_itime + g_itime )
    
    def test_merge_adds_cumulative_times(self):
        """Merging functions adds up their cumulative execution times"""
        function_h = self._callgraph.function( self._name_to_fln["h"] )
        function_k = self._callgraph.function( self._name_to_fln["k"] )
        
        h_ctime = function_h.cumulative_time()
        k_ctime = function_k.cumulative_time()

        merged = self._callgraph.treat_as_same( function_h, function_k )

        self.assertAlmostEqual( merged.cumulative_time(), h_ctime + k_ctime )

    def test_merge_adds_primitive_callcount_offsets(self):
        """Merging functions adds up their primitive call count offsets"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        
        f_pccount = function_f.primitive_callcount()
        g_pccount = function_g.primitive_callcount()

        merged = self._callgraph.treat_as_same( function_f, function_g )

        self.assert_( merged.primitive_callcount() == f_pccount + g_pccount )
    
    def test_merge_adds_total_callcount_offsets(self):
        """Merging functions adds up their total call count offsets"""
        function_f = self._callgraph.function( self._name_to_fln["f"] )
        function_g = self._callgraph.function( self._name_to_fln["g"] )
        
        f_tccount = function_f.total_callcount()
        g_tccount = function_g.total_callcount()

        merged = self._callgraph.treat_as_same( function_f, function_g )

        self.assert_( merged.total_callcount() == f_tccount + g_tccount )
    
     
    #- Auxiliary Methods for the Test Cases -----------------------------------
    def _generate_profile(self):
        """
        Generate a small profile with known call structure:
        f -> g --> h --> l
               |-> k -| 
        """
        try:
            return self.__profile
        
        except AttributeError:
            pass
        
        def f():
            # Spend some time.
            r = 0
            for i in range(0, 5000):
                r += i
            g()
        
        def g():
            # Spend some time.
            r = 0
            for i in range(0, 5000):
                r += i
            h()
            k()
        
        def h():
            # Spend some time.
            r = 0
            for i in range(0, 5000):
                r += i
            l()
        
        def k():
            # Spend some time.
            r = 0
            for i in range(0, 5000):
                r += i
            l()
        
        def l():
            # Spend some time.
            r = 0
            for i in range(0, 5000):
                r += i
        
        # Run the profiler on f()
        profile = cProfile.Profile()
        profile.enable( builtins = False )
        f()
        profile.disable()
        
        self.__profile = profile
        return profile
        

if __name__ == "__main__":
    unittest.main()
