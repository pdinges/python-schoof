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


def merge_casting_wrappers( callgraph ):
    """Merge wrappers and wrapped functions"""
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


def apply_threshold( callgraph, threshold ):
    """Prune functions with less than @p threshold percent total cost""" 
    threshold = int( threshold * callgraph.total_time() )
    insignificant_functions = [ f for f in callgraph if f.cumulative_time() < threshold ]
    for function in insignificant_functions:
        callgraph.treat_as_builtin( function )
        assert( not function.valid() )


import re

def merge_by_division_polynomials( callgraph ):
    """
    Merge all namespaces containing specific division polynomials
    into one generic namespace.
    
    For example, 'psi[3]' and 'psi[7]' will be unified into 'psi[l]'.
    """ 
    division_polynomial_namespaces = [
            ( "^E<Q<E<GF<{q}>>\[x,y\]/psi\[(?P<l>[l0-9]+)\]>>$",
              "E<Q<E<GF<{q}>>[x,y]/psi[l]>>" ),
              
            ( "^Q<E<GF<{q}>>\[x,y\]/psi\[(?P<l>[l0-9]+)\]>$",
              "Q<E<GF<{q}>>[x,y]/psi[l]>" ),
              
            ( "^E<GF<{q}>>\[x,y\]/psi\[(?P<l>[l0-9]+)\]$",
              "E<GF<{q}>>[x,y]/psi[l]" ),
       ]
    
    # Compile a list of all occurring fields
    fields_re = re.compile( "GF<(?P<q>[q0-9]+)>" )
    fields = set()
    for namespace in callgraph.namespaces():
        m = fields_re.search( namespace )
        if m:
            fields.add( m.groupdict()[ "q" ] )
    
    # Merge division polynomials grouped by underlying fields
    for q in fields:
        for namespace_re, merged_namespace in division_polynomial_namespaces:
            namespace_re = namespace_re.format( q = q )
            merged_namespace = merged_namespace.format( q = q )
            callgraph.merge_namespaces( namespace_re, merged_namespace )


import re

def merge_by_fields( callgraph ):
    """
    Merge all namespaces containing specific finite fields
    into one generic namespace.
    
    For example, 'GF<3>[x]' and 'GF<5>[x]' will be unified into 'GF<q>[x]'.
    """ 
    field_namespaces_with_divpoly = [
            ( "^E<Q<E<GF<(?P<q>[q0-9]+)>>\[x,y\]/psi\[{l}\]>>$",
              "E<Q<E<GF<q>>[x,y]/psi[{l}]>>" ),
              
            ( "^Q<E<GF<(?P<q>[q0-9]+)>>\[x,y\]/psi\[{l}\]>$",
              "Q<E<GF<q>>[x,y]/psi[{l}]>" ),
              
            ( "^E<GF<(?P<q>[q0-9]+)>>\[x,y\]/psi\[{l}\]$",
              "E<GF<q>>[x,y]/psi[{l}]" ),
       ]
    field_namespaces = [
            ( "^E<GF<(?P<q>[q0-9]+)>>\[x,y\]$",
              "E<GF<q>>[x,y]" ),
              
            ( "^GF<(?P<q>[q0-9]+)>\[x\]$",
              "GF<q>[x]" ),
              
            ( "^GF<(?P<q>[q0-9]+)>$",
              "GF<q>" ),
       ]
    
    # Compile a list of all occuring division polynomials
    divpoly_re = re.compile( "psi\[(?P<l>[l0-9]+)\]" )
    divpolys = set()
    for namespace in callgraph.namespaces():
        m = divpoly_re.search( namespace )
        if m:
            divpolys.add( m.groupdict()[ "l" ] )

    # Merge fields grouped by division polynomials
    for l in divpolys:
        for namespace_re, merged_namespace in field_namespaces_with_divpoly:
            namespace_re = namespace_re.format( l = l )
            merged_namespace = merged_namespace.format( l = l )
            callgraph.merge_namespaces( namespace_re, merged_namespace )
            
    for namespace_re, merged_namespace in field_namespaces:
        callgraph.merge_namespaces( namespace_re, merged_namespace )


