# -*- coding: utf-8 -*-
# $Id$

"""
@package   callgraph
@author    Peter Dinges
"""

from functools import reduce

class CallGraph:
    """
    The CallGraph class provides a directed bipartite graph of functions and
    calls between them.
    
    A call graph represents the data of a @c pstats.Stats instance: it
    interprets the functions and their mutual invocations in the profile as
    nodes (see Function and Call). All profiling data is accessible via
    respective node methods. 
    
    The graph is easy to traverse both forwards (from caller to callee)
    and backwards (from callee to caller). Its purpose is to support
    operations that are difficult to express in the list-sorting style
    of @c pstats.Stats. Examples of such operations are pruning of execution
    branches with treat_as_builtin(), and merging of nodes with
    treat_as_inlined().
    
    Multiple @c pstats.Stats objects can be merged into a single call graph
    by invoking add() several times.
    
    @see Call, Function, and @c pstats.Stats in the
         Python library documentation.
    """
    def __init__(self, stats):
        """
        Constructs a CallGraph from the given @p stats object.
        
        @param     stats    The @c pstats.Stats compatible object whose
                            data is to be represented as the new CallGraph.
        """
        # Function -> ( Outgoing Calls, Incoming Calls )
        self.__functions = {}
        # Call -> ( Calling Function, Called Function )
        self.__calls = {}
        
        # Indexes to look up Functions
        self.__fln_index = {}       # (filename, line number, name) -> Function
        self.__namespace_index = {} # namespace name -> set of Functions
        self.add(stats)
        

    def add(self, stats):
        """
        Import data from a @c pstats.Stats compatible object.
        
        Invoke the method on every source that should be added to the graph.
        The data will be merged with functions discerned by name, file name,
        and line number: only if all three are identical will functions be
        considered the same and their profiles combined.
        
        @todo   Combining calling statistics has yet to be implemented.
                Currently, parallel arcs will be created.
        
        @param     stats    The @c pstats.Stats compatible object whose
                            data is to be added to the CallGraph.
        """
        # fln = (filename, line_number, name)
        for fln, data in stats.stats.items():
            function = self._setdefault_function( fln )
            
            # Dictionary of all functions that called 'function'
            caller_dict = data[4]
            for caller_fln, caller_data in caller_dict.items():
                caller = self._setdefault_function( caller_fln )
                self._add_call( caller, function, *caller_data )
            
            # The root function has no incoming calls to store its timing.
            if not caller_dict:
                inline_time = data[2]
                function.add_inline_time( inline_time )
                


    def total_time(self):
        """
        Returns the duration of the profiling.
        
        The duration is the amount of time that passed during the profiling.
        Every amount of time spent in individual functions or execution
        branches is less or equal to this duration.
        
        @return    The amount of time that passed during the profiling. 
        """
        cumulative_times = [ f.cumulative_time() for f in self ]
        return reduce( max, cumulative_times, 0 )

                
    def function(self, file_line_name):
        """
        Fetch the Function identified by the @p name tuple.
        
        @param    file_line_name    A tuple @c (filename, line_number, name)
                                    uniquely identifying the Function.
                              
        @return   The Function identified by the @p file_line_name tuple.
        
        @see Function.__init__()
        """
        return self.__fln_index[ file_line_name ]


    def namespace(self, name):
        """
        Fetch the set of Functions in the given namespace.
        
        @param     name    The name string identifying the namespace.
        
        @return    The set of functions that lie in the namespace. If no such
                   namespace exists, the set will be empty.
        """
        return self.__namespace_index.get( name, set() )


    def namespaces(self):
        """
        Get a list of all namespaces appearing in added profiles.
        
        @return    A list of all known namespace name strings.
        """
        return self.__namespace_index.keys()


    def __iter__(self):
        """
        Iterate over all Functions in the call graph without particular order.
        
        @return    A generator to iterate over all Functions in the call graph.
        """
        for function in self.__fln_index.values():
            yield function
            
    
    def treat_as_builtin(self, function):
        """
        Make @p function behave like a built-in function.
        
        The method removes the function from the graph; the profiling data,
        execution time and call counts, will be merged with the calling and
        called functions.
        
        Use this method to prune the graph, for example when hiding irrelevant
        functions. It preserves the execution profile.
        
        @param     function    The Function to hide.
        """
        # TODO Add call counts
        for call in function.incoming_calls():
            call.caller().add_inline_time( call.cumulative_time() )
        for call in function.outgoing_calls():
            call.callee().add_inline_time( call.inline_time() )
        self._remove_function( function )


    def treat_as_inlined(self, function):
        """
        Merge @p function with its callers, thereby pretending that it was an
        inline function.
        
        This method is handy for eliminating wrappers from the graph.

        The inline_time() of @p function will be added to its callers' inline
        execution times.  Its outgoing calls will also be added to its callers.
        
        However, be cautious when using this method: it cannot separate
        execution paths and therefore duplicates all outgoing calls. Suppose
        Function C is called by A and B; C invokes D and E. After inlining C,
        the graph will contain Calls from A to D and E, as well as from B to D
        and E.
        
        @param     function    The Function to be inlined into its callers.
        """
        for in_call in function.incoming_calls():
            in_call.caller().add_inline_time( in_call.inline_time() )
            for out_call in function.outgoing_calls():
                self._add_call(
                          in_call.caller(),
                          out_call.callee(),
                          out_call.primitive_callcount(),
                          out_call.total_callcount(),
                          out_call.inline_time(),
                          out_call.cumulative_time()
                      )
        self._remove_function( function )

    
    def _setdefault_function(self, file_line_name):
        """
        Fetch the Function identified by the @p name tuple; create a new
        Function if it does not yet exist.
        
        @param     file_line_name    A tuple @c (filename, line_number, name)
                                     uniquely identifying the Function.
                              
        @return    The Function identified by the @p file_line_name tuple; if
                   the tuple is new, return a new instance.
        
        @see Function.__init__()
        """
        if not file_line_name in self.__fln_index:
            return self._add_function( file_line_name )
        return self.__fln_index[ file_line_name ] 

    
    def _add_function(self, file_line_name):
        """
        Add a Function identified by @p file_line_name to the call graph. Raise
        a @c ValueError if it already exists.

        @param     file_line_name    A tuple @c (filename, line_number, name)
                                     uniquely identifying the Function.
        @exception ValueError        A function with this tuple already exists.
                              
        @return    The fresh Function instance created from the
                   @p file_line_name tuple.
        """
        if not file_line_name in self.__fln_index:
            function = Function( self, *file_line_name )
            # ( Outgoing Calls, Incoming Calls )
            self.__functions[ function ] = ( set(), set() )
            
            # Update indexes
            self.__fln_index[ file_line_name ] = function
            self.__namespace_index.setdefault( function.namespace(), set() ).add( function )
            
            return function
        message = "Function with this identifying triple already exists: {0}"
        raise ValueError( message.format( file_line_name ) )


    def _remove_function(self, function):
        """
        Remove @function from the call graph together with all incoming and
        outgoing Calls.
        
        @param    function    The Function to remove from the graph.
        """
        # Remove from indexes
        if function.namespace():
            absolute_name = "::".join( [ function.namespace(), function.name() ] )
        else:
            absolute_name = function.name()
        fln = ( function.filename(), function.line_number(), absolute_name )
        del self.__fln_index[ fln ]
        
        self.__namespace_index[ function.namespace() ].discard( function )
        if not self.__namespace_index[ function.namespace() ]:
            del self.__namespace_index[ function.namespace() ]
        
        # Remove all associated Calls
        for calls in self.__functions[ function ]:
            # Removing calls mutates the set; copy it to avoid confusion.
            for call in calls.copy():
                self._remove_call( call )
        
        # Remove Function
        assert( self.__functions[ function ] == ( set(), set() ) )
        del self.__functions[ function ]
        function._invalidate()

        
    def _add_call(self, caller, callee, primitive_calls, total_calls, inline_time, cumulative_time ):
        """
        Add a Call to the graph with the given profiling data between @p caller
        and @p callee.
        
        @return    The freshly constructed Call instance.
        
        @see Call for a description of parameters.
        """
        # TODO Prevent parallel edges
        call = Call( self,
                     primitive_calls,
                     total_calls,
                     inline_time,
                     cumulative_time
                 )
        self.__calls[ call ] = ( caller, callee )
        self._outgoing_calls( caller ).add( call )
        self._incoming_calls( callee ).add( call )
        return call
        
        
    def _remove_call(self, call):
        """
        Remove @p call from the graph.
        
        @param     call    The Call to remove from the graph.
        """
        # Unregister from associated Functions
        caller, callee = self.__calls[ call ]
        self._outgoing_calls( caller ).discard( call )
        self._incoming_calls( callee ).discard( call )
        
        # Remove Call
        del self.__calls[ call ]
        call._invalidate()
    

    def _outgoing_calls(self, function):
        """
        Get the set of outgoing Calls of @p function.
        
        @return    The set of Calls issued by @p function.
        """
        return self.__functions[ function ][ 0 ]
    
    
    def _incoming_calls(self, function):
        """
        Get the set of incoming Calls of @p function.
        
        @return    The set of Calls that represent the invocations of
                   @p function.
        """
        return self.__functions[ function ][ 1 ]


    def _caller(self, call):
        """
        Fetch the Function that invoked the @p call.
        
        @return    The Function issuing the @p call.
        """
        return self.__calls[ call ][ 0 ]

    
    def _callee(self, call):
        """
        Fetch the Function invoked in the @p call.
        
        @return    The called Function.
        """
        return self.__calls[ call ][ 1 ]



