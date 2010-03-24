# -*- coding: utf-8 -*-
# $Id$

class DotCallgraph:
    def __init__(self, callgraph):
        self.__callgraph = callgraph

    def dump(self, file):
        print( "digraph callgraph {", file=file )
        print( "node [shape = box];", file=file )

        for i, namespace in enumerate( self.__callgraph.namespaces() ):
            print( "subgraph cluster_namespace{0} {{".format( i ), file=file )
            print( "label = \"{0}\";".format( namespace ), file=file )
            for function in self.__callgraph.namespace( namespace ):
                self._print_node( function, file )
            print( "}", file=file )
            print( file=file )

        print( file=file )
        for function in self.__callgraph:
            self._print_calls( function, file )
        
        print( "}", file=file )
        
    def _print_node(self, function, file):
        node_string = "{id} [label = \"{label}\"]".format(
                               id = id(function),
                               label = function.name()
                           ) 
        print( node_string, file=file )
    
    def _print_calls(self, function, file):
        for call in function.outgoing_calls():
            edge_string = "\"{caller}\":s -> \"{callee}\":n;".format(
                              caller = id( call.caller() ),
                              callee = id( call.callee() )
                          )
            print( edge_string, file=file ) 
    

import optparse
import os.path
import pstats
import sys

from callgraph import CallGraph, Call
from contextlib import closing

def main(arguments):
    usage_string = "%prog <list_of_profile_file_path>"
    parser = optparse.OptionParser( usage=usage_string )
    
    parser.add_option(  "-o",
                        "--output-name",
                        metavar="FILE",
                        dest="output_name",
                        help="Write output to FILE instead of "
                        "FIRST_INPUT_FILE.dot",
                        default=None
                    )
    
    options, arguments = parser.parse_args( arguments )
    
    if len( arguments ) < 1:
        parser.print_usage()
        return 2
    
    first_profile_name = arguments[ 0 ]
    
    if not options.output_name:
        base_name = os.path.splitext( os.path.basename( first_profile_name ) )[0]
        file_name = "{0}.dot".format( base_name )
        directory = os.path.dirname( first_profile_name )
        options.output_name = os.path.join( directory, file_name) 
        
    if os.path.exists( options.output_name ):
        message = "ERROR: Output file '{0}' already exists. Aborting."
        print( message.format( options.output_name ), file=sys.stderr )
        return 1
    
    callgraph = CallGraph()
    
    for profile_name in arguments:
        try:
            stats = pstats.Stats( profile_name )
            callgraph.add( stats )
        except IOError as error:
            message = "ERROR: Could not open profile file.\nReason: {0}"
            print( message.format( error), file=sys.stderr )
            return 1
         
    
    # TODO Make these steps functions and move them closer to CallGraph.
    # Merge wrappers and wrapped functions
    wrapper_functions = [ f for f in callgraph if f.name().endswith("_casting_wrapper") ]
    for wrapper in wrapper_functions:
        wrapped_function_name = wrapper.name()[: -len("_casting_wrapper") ]
        for call in wrapper.outgoing_calls():
            if call.callee().name() == wrapped_function_name:
                wrapped_function = call.callee()
                break
        assert( wrapped_function )
        callgraph.treat_as_inlined( wrapped_function )
        del wrapped_function
    
    # Prune functions with less than 2% cost. 
    threshold = int( 0.02 * callgraph.total_time() )
    insignificant_functions = [ f for f in callgraph if f.cumulative_time() < threshold ]
    for function in insignificant_functions:
        callgraph.treat_as_builtin( function )
        assert( not function.valid() )

    
    try:    
        with closing( open( options.output_name, "wt" ) ) as output:
            dot_callgraph = DotCallgraph( callgraph  )
            dot_callgraph.dump( output )

            return 0
    
    except IOError as error:
        message = "ERROR: Could not store the output.\nReason: {0}"
        print( message.format( error), file=sys.stderr )
        return 1


if __name__ == '__main__':
    sys.exit( main( sys.argv[ 1: ] ) )
