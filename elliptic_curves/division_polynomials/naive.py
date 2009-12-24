# -*- coding: utf-8 -*-
# $Id$

from elliptic_curves.polynomials.naive import CurvePolynomialRing

def division_polynomials_list(curve, n):
    psi = 5 * [ None ]
    A, B = curve.parameters()

    # R = F[x] / (y**2 - x**3 - A*x - B)
    R = CurvePolynomialRing( curve )
    x = R( (0, 1), 0 )
    y = R(  0    , 1 )
    
    psi[0] = R( 0, 0 )  
    psi[1] = R( 1, 0 )
    psi[2] = R( 0, 2 )
    psi[3] = R( (-(A**2), 12*B, 6*A, 0, 3), 0 )
    psi[4] = R(
            0,
            ( -4*( 8*(B**2) + A**3 ), -16*A*B, -20*(A**2), 80*B, 20*A, 0, 4 )
        )
   
    for j in range(5, n+1):
        k, l = divmod(j, 2) 
        if l:
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
    
    return psi[0:n+1]
