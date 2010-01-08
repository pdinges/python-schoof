# -*- coding: utf-8 -*-
# $Id$

class DivisionPolynomialsList:
    """
    List of division polynomials ordered by index.
    
    This implementation generates the polynomials on demand
    and caches the results.
    """
    def __init__(self, curve_polynomials):
        self.__curve_polynomials = curve_polynomials
        # __psi is the cache of division polynomials.
        self.__psi = None
    
    
    def __getitem__(self, index):
        """
        Retrieve the division polynomial with the given index.
        
        The polynomial will be an instance of curve_polynomials().
        """
        index = int(index)
        if index < 0:
            raise IndexError
        
        self.__generate_up_to( index )
        return self.__psi[ index ]


    def curve_polynomials(self):
        return self.__curve_polynomials

    def __generate_up_to( self, n ):
        """
        Ascertain that all division polynomials up to (including) 'n'
        exist in the cache self.__psi.
        
        Calling this method has no effect if the polynomials already exist.
        """
        if not self.__psi:
            self.__psi = 5 * [ None ]
 
            # R = F[x] / (y**2 - x**3 - A*x - B)
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
        for j in range( len(self.__psi), n+1 ):
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