class CallGraphNode:
    """
    Base class for nodes of CallGraphs.
    
    The class provides the mechanisms that ensure correct ownership of nodes:
    all nodes belong to a unique CallGraph that manages all edge information.
    If a node wants to know its neighbors, it asks its owning CallGraph (for
    example via @c CallGraph._caller() and the like).
    
    When the node is removed, the graph invokes @c _invalidate(). Afterwards,
    _assert_valid() raises a @c ValueError.
    New node types should inherit from this class.
    """
    def __init__(self, callgraph):
        """
        Constructor for new nodes. It registers the @p callgraph as owner of
        the new node.
        
        Subclasses must invoke this constructor, for example via
        @c super().__init__(callgraph)
        
        @param     callgraph    The CallGraph to which the new node belongs.
        """
        self.__callgraph = callgraph
        
    def valid(self):
        """
        @return    @c True, if the node still belongs to its owning CallGraph;
                   @c False otherwise. 
        """
        return self.__callgraph is not None
    
    def _assert_valid(self):
        """
        Ascertain that the node is still element of its owning CallGraph.
        If that is not the case, raise a @c ValueError.
        
        Use this method as a guard in member functions operating on the
        graph (such as retrieving neighbors).
        """
        if self.valid():
            return
        raise ValueError( "this element is no longer part of a CallGraph" )
    
    def _callgraph(self):
        """
        @return    The CallGraph that owns this node.
        """
        return self.__callgraph
    
    def _invalidate(self):
        """
        Signal the node that it has been deleted from its graph.
        """
        self.__callgraph = None



