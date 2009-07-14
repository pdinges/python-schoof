# -*- coding: utf-8 -*-
# $Id$

class FiniteField:
    """
    Finite field base class.
    
    This class and its subclasses are unnecessary, strictly speaking.
    Their only purpose at the moment is to make the algorithms more verbose.
    """
    def __init__(self, size):
        self._size = int(size)
    
    def __call__(self, representative):
        raise NotImplementedError

    def __str__(self):
        return """finite field of {0} elements""".format( self._size )
    