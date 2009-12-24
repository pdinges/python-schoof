# -*- coding: utf-8 -*-
# $Id$

class IntegerRing:
    """
    Ring of integers.
    
    This wrapper class makes python's integers available under the interface
    for ring classes.  
    """
    def __eq__(self, other):
        return self is other or isinstance(other, self.__class__)
    
    def __call__(self, n):
        return int(n)
    
    def zero(self):
        return 0

    def one(self):
        return 1
