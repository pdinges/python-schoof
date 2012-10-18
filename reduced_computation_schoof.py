# -*- coding: utf-8 -*-
# $Id$

"""
An implementation of Schoof's algorithm for counting the points of
elliptic curves over finite fields; the implementation avoids unnecessary
computations.

The implementation is faster than the naive version. Yet, it still uses naive
arithmetic and is badly suited for actual counting tasks. It demonstrates the
performance improvement from a smarter choice of moduli and reordered
computations.

@see Schoof, R.
"Elliptic Curves Over Finite Fields and the Computation of Square Roots mod p"
in Mathematics of Computation, Vol. 44, No. 170 (Apr. 1985), pp. 483--494.

@package   schoof.reduced_computation
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
    trace_congruences = []
    search_range = hasse_frobenius_trace_range( curve.field() )
    torsion_primes = greedy_prime_factors(
                                 len(search_range),
                                 curve.field().characteristic()
                             )
    
    # To avoid multivariate polynomial arithmetic, make l=2 a special case.
    if 2 in torsion_primes:
        trace_congruences.append( frobenius_trace_mod_2( curve ) )
        torsion_primes.remove( 2 )

    torsion_group = LTorsionGroup( curve )
    for prime in torsion_primes:
        trace_congruences.append(
                frobenius_trace_mod_l( torsion_group( prime ) )
             )
    
    trace_congruence = solve_congruence_equations( trace_congruences )
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
    
    # gcd() returns a gcd, which may have any unit as leading coefficient.
    # For relatively prime polynomials, the gcd is constant. 
    if gcd( rational_characteristic, defining_polynomial ).degree() == 0:
        # The rational characteristic and the defining polynomial are
        # relatively prime. Thus there is no rational point of order 2.
        return QuotientRing( Integers, 2 )(1)
    else:
        return QuotientRing( Integers, 2 )(0)


from rings.integers.naive import Integers
from rings.quotients.naive import QuotientRing

def frobenius_trace_mod_l(torsion_group):
    """
    Compute the trace of the Frobenius endomorphism modulo @f$ l @f$, where
    @f$ l @f$ is the torsion of @p torsion_group.
    
    The function guesses candidates and verifies whether the function that
    results from applying the characteristic polynomial @f$ \chi_\phi @f$
    to @f$ \phi @f$ maps every point in the @p torsion_group onto the point
    at infinity.
    
    @note      A torsion of 2 requires multivariate polynomial arithmetic,
               which is unavailable.  Therefore @f$ l @f$ must be greater than 2.
               Use frobenius_trace_mod_2() to get the trace modulo 2.
    
    @return    The congruence class of the trace of the Frobenius endomorphism.
               This is an element of @c QuotientRing( Integers, l ). 
    """
    assert torsion_group.torsion() > 2, \
        "torsion 2 requires multivariate polynomial arithmetic"
        
    torsion_quotient_ring = QuotientRing( Integers, torsion_group.torsion() )
    field_size = torsion_group.curve().field().size()

    # Note: Technically, there could be several points so we would have to
    #       filter the one candidate that worked for all points in the end.
    #       Luckily, there is only one point.
    for point in torsion_group.elements():
        frobenius_point = frobenius( point, field_size )
        frobenius2_point = frobenius( frobenius_point, field_size )
        determinant_point = ( field_size % torsion_group.torsion() ) * point
        
        point_sum = frobenius2_point + determinant_point
        if point_sum.is_infinite():
            return torsion_quotient_ring( 0 )
        
        trace_point = frobenius_point
        for trace_candidate in range( 1, (torsion_group.torsion()+1) // 2 ):
            if point_sum.x() == trace_point.x():
                if point_sum.y() == trace_point.y():
                    return torsion_quotient_ring( trace_candidate )
                else:
                    return torsion_quotient_ring( -trace_candidate )
            else:
                trace_point += frobenius_point

    message = "Frobenius equation held for no trace candidate"
    raise ArithmeticError( message )


def frobenius(point, q):
    """
    The Frobenius endomorphism @f$ \phi @f$.
    
    @return    The point @f$ (x^q, y^q) @f$ if @p point is @f$ (x, y) @f$.
    """
    return point.__class__( point.x() ** q, point.y() ** q )


from math import ceil, sqrt

def hasse_frobenius_trace_range(field):
    """
    Return the interval in which the trace of the Frobenius endomorphism
    must reside (using Hasse's theorem).
    
    Hasse's theorem gives a limit for the trace @f$ t @f$ of the Frobenius
    endomorphism on an elliptic curve over a field with  @f$ q @f$ elements:
    @f$ \left|t\right| \leq 2\sqrt{q} @f$.
    
    @return    The interval that must contain the trace of the Frobenius
               endomorphism according to Hasse's theorem.
    """
    # This only depends on the field and holds for any curve over it. 
    l = 2 * ceil( sqrt( field.size() ) )
    return range( -l, l+1 )


from support.primes import primes_range, inverse_primorial

def greedy_prime_factors(n, shunned=0):
    """
    Return a list of the first primes whose product is greater than, or equal
    to @p n, but do not use @p shunned.
    
    For example, if @p n is 14, then the returned list will consist of 3 and
    5, but not 2, because 3 times 5 is greater than 14. The function behaves
    like inverse_primorial() except that it removes unnecessary smaller primes.
    
    @note      Canceling of unnecessary primes follows a greedy algorithm.
               Therefore the choice of primes might be suboptimal; perfect
               choice, however, is an NP-complete problem (KNAPSACK).
    
    @note      This function uses primes_range() to obtain a list of primes.
               See the notes there for use case limitations.
    """
    primes = primes_range( 2, n+1 )
    
    # Find the smallest product of primes that is at least n, but don't use
    # the shunned prime.
    product = 1
    for index, prime in enumerate( primes ):
        if prime != shunned:
            product *= prime
            if product >= n:
                break
    
    # Throw away excess primes
    primes = primes[ : index+1 ]
    if shunned in primes:
        primes.remove( shunned )
    
    # Try to cancel unnecessary primes, largest first.
    # (This greedy search is not optimal; however, we did not set out to solve
    # the KNAPSACK problem, did we?)
    for index, prime in enumerate( reversed( primes ) ):
        canceled_product = product / prime
        if canceled_product >= n:
            product = canceled_product
            primes[ -(index+1) ] = 0
    
    return list( filter( None, primes ) )
    

#------------------------------------------------------------------------------

from fields.finite.naive import FiniteField
from elliptic_curves.naive import EllipticCurve

import sys
from support.running import AlgorithmRunner

def reduced_computation_schoof_algorithm( p, A, B, output=sys.stdout ):
    p, A, B = int(p), int(A), int(B)
    
    message = "Counting points of y^2 = x^3 + {A}x + {B} over GF<{p}>: "
    print( message.format( p=p, A=A, B=B ), end="", file=output )
    output.flush()
    
    order = p + 1 - frobenius_trace( EllipticCurve( FiniteField(p), A, B ) )
    print( order, file=output )
    return order


if __name__ == "__main__":
    runner = AlgorithmRunner(
                     reduced_computation_schoof_algorithm,
                     algorithm_version="$Rev$"
                 ) 
    runner.run()

