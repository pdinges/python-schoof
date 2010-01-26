# -*- coding: utf-8 -*-
# $Id$

class CallGraph:
    """
    A graph of function calls extracted from one or more pstats.Stats objects.
    
    The nodes represent the functions; the arcs represent calls from caller
    to callee. Arcs are labeled with profiling information.
    """
    def __init__(self, stats):
        self.__name_index = {}
        self.add(stats)

    def add(self, stats):
        for name, data in stats.stats.items():
            function = self.__name_index.setdefault( name, Function( *name ) )
            
            # Dictionary of all functions that called 'function'
            caller_dict = data[4]
            for caller_name, caller_data in caller_dict.items():
                caller = self.__name_index.setdefault( caller_name, Function( *caller_name ) )
                # Automatically registers with functions on creation
                call = Call( caller, function, *caller_data )
                
    def function(self, name):
        return self.__name_index[ name ]

    def __iter__(self):
        for function in self.__name_index.values():
            yield function
            
    def __getitem__(self, name):
        # TOOD: Implement proper item access
        return self.__name_index[ name ]


# Nodes
from functools import reduce
from operator import add

class Function:
    def __init__(self, filename, line_number, name):
        self.__filename = filename
        self.__line_number = line_number
        self.__name = name
        self.__incoming_calls = set()
        self.__outgoing_calls = set()

    def filename(self):
        return self.__filename
    
    def line_number(self):
        return self.__line_number
    
    def name(self):
        return self.__name
    
    def inline_time(self):
        inline_times = [ c.inline_time() for c in self.__incoming_calls ]
        return reduce( add, inline_times, 0 )
    
    def cumulative_time(self):
        outgoing_times = [ c.cumulative_time() for c in self.__outgoing_calls ]
        return reduce( add, outgoing_times, self.inline_time() )
    
    def incoming_calls(self):
        return self.__incoming_calls
    
    def outgoing_calls(self):
        return self.__outgoing_calls
    
    def callers(self):
        return [ call.caller() for call in self.__incoming_calls ]
    
    def callees(self):
        return [ call.callee() for call in self.__outgoing_calls ]

    def _register_call(self, call):
        if self is call.caller():
            self.__outgoing_calls.add( call )
        elif self is call.callee():
            self.__incoming_calls.add( call )

    def _unregister_call(self, call):
        self.__outgoing_calls.discard( call )
        self.__incoming_calls.discard( call )
        
    def __str__(self):
        return "Function '{name}'".format( name = self.__name )
        

# Arcs
class Call:
    def __init__(self, caller, callee, primitive_calls, total_calls, inline_time, cumulative_time):        
        self.__caller = caller
        self.__callee = callee
        self.__primitive_calls = primitive_calls
        self.__total_calls = total_calls
        self.__inline_time = inline_time
        self.__cumulative_time = cumulative_time
        
        caller._register_call( self )
        callee._register_call( self )
        
    def __del__(self):
        self.__caller._unregister_call( self )
        self.__callee._unregister_call( self )

    def caller(self):
        return self.__caller
    
    def callee(self):
        return self.__callee
    
    def primitive_calls(self):
        return self.__primitive_calls
    
    def total_calls(self):
        return self.__total_calls
    
    def inline_time(self):
        return self.__inline_time
    
    def cumulative_time(self):
        return self.__cumulative_time
    
    def __str__(self):
        return "{caller} --> {callee}".format( caller = self.__caller, callee = self.__callee )
