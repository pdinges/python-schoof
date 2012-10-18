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
A naive implementation of an implicitly represented l-torsion group
of an elliptic curve.

@package   elliptic_curves.l_torsion_group.naive
@author    Peter Dinges <pdinges@acm.org>
"""

from rings.quotients.naive import QuotientRing
from fields.fraction.naive import FractionField
from elliptic_curves.naive import EllipticCurve
from elliptic_curves.polynomials.naive import CurvePolynomials
from elliptic_curves.division_polynomials.naive import DivisionPolynomialsList

from support.types import template

class LTorsionGroup( metaclass=template("_elliptic_curve") ):
    """
    An l-torsion group of an elliptic curve for odd l; use the @c elements()
    method to have intuitive syntax when working with l-torsion points.
    
    This is a template class that must be instantiated with the elliptic curve.
    Use it, for example, as follows:
    @code
    # Create the underlying elliptic curve
    E = elliptic_curves.naive.EllipticCurve( FiniteField(7), 3, 4 )
    # Instantiate the template; El is a class (here: l-torsion groups of E)
    El = LTorsionGroup( E )
    
    # Construct the group of 3-torsion points and do something with its points
    for P in El[3].elements():
        do_something(P)
    @endcode
    
    The l-Torsion points of an elliptic curve are the points of order l.  Their
    coordinates come from the algebraic closure of the elliptic curve's field,
    which makes them badly suited for computer representation. (Extending the
    coordinate domain to the algebraic closure makes sure that all points of
    order l are available; there are always @f$ l^2 @f$ points of order l if
    l is prime to the field characteristic.) 
    
    @note  The l-torsion points are represented implicitly through polynomial
           arithmetic.  Therefore, the list of points in returned by
           @c elements() contains only a single entry: the point @f$ (x, y) \in
           E\bigl(\mathbb{F}_{p}(E) / \psi_l\bigr) @f$, where
           @f$ \mathbb{F}_{p}(E)/\psi_l @f$ denotes the field of rational
           functions over the elliptic curve @f$ E @f$ with numerator and
           denominator polynomials taken modulo the l-th division polynomial
           @f$ \psi_l @f$.
           
    @note  The class supports only odd torsions greater one because
           multivariate polynomial arithmetic is unavailable
           
    @see   Silverman, Joseph H., "The Arithmetic of Elliptic Curves",
           second edition, Springer, 2009, p. 373
    """

    #- Instance Methods ------------------------------------------------------- 
    
    def __init__(self, torsion):
        """
        Construct a new l-torsion group for the given @p torsion.
        
        @param torsion The @p torsion is the order of the points in the group;
                       the group represents all points of order @p torsion.  It
                       must be an odd integer greater than 1 and prime to the
                       field characteristic; the limitation comes from the
                       implicit representation, see above. 
        """
        torsion = int( torsion )
        if torsion < 3 or torsion % 2 == 0 or self.curve().field()(torsion) == 0:
            raise ValueError( "only odd torsions greater than 1 are supported" )
        
        self.__torsion = torsion
        self.__point = None
    
    
    def elements(self):
        """
        Return a list containing the one point that implicitly represents
        the whole group.
        
        Use it, for example, to elegantly perform an operation on all l-torsion
        points:
        @code
        for P in torsion_group.elements():
            do_something(P)
        @endcode

        The one point in the list is @f$ (x, y) \in
        E\bigl(\mathbb{F}_{p}(E) / \psi_l\bigr) @f$, where
        @f$ \mathbb{F}_{p}(E)/\psi_l @f$ denotes the field of rational functions
        over the elliptic curve @f$ E @f$ with numerator and denominator
        polynomials taken modulo the l-th division polynomial @f$ \psi_l @f$.
        """
        if not self.__point:
            self.__init_point()
        return [ self.__point ]
    
    
    def torsion(self):
        """
        Return the group's torsion, that is, l for the l-torsion group.
        """
        return self.__torsion


    def __init_point(self):
        """
        Create the point that implicitly represents the whole l-torsion group
        and store it in the cache.
        
        Calling the method has no effect if the point already exists.
        """
        if self.__point:
            return
        
        # R = F[x] / (y**2 - x**3 - A*x - B)
        R = self._division_polynomial_list().curve_polynomials()
        # The n-th division polynomial
        psi = self._division_polynomial_list()[ self.__torsion ]

        # T = ( F[x] / (y**2 - x**3 - A*x - B) ) / psi(l)
        S = QuotientRing( R, psi )
        T = FractionField( S )
        
        A, B = R.curve().parameters()
        
        # Polynomials x and y on the curve interpreted
        # as elements of the field of fractions
        x = T( R( (0, 1), 0 ) )
        y = T( R( 0     , 1 ) )
        
        self.__point = EllipticCurve( T, A, B )( x, y )


    #- Class Methods----------------------------------------------------------- 
    
    @classmethod
    def curve(cls):
        """
        Return the elliptic curve that was used to initialize the template.
        """
        return cls._elliptic_curve
    
    @classmethod
    def _division_polynomial_list(cls):
        """
        Return the list of division polynomials that supplies the modulus for
        the implicit polynomial representation of the l-torsion points.
        """
        try:
            return cls.__division_polynomial_list
        except AttributeError:
            # R = F[x] / (y**2 - x**3 - A*x - B)
            # where F, A, B are the elliptic curve's field and its parameters.
            R = CurvePolynomials( cls._elliptic_curve )
            cls.__division_polynomial_list = DivisionPolynomialsList( R )

            return cls.__division_polynomial_list
