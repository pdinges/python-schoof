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


# Docstrings will be empty if optimization (-OO command line flag) is enabled.
# However, the description has to be available regardless of this.  Thus put
# it in an extra variable.
__description = \
"""
Convert execution profile dumps generated with the cProfile module to a file
in the Callgrind format (typically named 'callgrind.out...').

The Callgrind format is widely supported in profiling tools.  For example,
the excellent profile inspection tool KCacheGrind supports Callgrind files.

This script accepts several profile dumps as input and allows some aggregation
and grouping of the data. 
"""
__doc__ = __description


import callgraph_operations 
from contextlib import closing
import sys

def main(arguments):
    options, arguments = parse_arguments( arguments )
    
    output = get_output( arguments[0], options )
    callgraph = get_callgraph( arguments )
    
    #- Merge ------------------------------------------------------------------ 
    if not options.preserve_wrappers:
        callgraph_operations.merge_casting_wrappers( callgraph )
    
    if options.merge_divpolys:
        callgraph_operations.merge_by_division_polynomials( callgraph )
    
    if options.merge_fields:
        callgraph_operations.merge_by_fields( callgraph )
    
    #- Output -----------------------------------------------------------------
    try:    
        with closing( output ):
            callgrind_profile = CallgrindProfile( callgraph )
            callgrind_profile.dump( output )

            sys.exit(0)
    
    except IOError as error:
        message = "ERROR: Could not store the output.\nReason: {0}"
        print( message.format( error ), file=sys.stderr )
        sys.exit(1)


from functools import reduce

class CallgrindProfile:
    """
    A callgrind profile generated from a callgraph.CallGraph.
    
    See "Callgrind Format Specification" in the Valgrind documentation at
    http://www.valgrind.org/docs/manual/cl-format.html  (Jan. 26, 2010)
    
    Inspired by the 'lsprofcalltree.py' script by David Allouche et al.
    """
    def __init__(self, callgraph):
        self.__callgraph = callgraph
    
    
    def dump(self, file):
        print( "events: Ticks", file=file )
        self._print_summary( file )
        
        for function in self.__callgraph:
            self._print_function( function, file )
        
        
    def _print_summary(self, file):
        total_time = int( self.__callgraph.total_time() * 1000 )
        print( "summary: {0:d}".format( total_time ), file=file )
        
        
    def _print_function(self, function, file):
        print( "fi={0:s}".format( function.filename() ), file=file )
        print( "fn={0:s}".format( self._absolute_name( function ) ), file=file )
        
        inline_time = int( function.inline_time() * 1000 )
        cost_data = ( function.line_number(), inline_time )
        print( "{0:d} {1:d}".format( *cost_data ), file=file)
        
        for call in function.outgoing_calls():
            self._print_call( call, file )

            
    def _print_call(self, call, file):
        callee = call.callee()
        print( "cfn={0:s}".format( self._absolute_name( callee ) ), file=file )
        print( "cfi={0:s}".format( callee.filename() ), file=file )
        
        calls_data = ( call.total_callcount(), callee.line_number() )
        print( "calls={0:d} {1:d}".format( *calls_data ), file=file )
        
        cumulative_time = int( call.cumulative_time() * 1000 )
        cost_data = ( call.caller().line_number(), cumulative_time )
        print( "{0:d} {1:d}".format( *cost_data ), file=file )
    
    @staticmethod
    def _absolute_name(function):
        if function.namespace():
            return "{0:s}::{1:s}".format( function.namespace(), function.name() )
        else:
            return function.name()


import optparse

def parse_arguments( arguments ):
    usage_string = "%prog <list_of_profile_file_paths>"
    parser = optparse.OptionParser(
                               usage=usage_string,
                               description=__description.strip()
                           )
    
    parser.add_option(  "-o",
                        "--output-name",
                        dest="output_name",
                        default=None,
                        metavar="FILE",
                        help="Write output to FILE instead of "
                        "callgrind.out.FIRST_INPUT_FILE  Use '-' to have the"
                        "output written to the terminal (stdout)."
                   )
    
    parser.add_option(  "-w",
                        "--overwrite",
                        dest="overwrite",
                        action="store_true",
                        default=False,
                        help="Overwrite the output file if it already exists."
                   )

    parser.add_option( "-c",
                       "--preserve-wrappers",
                       dest="preserve_wrappers",
                       action="store_true",
                       default=False,
                       help="Preserve casting wrappers instead of merging "
                       "them with the wrapped function"
                   )
    parser.add_option( "-d",
                       "--merge-division-polynomials",
                       dest="merge_divpolys",
                       action="store_true",
                       default=False,
                       help="Merge namespaces with division polynomials into "
                       "a generic namespace"
                   )
    parser.add_option( "-f",
                       "--merge-fields",
                       dest="merge_fields",
                       action="store_true",
                       default=False,
                       help="Merge namespaces of fields with different element "
                       "count into a generic namespace"
                   )
    
    options, arguments = parser.parse_args( arguments )

    if len( arguments ) < 1:
        parser.print_usage()
        sys.exit(2)
    
    return options, arguments


import os.path
import sys

def get_output( first_profile_name, options ):
    if options.output_name == "-":
        return sys.stdout
        
    elif not options.output_name:
        base_name = os.path.splitext( os.path.basename( first_profile_name ) )[0]
        file_name = "callgrind.out.{0}".format( base_name )
        directory = os.path.dirname( first_profile_name )
        options.output_name = os.path.join( directory, file_name) 
        
    if not options.overwrite and os.path.exists( options.output_name ):
        message = "ERROR: Output file '{0}' already exists. Aborting."
        print( message.format( options.output_name ), file=sys.stderr )
        sys.exit(1)
    
    return open( options.output_name, "wt" )


import callgraph
import pstats
import sys

def get_callgraph( profile_names ):
    callgraph_ = callgraph.CallGraph()
    
    for profile_name in profile_names:
        try:
            stats = pstats.Stats( profile_name )
            callgraph_.add( stats )
        except IOError as error:
            message = "ERROR: Could not open profile file.\nReason: {0}"
            print( message.format( error), file=sys.stderr )
            sys.exit(1)
    
    return callgraph_


if __name__ == '__main__':
    main( sys.argv[ 1: ] )
