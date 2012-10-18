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
r"""
Create a table of the most expensive functions in execution profile dumps
generated with the cProfile module.  The output is in LaTeX table format:
columns separated with '&', rows separated with '\\'.  It has four columns:
cumulative time, inline time, function name, function description.  The script    
uses the cumulative time as primary sort key; the inline time is the secondary
sort key.  

This script accepts several profile dumps as input and allows some aggregation,
grouping, and pruning of the data. 
"""
__doc__ = __description


import callgraph_operations 
from contextlib import closing
from datetime import datetime
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
    
    #- Prune ------------------------------------------------------------------
    if options.threshold:
        callgraph_operations.apply_threshold( callgraph, options.threshold / 100 )
    
    #- Print ------------------------------------------------------------------
    try:
        with closing( output ):
            header = "%% Table of the {limit} most expensive functions " \
                     "(first sort key: cumulative time; second key: inline time)\n" \
                     "%% Cost threshold: {threshold}%\n" \
                     "%% Merged: {merged}\n" \
                     "%% Generated on {date} from:\n" \
                     "%% {input}"
            merge_options = [
                           (options.preserve_wrappers, "preserved casting wrappers"),
                           (options.merge_divpolys, "division polynomials namespaces"),
                           (options.merge_fields, "fields namespaces" )
                       ]
            header = header.format(
                               limit = options.limit,
                               threshold = int( options.threshold ),
                               merged = ", ".join( [ m[1] for m in merge_options if m[0] ] ),
                               date = datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                               input = "\n%% ".join( arguments ), 
                           )
            print( header, file=output )
            
            functions = sorted( callgraph, key=function_sort_key, reverse=True )
            rows = [ prepare_row( f, callgraph.total_time() )
                       for f in functions[ : options.limit ] ]
            
            # Sort again to prevent (seemingly) wrong order
            # from rounding to the same value
            for row in sorted( rows, reverse=True ):
                print( format_row( row ), file=output )

        sys.exit(0)
    
    except IOError as error:
        message = "ERROR: Could not store the output.\nReason: {0}"
        print( message.format( error), file=sys.stderr )
        sys.exit(1)


import optparse
import sys

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
                        "FIRST_INPUT_FILE.tex  Use '-' to have the output "
                        "written to the terminal (stdout)."
                   )
    
    parser.add_option(  "-w",
                        "--overwrite",
                        dest="overwrite",
                        action="store_true",
                        default=False,
                        help="Overwrite the output file if it already exists."
                   )
    
    parser.add_option( "-t",
                       "--threshold",
                       dest="threshold",
                       type="int",
                       default=2,
                       metavar="PERCENT",
                       help="Ignore all functions with less than PERCENT "
                       "part in the total execution time"
                   )
    parser.add_option( "-l",
                       "--limit",
                       dest="limit",
                       type="int",
                       default=15,
                       metavar="NUMBER",
                       help="Return the top NUMBER functions" 
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
        file_name = "{0}.tex".format( base_name )
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


def function_sort_key( function ):
    # TODO Use locale.strxform() to have locale aware string keys
    return ( function.cumulative_time(),
             function.inline_time(),
             function.namespace().lower(),
             function.name().lower()
         )


import callgraph_operations 

def prepare_row( function, total_time ):
    total_percent = int( round( 100 * function.cumulative_time() / total_time ) )
    inline_percent = int( round( 100 * function.inline_time() / total_time ) )
    name =  callgraph_operations.tex_name( function )
    description = callgraph_operations.tex_description( function )

    return ( total_percent, inline_percent, name, description )


def format_row( row ):
    if row[3]:
        return r"{0} & {1} & !{2}! \hfill\hbox{{\hskip 1.5em ({3})}} \\".format( *row )
    else:
        return r"{0} & {1} & !{2}! \\".format( *row )


if __name__ == '__main__':
    main( sys.argv[ 1: ] )
