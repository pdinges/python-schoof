# -*- coding: utf-8 -*-
# $Id$

from support.profiling import profiling_name

@profiling_name("Z")
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
