# -*- coding: utf-8 -*-
# $Id$

class Integers(int):
    """
    Ring of integers.
    
    This wrapper class makes python's integers available under the interface
    for rings.  
    """
    @staticmethod
    def zero():
        return 0

    @staticmethod
    def one():
        return 1
