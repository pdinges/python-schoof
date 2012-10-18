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


__description = \
"""
Generate a list of random parameters of non-singular elliptic curves
over the finite fields with @c p elements. The primes @c p are computed from
pairs "n, k" as p = 2^n - k; the pairs are read one per line from the given
input file.
"""
__doc__ = __description


def non_singular(p, A, B):
    """
    Test whether the elliptic curve with parameters @p A and @p B is
    non-singular over the finite field with @p p elements.
    """
    assert p > 3, \
        "discriminant test for non-singular curves requires characteristic > 3" 
    return (4 * A**3  +  27 * B**2) % p != 0


import random

def generate_parameters(p, number):
    """
    Return a set of @p number parameter pairs @c (A,B) of non-singular
    elliptic curves over the finite field with @p p elements. 
    """
    parameters = set()
    
    # Too many pairs to guess and test; use systematic approach
    if number > 0.8 * (p**2 - 1):
        pairs = [ (i, j) for i in range(0, p) for j in range(0, p) ]
        
        while pairs and len( parameters ) < number:
            index = random.randrange( 0, len(pairs) )
            A, B = pairs[ index ]
            del pairs[ index ]
            if non_singular(p, A, B):
                parameters.add( (A, B) )
                
        if len( parameters ) < number:
            warning = "WARNING: Could find only {n} parameter pairs for p = {p}"
            print( warning.format( n=len( parameters ), p=p ), file=sys.stderr )
    
    else:
        while len( parameters ) < number:
            A = random.randrange(0, p)
            B = random.randrange(0, p)
            if (A, B) not in parameters and non_singular(p, A, B):
                parameters.add( (A, B) )

    return parameters


import optparse
import os.path
import sys

from contextlib import closing

def main(arguments):
    usage_string = "%prog <primes_list>"
    parser = optparse.OptionParser(
                               usage=usage_string,
                               description=__description.strip()
                           )
    
    parser.add_option(  "-o",
                        "--output-name",
                        metavar="FILE",
                        dest="output_name",
                        help="Write output to FILE instead of console",
                        default=None
                    )
    
    parser.add_option(  "-n",
                        "--curves-per-prime",
                        metavar="N",
                        dest="curves_per_prime",
                        help="Generate N sets of curve parameters per prime",
                        default=11
                    )
    
    options, arguments = parser.parse_args( arguments )
    
    if len( arguments ) != 1:
        parser.print_usage()
        return 2
    
    primes_list_name = arguments[ 0 ]
    
    if options.output_name and os.path.exists( options.output_name ):
        message = "ERROR: Output file '{0}' already exists. Aborting."
        print( message.format( options.output_name ), file=sys.stderr )
        return 1
    
    try:
        primes_list = open( primes_list_name, "rt" )
    
    except IOError as error:
        message = "ERROR: Could not open primes list.\nReason: {0}"
        print( message.format( error ), file=sys.stderr )
        return 1
    

    if options.output_name:
        try:
            output_file = open( options.output_name, "wt" )
        except IOError as error:
            message = "ERROR: Could not store the output.\nReason: {0}"
            print( message.format( error ), file=sys.stderr )
            return 1
    else:
        output_file = sys.stdout
            
    
    with closing( output_file ) as output:
        for line in primes_list:
            # Ignore empty lines and comments (starting with #)
            if not line.strip() or line.strip().startswith("#"):
                continue
            n, k = map( int, line.split(",") )
            p = 2**n - k
            
            parameters = generate_parameters( p, int(options.curves_per_prime) )
            
            comment = "# {n}-bit prime {p} = 2^{n} - {k}".format( n=n, k=k, p=p )
            print( comment, file=output )
            
            for A, B in parameters:
                print(p, A, B, file=output)
            print( file=output )

        return 0


if __name__ == '__main__':
    sys.exit( main( sys.argv[ 1: ] ) )