def plain_name( function ):
    """
    Return the @p function name, free from clutter such as wrapper postfixes.
    """
    if function.name().endswith( "_casting_wrapper" ):
        return function.name()[ : -len("_casting_wrapper") ]
    
    return function.name()


def tex_name( function ):
    """Return the @p function name as it should appear in the thesis."""
    if function.namespace():
        return "{0}::{1}".format( function.namespace(), plain_name( function ) )
    else:
        return plain_name( function )


def tex_description( function ):
    """Return a TeX string that describes, what @p function does."""
    description = _tex_method_descriptions.get( plain_name( function ), "" )

    for namespace_re, tex_name in _tex_namespace_names:
        match = namespace_re.match( function.namespace() )
        if match:
            tex_name = tex_name.format( **match.groupdict() )
            # Make the plain l a script l (\ell in TeX)
            tex_name = tex_name.replace( "\divpoly[l]", r"\divpoly[\l]" )
            return description.format( ns = tex_name )
    else:
        return description.format( ns = function.namespace() )


#------------------------------------------------------------------------------
# These tables are ugly. However, the effort that proper parsing takes would
# never pay off.

import re

_tex_namespace_names = [ (re.compile(r), n) for r, n in [
        ( "^E<Q<E<GF<(?P<q>[q0-9]+)>>\[x,y\]/psi\[(?P<l>[l0-9]+)\]>>$",
          r"$\ecE\bigl(\ratField{{\fieldF_{{{q}}}}}{{\ecE}}/\divpoly[{l}]\bigr)$" ),
          
        ( "^Q<E<GF<(?P<q>[q0-9]+)>>\[x,y\]/psi\[(?P<l>[l0-9]+)\]>$",
          r"$\ratField{{\fieldF_{{{q}}}}}{{\ecE}}/\divpoly[{l}]$" ),
          
        ( "^E<GF<(?P<q>[q0-9]+)>>\[x,y\]/psi\[(?P<l>[l0-9]+)\]$",
          r"$\polyRing{{\fieldF_{{{q}}}}}{{\ecE}}/\divpoly[{l}]$" ),
          
        ( "^E<GF<(?P<q>[q0-9]+)>>\[x,y\]$",
          r"$\polyRing{{\fieldF_{{{q}}}}}{{\ecE}}$" ),
          
        ( "^E<GF<(?P<q>[q0-9]+)>>$",
          r"$\ecE$" ),
          
        ( "^GF<(?P<q>[q0-9]+)>\[x\]$",
          r"$\polyRing{{\fieldF_{{{q}}}}}{{\x}}$" ),
          
        ( "^GF<(?P<q>[q0-9]+)>$",
          r"$\fieldF_{{{q}}}$" ), ]
    ]
    
_tex_method_descriptions = {
        "__add__"       : "Addition in {ns}", 
        "__radd__"      : "Addition in {ns}", 
        "__sub__"       : "Subtraction in {ns}", 
        "__rsub__"      : "Subtraction in {ns}",
        "__mul__"       : "Multiplication in {ns}",
        "__rmul__"      : "Multiplication in {ns}",
        "__truediv__"   : "Division in {ns}",
        "__rtruediv__"  : "Division in {ns}",
        "__divmod__"    : "Division with remainder in {ns}",
        "__rdivmod__"   : "Division with remainder in {ns}",
        "__mod__"       : "Taking the remainder in {ns}",
        "__rmod__"      : "Taking the remainder in {ns}",
        "__pow__"       : "Exponentiation in {ns}",
        "__rpow__"      : "Exponentiation in {ns}",
        "__neg__"       : "Negation in {ns}",
        "frobenius"     : "Frobenius endomorphism",
        "frobenius_trace"      : r"Computation of $\trace({{\frob}})$",
        "frobenius_trace_mod_l": r"Computation of $\trace({{\frob}}) \mod \l$",
        "frobenius_trace_mod_2": r"Computation of $\trace({{\frob}}) \mod 2$",
        "frobenius_equation": r"Test trace candidate on $\charpoly{{\frob}}(\frob) = \rmapId$",
        "<meta>__call__"    : "Object creation",
        "__new__"           : "Object creation",
        "__init__"          : "Object initialization",
        "naive_schoof_algorithm": "Main function",
        "remainder"     : r"Get the representative of $\felA \in$ {ns}",
    }