from functools import reduce
from operator import add

class Function( CallGraphNode ):
    """
    Function objects represent called functions in a CallGraph; they originate
    in @c pstats.Stats entries and thus are identified by filename, line number,
    and function name. 
    
    The objects track their incoming and outgoing calls. It is therefore
    possible to traverse the graph along execution paths. Direct traversal to
    adjacent Functions is available from the caller() and callee() convenience
    methods.
    
    Lack of detail on the side of the @c cProfile module, however, makes it
    impossible to separate specific execution paths. Some information on the
    timing of a path is available from cumulative_time() in incoming_calls()
    because these values are the measured time it took to execute the function
    body and all invoked functions.
    
    The class further provides convenience methods to retrieve (accumulated)
    profiling information for the function. To get information about a specific
    invocation path, use Call objects.
    
    @see Call and CallGraph
    """
    def __init__(self, callgraph, filename, line_number, name, inline_time_offset=0):
        """
        Construct a new Function without connections.
        
        @param     callgraph   The CallGraph instance to which this node
                               belongs. (See CallGraphNode.)
        @param     filename    Name of the file that contains the
                               represented function's source code.
        @param     line_number Number of the first line of function code in
                               above file.
        @param     name        The function name. If @p name contains a double
                               color (@c ::), the last portion after the final
                               occurence will be interpreted as the function
                               name. The portion on the left will be the
                               function's namespace. (Thus, @c ns1::ns2::f
                               as @p name results in a name() of @c f and a
                               namespace() of @c ns1::ns2.
        """
        super().__init__( callgraph )
        self.__filename = filename
        self.__line_number = line_number
        if "::" in name:
            self.__namespace, self.__name = name.rsplit( "::", 1 )
        else:
            self.__namespace, self.__name = "", name
        self.__inline_time_offset = inline_time_offset

    def filename(self):
        """
        Get the name of the file that contains the source code of the
        represented function.
        
        @return    Name of the source code file of the represented function. 
        """
        return self.__filename
    
    def line_number(self):
        """
        Get the number of the first line of the represented function's code
        in filename().
        
        @return    Number of the line at which the code of the represented
                   function starts.
        """
        return self.__line_number
    
    def name(self):
        """
        Get the represented function's name.
        
        See __init__() for how this relates to the @c name entry of a
        @c (file_name, line_number, name) triple from @c pstats.Stats.
        
        @return    Name of the represented function.
        
        @see __init__()
        """
        return self.__name
    
    def namespace(self):
        """
        Get the represented function's namespace.
        
        See __init__() for how this relates to the @c name entry of a
        @c (file_name, line_number, name) triple from @c pstats.Stats.
        
        @return    Namespace of the represented function.
        
        @see __init__()
        """
        return self.__namespace
    
    def inline_time(self):
        """
        Retrieve the total time spent executing the function's body, ignoring
        the time spent in calls to other functions.
        
        This method sums the information over all execution paths. Use
        incoming_calls() to get the times of specific invocations.
        
        Use add_inline_time() to add execution time that does not appear in
        the graph (for example when deleting or merging Calls).
        
        This method raises a ValueError if the Function is no longer part of
        its owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return    The execution time for expressions in the function body.
                   Time spent in called functions does not add to this time.
        
        @see add_inline_time() 
        """
        inline_times = [ c.inline_time() for c in self.incoming_calls() ]
        return reduce( add, inline_times, self.__inline_time_offset )
    
    def cumulative_time(self):
        """
        Retrieve the total time spent executing the function. This includes
        the time spent in called functions.
        
        Times are accumulated over all execution paths. Use incoming_calls()
        to access information of a specific invocation.
        
        This method raises a ValueError if the Function is no longer part of
        its owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return    The total time it took to execute this function and all
                   the functions it called.
        """
        outgoing_times = [ c.cumulative_time() for c in self.outgoing_calls() ]
        return reduce( add, outgoing_times, self.inline_time() )

    def primitive_callcount(self):
        """
        Retrieve the number of times this function was called, not counting
        invocations via recursive loops.
        
        Call counts are added up over all execution paths. Use incoming_calls()
        to access information of a specific invocation.
        
        This method raises a ValueError if the Function is no longer part of
        its owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return    How often the function was called except for recursive
                   loops.
        """ 
        incoming_callcounts = [ c.primitive_callcount() for c in self.incoming_calls() ]
        return reduce( add, incoming_callcounts, 0 )
    
    def total_callcount(self):
        """
        Retrieve the total number of times this function was called, including
        invocations via recursive loops.
        
        Call counts are added up over all execution paths. Use incoming_calls()
        to access information of a specific invocation.
        
        This method raises a ValueError if the Function is no longer part of
        its owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return    How often the function was called.
        """ 
        incoming_callcounts = [ c.total_callcount() for c in self.incoming_calls() ]
        return reduce( add, incoming_callcounts, 0 )
    
    def outgoing_calls(self):
        """
        Get a list of Calls invoked by this function, that is, the direct
        successors in the CallGraph.
        
        @return    A list of outgoing calls.
        """
        self._assert_valid()
        return self._callgraph()._outgoing_calls( self )
    
    def incoming_calls(self):
        """
        Get a list of Calls to this function, that is, the direct predecessors
        in the CallGraph.
        
        This method raises a ValueError if the Function is no longer part of
        its owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return    A list of incoming calls.
        """
        self._assert_valid()
        return self._callgraph()._incoming_calls( self )
    
    def callers(self):
        """
        Get a list of all Functions that called this Function.
        
        This method raises a ValueError if the Function is no longer part of
        its owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return    The list of callers.
        """
        self._assert_valid()
        return [ call.caller() for call in self.incoming_calls() ]
    
    def callees(self):
        """
        Get a list of Functions called by this Function.
        
        This method raises a ValueError if the Function is no longer part of
        its owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return    The list of callees.
        """
        self._assert_valid()
        return [ call.callee() for call in self.outgoing_calls() ]

    def add_inline_time(self, time):
        """
        Add time to the offset used to calculate inline_time().
        
        @see inline_time()
        """
        self.__inline_time_offset += time

    def __str__(self):
        return "Function '{name}'".format( name = self.__name )
        


