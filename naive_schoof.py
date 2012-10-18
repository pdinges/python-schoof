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


"""
A naive implementation of Schoof's algorithm for counting the points of
elliptic curves over finite fields.

The implementation is meant for instructional purposes, not for actual counting
of, say, curves for cryptographic settings. It uses naive arithmetic and
emphasizes ease of understanding over performance; all speed-ups (such as
symmetry of search ranges, Hasse's theorem, etc.) are excluded.

@see Schoof, R.
"Elliptic Curves Over Finite Fields and the Computation of Square Roots mod p"
in Mathematics of Computation, Vol. 44, No. 170 (Apr. 1985), pp. 483--494.

@package   schoof.naive
@author    Peter Dinges <pdinges@acm.org>
"""

from elliptic_curves.l_torsion_group.naive import LTorsionGroup
from support.primes import inverse_primorial, primes_range
from support.quotients import solve_congruence_equations, representative_in_range

def frobenius_trace(curve):
    """
    Compute the trace of the Frobenius endomorphism for the given EllpiticCurve
    @p curve.
    
    This is an implementation of Schoof's original algorithm for counting the
    points of an elliptic curve over a finite field.
    
    @return    The trace @f$ t @f$ of the Frobenius endomorphism. The number of
               points on the curve then is @f$ q + 1 - t @f$, where @f$ q @f$
               is the size of the finite field over which the curve was defined.
    """
    # Initialize variables and parameters
    trace_congruences = []
    search_range = possible_frobenius_trace_range( curve.field() )
    upper_prime_bound = inverse_primorial(
                            len(search_range),
                            shunned = curve.field().characteristic()
                          )
    
    # Collect the congruence equations (avoid multivariate
    # polynomial arithmetic by handling 2-torsion separately)
    trace_congruences.append( frobenius_trace_mod_2( curve ) )

    torsion_group = LTorsionGroup( curve )
    for prime in primes_range( 3, upper_prime_bound+1 ):
        if prime != curve.field().characteristic():
            trace_congruences.append(
                    frobenius_trace_mod_l( torsion_group( prime ) )
                 )
    
    # Recover the unique valid trace representative
    trace_congruence = solve_congruence_equations(
                                          trace_congruences
                                      )
    return representative_in_range( trace_congruence, search_range )


from rings.integers.naive import Integers
from rings.polynomials.naive import Polynomials
from rings.quotients.naive import QuotientRing
from support.rings import gcd

def frobenius_trace_mod_2(curve):
    """
    Compute the trace of the Frobenius endomorphism modulo 2.
    
    We cannot use the implicit torsion group representation of
    frobenius_trace_mod_l() in the case @f$ l=2 @f$ because the second division
    polynomial is @f$ y @f$, and multivariate polynomial arithmetic is
    unavailable. Implementing it for this single case would be overkill.
    
    Instead, we test whether there are any rational 2-torsion points. If so,
    then @f$ E[2] @f$ is a subgroup of the @p curve and its order divides the
    order of the curve (which is the number of rational points). Now, the
    number of rational points in @f$ E[2] @f$ can only be 2 or 4 in this case, so
    we know that the number of rational points is even. Hence, the Frobenius
    trace must then be 0 modulo 2.
    
    @return    0 if the number of points on the curve is even, 1 otherwise.
               The result is a congruence class modulo 2, that is, an element
               of @c QuotientRing( Integers, 2 ).
    """
    R = Polynomials( curve.field() )
    
    x = R(0, 1)
    A, B = curve.parameters()

    defining_polynomial = x**3 + A*x + B
    rational_characteristic = x**curve.field().size() - x
    
    # gcd() has an arbitrary unit as leading coefficient;
    # relatively prime polynomials have a constant gcd.
    d = gcd( rational_characteristic, defining_polynomial )
    if d.degree() == 0:
        # The rational characteristic and the defining polynomial
        # are relatively prime: no rational point of order 2 exists
        # and the Frobenius trace must be odd.
        return QuotientRing( Integers, 2 )(1)
    else:
        return QuotientRing( Integers, 2 )(0)


