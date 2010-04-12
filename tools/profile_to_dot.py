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
import sys

def parse_arguments( arguments ):
    usage_string = "%prog <list_of_profile_file_path>"
    parser = optparse.OptionParser( usage=usage_string )
    
    parser.add_option(  "-o",
                        "--output-name",
                        dest="output_name",
                        default=None,
                        metavar="FILE",
                        help="Write output to FILE instead of "
                        "FIRST_INPUT_FILE.dot"
                   )
    parser.add_option( "-t",
                       "--threshold",
                       dest="threshold",
                       type="float",
                       default=0.02,
                       metavar="PERCENT",
                       help="Ignore all functions with less than PERCENT "
                       "part in the total execution time"
                   )
    
    parser.add_option( "-w",
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
        file_name = "{0}.tex".format( base_name )
        directory = os.path.dirname( first_profile_name )
        options.output_name = os.path.join( directory, file_name) 
        
    if os.path.exists( options.output_name ):
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


import sys
import callgraph_operations 
from datetime import datetime
from callgraph import CallGraph
from contextlib import closing

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
    
    #- Prune ------------------------------------------------------------------
    if options.threshold:
        callgraph_operations.apply_threshold( callgraph, options.threshold )
    
    #- Print ------------------------------------------------------------------
    try:
        with closing( output ):
            header = "// Call Graph with\n" \
                     "// Cost threshold: {threshold}%\n" \
                     "// Merged: {merged}\n" \
                     "// Generated on {date} from:\n" \
                     "// {input}"
            merge_options = [
                           (options.preserve_wrappers, "preserved casting wrappers"),
                           (options.merge_divpolys, "division polynomials namespaces"),
                           (options.merge_fields, "fields namespaces" )
                       ]
            header = header.format(
                               threshold = int( options.threshold * 100 ),
                               merged = ", ".join( [ m[1] for m in merge_options if m[0] ] ),
                               date = datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                               input = "\n// ".join( arguments ), 
                           )
            print( header, file=output )

            dot_callgraph = DotCallgraph( callgraph  )
            dot_callgraph.dump( output )

            sys.exit(0)
    
    except IOError as error:
        message = "ERROR: Could not store the output.\nReason: {0}"
        print( message.format( error), file=sys.stderr )
        sys.exit(1)


if __name__ == '__main__':
    main( sys.argv[ 1: ] )
