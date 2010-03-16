# -*- coding: utf-8 -*-
# $Id$

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
import os.path
import pstats
import sys

from callgraph import CallGraph
from contextlib import closing

def main(arguments):
    usage_string = "%prog <profile_file_path>"
    parser = optparse.OptionParser( usage=usage_string )
    
    parser.add_option(  "-o",
                        "--output-name",
                        metavar="FILE",
                        dest="output_name",
                        help="Write output to FILE instead of "
                        "callgrind.out.INPUT_FILE",
                        default=None
                    )
    
    options, arguments = parser.parse_args( arguments )
    
    if len( arguments ) != 1:
        parser.print_usage()
        return 2
    
    profile_name = arguments[ 0 ]
    
    if not options.output_name:
        file_name = "callgrind.out.{0}".format( os.path.basename( profile_name ) )
        directory = os.path.dirname( profile_name )
        options.output_name = os.path.join( directory, file_name ) 
        
    if os.path.exists( options.output_name ):
        message = "ERROR: Output file '{0}' already exists. Aborting."
        print( message.format( options.output_name ), file=sys.stderr )
        return 1
    
    try:
        stats = pstats.Stats( profile_name )
    except IOError as error:
        message = "ERROR: Could not open profile file.\nReason: {0}"
        print( message.format( error ), file=sys.stderr )
        return 1
         
    callgraph = CallGraph( stats )
    
    try:    
        with closing( open( options.output_name, "wt" ) ) as output:
            callgrind_profile = CallgrindProfile( callgraph )
            callgrind_profile.dump( output )

            return 0
    
    except IOError as error:
        message = "ERROR: Could not store the output.\nReason: {0}"
        print( message.format( error ), file=sys.stderr )
        return 1


if __name__ == '__main__':
    sys.exit( main( sys.argv[ 1: ] ) )
