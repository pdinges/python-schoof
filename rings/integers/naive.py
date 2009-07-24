# -*- coding: utf-8 -*-
# $Id$

class IntegerRing:
    """
    Ring of integers.
    
    This wrapper class makes python's integers available under the interface
    for ring classes.  
    """
    def __call__(self, n):
        return int(n)
    
    def zero(self):
        return 0

    def one(self):
        return 1
