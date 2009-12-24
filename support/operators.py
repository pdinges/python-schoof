# -*- coding: utf-8 -*-
# $Id$

#   @f( arg )
#   def g(): pass
# resolves to
#   def g(): pass
#   g = f( arg )( g )
# See section "Function definitions" in the Python language reference.
def ascertain_operand_set( operand_set_getter ):
    """
    A decorator function for binary operators that, if necessary, translates
    the 'other' operand into an element from the set returned by
    operand_set_getter().
    """
    def decorator( operator ):
        def wrapped_operator( self, other ):
            try:
                self_operand_set = getattr( self, operand_set_getter )()
                other_operand_set = getattr( other, operand_set_getter )()
                if self_operand_set == other_operand_set:
                    return operator( self, other )
            except AttributeError:
                pass
    
            try:
                # Retry after type casting
                self_operand_set = getattr( self, operand_set_getter )()
                return operator( self, self_operand_set( other ) )
            except TypeError:
                return NotImplemented
    
        return wrapped_operator    
    return decorator
