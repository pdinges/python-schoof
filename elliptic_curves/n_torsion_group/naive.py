# -*- coding: utf-8 -*-
# $Id$

from rings.quotients.naive import QuotientRing
from fields.fraction.naive import FractionField
from elliptic_curves.naive import CartesianPoint
from elliptic_curves.polynomials.naive import CurvePolynomialRing


class ImplicitNTorsionGroup:
    def __init__(self, curve, torsion, division_polynomial):
        self.__curve = curve
        self.__torsion = torsion
        
        # R = F[x] / (y**2 - x**3 - A*x - B)
        R = CurvePolynomialRing( curve )
        # S = ( F[x] / (y**2 - x**3 - A*x - B) ) / psi(l)
        S = QuotientRing( R, division_polynomial )
        T = FractionField( S )

        # Polynomials x and y on the curve interpreted
        # as elements of the field of fractions
        x = T( R( (0, 1), 0 ) )
        y = T( R(  0    , 1 ) )

        self.__point = CartesianPoint( curve, x, y )
        
    
    def __iter__(self):
        """
        Return point iterator that only has one point with implicit polynomial
        representation (X, Y) mod div poly. This fits perfectly into the algorithm.
        """
        return iter([ self.__point ])
    
    def curve(self):
        return self.__curve
    
    def torsion(self):
        return self.__torsion
