# -*- coding: utf-8 -*-
# $Id$

from rings.quotients.naive import QuotientRing
from fields.fraction.naive import FractionField
from elliptic_curves.naive import EllipticCurve
from elliptic_curves.polynomials.naive import CurvePolynomials
from elliptic_curves.division_polynomials.naive import DivisionPolynomialsList

from support.types import template

class NTorsionGroup( metaclass=template("_elliptic_curve") ):
    def __init__(self, torsion):
        self.__torsion = torsion
        self.__point = None
    
    def elements(self):
        """
        Return a list containing the one point that implicitly represents
        the whole group through polynomials (X, Y). This perfectly
        fits into the algorithm.
        """
        if not self.__point:
            self.__init_point()
        return [ self.__point ]
    
    def torsion(self):
        return self.__torsion

    @classmethod
    def curve(cls):
        return cls._elliptic_curve
    
    def __init_point(self):
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

    @classmethod
    def _division_polynomial_list(cls):
        try:
            return cls.__division_polynomial_list
        except AttributeError:
            # R = F[x] / (y**2 - x**3 - A*x - B)
            # where F, A, B are the elliptic curve's field and its parameters.
            R = CurvePolynomials( cls._elliptic_curve )
            cls.__division_polynomial_list = DivisionPolynomialsList( R )

            return cls.__division_polynomial_list
