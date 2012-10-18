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
An indexed list of division polynomials.

@package   elliptic_curves.division_polynomials.naive
@author    Peter Dinges <pdinges@acm.org>
"""

class DivisionPolynomialsList:
    """
    An indexed list of division polynomials over an elliptic curve.

    Use it, for example, as follows:
    @code
    # Create the underlying elliptic curve
    E = elliptic_curves.naive.EllipticCurve( FiniteField(7), 3, 4 )
    R = CurvePolynomials( E )
    # Instantiate the list
    psi = DivisionPolynomialsList( R )

    # Retrieve some division polynomials
    p = psi[2]    # The second is '2y'
    q = psi[3]    # The third is already longer: 3x^4 + 6Ax^2 + 12Bx -A^2
    
    # Use division polynomials for arithmetic on l-torsion points
    Q = QuotientRing( R, psi[3] )
    # Do something with Q...
    @endcode

    The division polynomials are specific polynomials over an elliptic curve.
    The l-th divison polynomial @f$ \psi_l @f$ has zeros of multiplicity 1
    precisely at the finite l-torsion points
    @f$ E[l]\setminus\{\mathcal{O}\} @f$.  Modular polynomial arithmetic then
    allows computations with the l-torsion points without knowing them
    explicitly. (Their coordinates come from the algebraic closure of the
    curve's field; thus they might be badly suited for computer representations.)
    
    An implementation of l-torsion groups using division polynomials is available from
    @c elliptic_curves.l_torsion_group.naive.LTorsionGroup. 
    
    @note  The implementation lazily constructs the polynomials: the l-th polynomial
           will be instantiated only if index @c l is accessed; the polynomial will
           then be cached.
        
    @see   elliptic_curves.polynomials.naive.CurvePolynomials;
           elliptic_curves.l_torsion_group.naive.LTorsionGroup; and
           Charlap, Leonard S. and Robbins, David P., "CRD Expositroy Report 31:
           An Elementary Introduction to Elliptic Curves", 1988, chapter 9
    """

    def __init__(self, curve_polynomials):
        """
        Construct a new list of division polynomials for the given ring of
        @p curve_polynomials.
        
        @param curve_polynomials   The ring of polynomials over an elliptic
                                   curve from which the polynomials will come.
                                   Note that no type checks will be performed
                                   to guarantee maximum freedom in experiments.
                                   If the given object supports the interface
                                   of @c elliptic_curves.polynomials.naive.CurvePolynomials,
                                   then everything will be fine.
        """
        class DivisionPolynomials( curve_polynomials ):
            """
            DivisionPolynomials are specific instances of polynomials on the
            curve.  They grow quadratically in degree, which clutters their
            string representation.  Instead of printing the coefficients,
            print the customary 'psi[l]' where l is the polynomial's index.
            
            @see   elliptic_curves.polynomials.naive.CurvePolynomials
            """
            def __str__(self):
                # The leading coefficient equals the torsion.  Using quotient
                # classes is not a problem: first of all, they should not
                # appear in realistic use cases.
                # Second, adding a point m-times to itself for m > p, where p
                # denotes the field characteristic, is the same as adding it
                # m % p times to itself.  Therefore, the m-th division
                # polynomial must equal the (m % p)-th division polynomial. 
                return "psi[{0}]".format(
                             self.leading_coefficient().remainder()
                         )
        self.__curve_polynomials = DivisionPolynomials
        
        # __psi is the cache of division polynomials.
        self.__psi = None
    
    
    def __getitem__(self, index):
        """
        Retrieve the division polynomial with the given @p index; an index
        of @f$ l @f$ will return @f$ \psi_l @f$.
        
        The polynomial will be an instance of @c curve_polynomials().
        """
        index = int(index)
        if index < 0:
            raise IndexError
        
        self.__generate_up_to( index )
        return self.__psi[ index ]


    def curve_polynomials(self):
        """
        Return the ring of polynomials from which the division polynomials come.
        
        This is the ring of polynomials over an elliptic curve used to
        construct the DivisionPolynomialsList.
        
        @see   __init__()
        """
        return self.__curve_polynomials


    def __generate_up_to( self, l ):
        """
        Ascertain that all division polynomials up to (including) 'l'
        exist in the cache self.__psi.
        
        Calling this method has no effect if the polynomials already exist.
        """
        # See Charlap, Leonard S. and Robbins, David P., "CRD Expositroy
        # Report 31: An Elementary Introduction to Elliptic Curves", 1988,
        # Definition 9.8 for the recurrence
        if not self.__psi:
            self.__psi = 5 * [ None ]
 
            # R = F[x,y] / (y**2 - x**3 - A*x - B)
            R = self.__curve_polynomials
            # The polynomial y (used in the recursion scheme)
            self.__y = R( 0, 1 )

            A, B = self.__curve_polynomials.curve().parameters()
            
            # Lists are copied by reference; assigning to psi modifies self.__psi
            psi = self.__psi
            psi[0] = R( 0, 0 )  
            psi[1] = R( 1, 0 )
            psi[2] = R( 0, 2 )
            psi[3] = R( (-(A**2), 12*B, 6*A, 0, 3), 0 )
            psi[4] = R(
                    0,
                    ( -4*( 8*(B**2) + A**3 ), -16*A*B, -20*(A**2), 80*B, 20*A, 0, 4 )
                )

        psi = self.__psi
        y = self.__y
        for j in range( len(self.__psi), l+1 ):
            k, m = divmod(j, 2) 
            if m:
                # j is odd
                psi.append( psi[k+2] * psi[k]**3  -  psi[k+1]**3 * psi[k-1] )
            else:
                if k % 2 == 0:
                    psi.append(
                            ( psi[k].y_factor() // 2 ) \
                            * ( psi[k+2] * psi[k-1]**2 - psi[k-2] * psi[k+1]**2 )
                        )
                else:
                    psi.append(
                            y * ( psi[k].x_factor() // 2 ) \
                            * ( psi[k+2] * psi[k-1].y_factor()**2  \
                                - psi[k-2] * psi[k+1].y_factor()**2 )
                        )