class Call ( CallGraphNode ):
    """
    Call objects represent Function invocations in a CallGraph; they come from
    @c pstats.Stats entries and thus provide information on the call counts
    and execution time.
    
    Lack of detail on the side of the @c cProfile module, however, makes it
    impossible to separate specific execution paths. Some information on the
    timing of a path is available from cumulative_time() because this value
    is the measured time it took to execute the callee() function body and
    all functions invoked up to the return.
    
    The class further provides information about a specific invocation path.
    Use the convenience methods Function.inline_time() and
    Function.cumulative_time() to retrieve (accumulated) profiling information.
    
    @see Function and CallGraph
    """
    def __init__(self, callgraph, primitive_callcount, total_callcount, inline_time, cumulative_time):
        """
        Create a new Call with the given execution profile.
        
        @param     callgraph           The CallGraph owning this Call.
        @param     primitive_callcount The number of times this Call was issued
                                       (without recursive calls).
        @param     total_callcount     The number of times this Call was issued
                                       (including recursive calls).
        @param     inline_time         The time it took to execute the function
                                       body when invoked from the caller(),
                                       without the time other functions took.
        @param     cumulative_time     The time it took to execute the function
                                       when invoked from the caller, including
                                       sub calls.
        """
        super().__init__( callgraph )        
        self.__primitive_callcount = primitive_callcount
        self.__total_callcount = total_callcount
        self.__inline_time = inline_time
        self.__cumulative_time = cumulative_time
        
    def caller(self):
        """
        Return the Function that issued this call.
        
        This method raises a ValueError if the Call is no longer part of its
        owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return The calling Function.
        """
        self._assert_valid()
        return self._callgraph()._caller( self )
    
    def callee(self):
        """
        Return the Function that received this call.
        
        This method raises a ValueError if the Call is no longer part of its
        owning CallGraph; see CallGraphNode.
        
        @exception    ValueError  The Function was already deleted from the call
                                  graph.
        
        @return The called Function.
        """
        self._assert_valid()
        return self._callgraph()._callee( self )
    
    def primitive_callcount(self):
        """
        Return the number of times this Call was issued without recursive
        calls.
        
        @return    How often the Call was issued, excluding calls through
                   recursive loops.
        """
        return self.__primitive_callcount
    
    def total_callcount(self):
        """
        Return the number of times this Call was issued including recursive
        calls.
        
        @return    How often the Call was issued, including calls through
                   recursive loops.
        """
        return self.__total_callcount
    
    def inline_time(self):
        """
        Return the time it took to execute the function body when invoked
        by caller(), without the time the called functions took.
        
        @return    The execution duration without subcalls when called by
                   caller().
        """
        return self.__inline_time
    
    def cumulative_time(self):
        """
        Return the time it took to execute the function when invoked by
        caller(), including the execution time of sub calls.

        @return    The total execution duration when called by caller().
        """
        return self.__cumulative_time
    
    def __str__(self):
        return "{0} --> {1}".format( self.caller(), self.callee() )