from rings.integers.naive import Integers
from rings.quotients.naive import QuotientRing

def frobenius_trace_mod_l(torsion_group):
    """
    Compute the trace of the Frobenius endomorphism modulo @f$ l @f$, where
    @f$ l @f$ is the torsion of @p torsion_group.
    
    The function guesses candidates and verifies the frobenius_equation() for
    every point in the @p torsion_group.
    
    @note      A torsion of 2 requires multivariate polynomial arithmetic,
               which is unavailable.  Therefore @f$ l @f$ must be greater than 2.
               Use frobenius_trace_mod_2() to get the trace modulo 2.
    
    @return    The congruence class of the trace of the Frobenius endomorphism.
               This is an element of QuotientRing( Integers, l ). 
    """
    assert torsion_group.torsion() > 2, \
        "torsion 2 requires multivariate polynomial arithmetic"
        
    ints_mod_torsion = QuotientRing( Integers,
                                     torsion_group.torsion() )
    field_size = torsion_group.curve().field().size()
    
    for trace_candidate in range( 0, torsion_group.torsion() ):
        candidate_congruence = ints_mod_torsion( trace_candidate )
        for point in torsion_group.elements():
            if not frobenius_equation( candidate_congruence,
                                       field_size,
                                       point ):
                # Exit inner loop and skip the 'else' clause.
                break
        else:
            # Execute after the iteration completed; skip upon break.
            return candidate_congruence
    
    message = "Frobenius equation held for no trace candidate"
    raise ArithmeticError( message )


def frobenius_equation(trace, size, point):
    """
    Check whether @p trace could be the trace of the Frobenius endomorphism
    @f$ \phi @f$ on the l-torsion group. To test the candidate, use it in
    the function that results from applying the characteristic polynomial
    @f$ \chi_\phi @f$ to @f$ \phi @f$.  This function must then map @p point
    onto the point at infinity.
    
    @param     trace   The candidate congruence class for the remainder of the
                       trace of @f$ \phi \mod l @f$.
    @param     size    The size of the field over which the curve was defined.
                       This is the exponent of the Frobenius endomorphism.
    @param     point   The l-torsion point that will be inserted into
                       @f$ \chi_{\phi}(phi) @f$.
    
    @return    @c True, if @f$ (\chi_{\phi}(\phi))(\mathtt{point}) @f$ is the
               point at infinity. 
    """ 
    size_remainder = size % trace.modulus()
    result = frobenius( frobenius(point, size), size ) \
                - trace.remainder() * frobenius(point, size) \
                + size_remainder * point
    return result.is_infinite()


def frobenius(point, q):
    """
    The Frobenius endomorphism @f$ \phi @f$.
    
    @return    The point @f$ (x^q, y^q) @f$ if @p point is @f$ (x, y) @f$.
    """
    return point.__class__( point.x() ** q, point.y() ** q )


def possible_frobenius_trace_range(field):
    """
    Return the interval in which the trace of the Frobenius endomorphism
    must reside.
    
    This is the naive estimation: a curve has at least one point (at infinity),
    and at most @f$ 2q + 1 @f$ points, where @f$ q @f$ is the field size.
    
    @return    The interval that must contain the trace of the Frobenius
               endomorphism.
    """
    # This only depends on the field and holds for any curve over it. 
    return range( -field.size(), field.size()+1 )

    
#------------------------------------------------------------------------------

from fields.finite.naive import FiniteField
from elliptic_curves.naive import EllipticCurve

import sys
from support.running import AlgorithmRunner

def naive_schoof_algorithm( p, A, B, output=sys.stdout ):
    p, A, B = int(p), int(A), int(B)
    
    message = "Counting points on y^2 = x^3 + {A}x + {B} over GF<{p}>: "
    print( message.format( p=p, A=A, B=B ), end="", file=output )
    output.flush()
    
    order = p + 1 - frobenius_trace( EllipticCurve( FiniteField(p), A, B ) )
    print( order, file=output )
    return order


if __name__ == "__main__":
    runner = AlgorithmRunner(
                     naive_schoof_algorithm,
                     algorithm_version="$Rev$"
                 ) 
    runner.run()

