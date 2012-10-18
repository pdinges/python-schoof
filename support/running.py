# -*- coding: utf-8 -*-
# Copyright (c) 2010--2012  Peter Dinges <pdinges@acm.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Support classes for feeding files of parameter lists to algorithms;
furthermore support for the profiling of algorithms.

@package   support.running
@author    Peter Dinges <pdinges@acm.org>
"""

import cProfile
import os
import platform
import resource
import time

from contextlib import closing

class DataRecorder:
    """
    DataRecorder objects concentrate the tools for collecting profiles of
    execution and resource usage. They support performance analysis by taking
    care that all relevant information will be recorded.

    When a DataRecorder is created, it starts the profiler and records the
    current time, memory consumption, and cpu utilization. When the recorder is
    stopped, it again records the time, memory and cpu usage. After stopping
    the recorder, the execution profile and resource usage data may be dumped
    into a set of files for later analysis. 

    For example, suppose you want to collect profiling information of an
    algorithm implementation. The following code creates a profile and measures
    the used resources; finally it writes them to the files @c algo.profile and
    @c algo.timing
    
    @code
    dr = DataRecorder( "algo" )    # Start recorder
    algo( some_parameter_set )     # Invoke algorithm
    dr.stop()
    dr.dump()                      # Write the recorded information to disk
    @endcode
    
    @note      It is the user's responsibility to dump() the collected
               information; a DataRecorder will not write information to the
               disk on its own. This allows throwing away incomplete
               data sets.
               
    @see The @c cProfile and @c resource modules
    """
    
    def __init__(self, basename, path=os.curdir):
        """
        Construct a new DataRecorder that will write the gathered information
        into files derived from the given @p basename in @p path.
        
        The output files will be @c basename.profile and @c basename.timing
        in @p path. The new instance immediately reserves these files, so they
        will be available when the data is stored. That is why the @p basename
        and @p path are parameters to the constructor instead of dump(), which
        actually writes out the data.
        
        @param     basename    A string for use as the first part of the output
                               file names; these have the extensions
                               @c .profile and @c .timing.
        @param     path        Create the output files in the directory
                               identified by this name string.
        """ 
        # Fail early: immediately try to open files.
        timing_filename = self._available_filename(path, basename, "timing")
        self.__timing_file = open( timing_filename, mode="wt" ) 

        # Actually, Profile expects a filename. By opening the file
        # here, we make sure it will be available when the profiling
        # is over.
        profile_filename = self._available_filename(path, basename, "profile")
        self.__profile_file = open( profile_filename, mode="w" )
        
        self.__stop_time = None
        self.__stop_resources = None

        # Use milliseconds for all times to ease further processing
        self.__start_time = time.time()
        self.__start_resources = resource.getrusage( resource.RUSAGE_SELF )
        
        self.__profile = cProfile.Profile()
        self.__profile.enable( builtins=False )


    def is_running(self):
        """
        Check whether the object currently records data.
        
        @return    @c True, if execution data is being recorded at the moment;
                   @c False otherwise.
        """
        # There is no way to restart; stop() is the only method setting
        # this variable.
        return self.__stop_time is None
    

    def stop(self):
        """
        End data acquisition.
        
        @note  There is no way to restart the DataRecorder.  
        """
        if not self.is_running():
            return
        
        # Stop profiling and resource monitoring.
        self.__profile.disable()
        self.__stop_time = time.time()
        self.__stop_resources = resource.getrusage( resource.RUSAGE_SELF )


    def dump_data(self, extra_information = {}):
        """
        Write the collected information to the files supplied to the
        constructor.
        
        Calling this method implies a call of stop(); thus data recording ends.
        
        @param     extra_information   A dictionary with additional entries to
                                       the @c .timing file. Use this, for
                                       example, to record the results of the
                                       profiled execution. 
        """
        if self.is_running():
            self.stop()
        
        # Dump the call profile. And: yes, this is a race condition.
        self.__profile_file.close()
        self.__profile.dump_stats( self.__profile_file.name )

        # Compute the resource usage
        wall_time = self.__stop_time - self.__start_time
        user_time =  self.__stop_resources.ru_utime - self.__start_resources.ru_utime
        sys_time = self.__stop_resources.ru_stime - self.__start_resources.ru_stime
        cpu_time = user_time + sys_time
        max_rss = self.__stop_resources.ru_maxrss
        
        with closing( self.__timing_file ) as timing_file:
            info = [ "node: {0}".format( platform.node() ),
                     "platform: {0}".format( platform.platform() ),
                     "python: {0}".format( platform.python_version() ),
                     "date (Y/M/D h:m:s): {0}".format(
                              datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                          ),
                     "wall time (s): {0}".format( wall_time ),
                     "user time (s): {0}".format( user_time ),
                     "sys time (s): {0}".format( sys_time ),
                     "cpu time (s): {0}".format( cpu_time),
                     "max memory (kB): {0}".format( max_rss ),
                 ]
            for key, value in sorted( extra_information.items() ):
                info.append( "{0}: {1}".format( key, value ) )
            
            # Finally, dump the resource information
            print( "\n".join( info ), file=timing_file )

        
    @staticmethod
    def _available_filename(path, basename, extension):
        """
        Find and return the next available free combination of @p basename,
        @p extension, and some integer.
        """
        filename = "{base}.{ext}".format( base = basename, ext = extension )
        if not os.path.exists( os.path.join(path, filename ) ):
            return os.path.join(path, filename )
        
        # TODO: Find a better method to generate alternative file names.
        #       The limit 25 is completely arbitrary.
        for i in range(1, 26):
            filename = "{base}-{i}.{ext}".format(
                                     base = basename,
                                     i = i,
                                     ext = extension
                                 )
            if not os.path.exists( os.path.join(path, filename ) ):
                return os.path.join(path, filename )
            
        raise IOError( "suitable output filenames already taken" )


from contextlib import closing, contextmanager

import fcntl
import os.path

class ParallelParser:
    """
    A simple parser for "separated value" (SV) files that makes sure that every
    line of the file is yielded in only one instance operating on it.
    
    Use this class, for instance, to have multiple instances of a program
    operate on the same parameter list. The class makes sure that every line
    is read by only one instance of the program.
    
    The different instances of ParallelParser synchronize their operation
    through a shared text file. File system locking prevents concurrent reads
    and writes. Since this works even on networked file systems, parser
    instances can in this way communicate across a network. The communication
    file is named @c file.pipe, where @c file is the name of the parsed file. 
    
    To iterate over a file @c foo.txt line by line, you could use the following
    code:
    @code
    for line in ParallelParser( "foo.txt" ):
        # Do something with line
    @endcode
    
    Now suppose you have a computation intensive algorithm @c f(x,y) and you
    want to apply it once to the parameter set of every line in the parameter
    list in @c param.lst. Thus you write a program like
    @code
    for params in ParallelParser( "param.lst", "," ):
        f(*params)    # Expand the tuple params
    @endcode
    If you start, say, two instances of the program and the contents of
    @c param.lst are
    @code
    1,2
    3,4
    5,6
    @endcode
    then one instance will receive the tuple @c (1,2) and the other @c (3,4).
    The final tuple @c (5,6) will be read by whichever instance finishes first.
    
    @note      This class is designed for use cases where each yielded line
               takes a long time to process. Synchronization by file locking
               probably involves a large overhead, so fast processing with many
               parsers at the same time will scale badly. 
    
    @see __iter__() for a detailed description which lines the parser yields.
    """
    
    def __init__(self, file, separator=" "):
        """
        Construct a new ParallelParser for iterating over @p file.
        
        @param     file        The name of the file to be parsed. It als serves
                               as the first part of the name of the shared
                               communication file @c file.pipe.
        @param     separator   The parser splits the entries in each line of
                               @p file by @p separator. For example, to
                               retrieve a the entries of a comma separated
                               value (CSV) file as a tuple, use "," as
                               separator. The line "1,2,3" then yields the
                               tuple @c (1,2,3); with a space as separator, the
                               parser yields a tuple with one entry: the 
                               string "1,2,3".
        """
        self.__separator = separator
        self.__file = open( file, "rt" )
        
        directory = os.path.dirname( file )
        pipe_file = "{}.pipe".format( os.path.basename( file ) )
        self.__pipe = open( os.path.join( directory, pipe_file ), "at+" )
        self.__locked = False


    def __del__(self):
        """
        Destruct a ParallelParser and unregister it from the shared
        communication file. If the instance was the last to use the file, it
        also removes the file.
        """
        with self.__lock() as data:
            remove_pipe = True if data[0] == 0 else False

        if remove_pipe:
            self.__pipe.close()
            os.remove( self.__pipe.name )
        

    def __iter__(self):
        """
        Interface method to support line by line iteration with the @c for
        statement.
        
        Every line is split with the @c separator provided to __init__(),
        the method thus returns a tuple of contents. For example, the line
        "1,2,3" will yield @c (1,2,3) if the @c separator is ",".
        
        The parser skips empty lines and comment lines, that is, lines that
        start with zero or more spaces followed by a hash '#'.
        
        @return    A tuple of the line contents, split by @c separator.
        """
        # Register: increase the number of parsers
        with self.__lock() as data:
            parsers, current_offset, current_line = data
            self.__update( parsers + 1, current_offset, current_line )
        
        # Iterate until the file ends
        # readline() is just at test for EOF; file will be seek()ed anyway
        line = self.__file.readline()
        while line:
            with self.__lock() as data:
                parsers, current_offset, current_line = data
                self.__file.seek( current_offset )
                line = self.__file.readline()
                current_line += 1

                # Skip over empty lines and comments until the file ends
                while line and (not line.strip() or line.strip().startswith( "#" )):
                    line = self.__file.readline()
                    current_line += 1
            
            # File might have ended already
            if line:
                self.__update( parsers, self.__file.tell(), current_line )
                yield current_line, tuple( line.strip().split( self.__separator ) )
        
        # Unregister: decrease the number of parsers
        with self.__lock() as data:
            parsers, current_offset, current_line = data
            self.__update( parsers - 1, current_offset, current_line )

        raise StopIteration
    
        
    @contextmanager
    def __lock(self):
        """
        Obtain a lock on the shared communication file.
        
        Use this @c contextmanager with the @c with statement.
        
        @see The @c contextlib module.
        """
        previously_locked = self.__locked
        fcntl.lockf( self.__pipe, fcntl.LOCK_EX )
        self.__locked = True

        try:
            self.__pipe.seek( 0 )
            parsers, offset, line = map(int, self.__pipe.readline().split( " " ) )
        except ValueError:
            parsers, offset, line = 0, 0, 0
        
        yield parsers, offset, line
        
        self.__locked = previously_locked
        if not previously_locked:
            fcntl.lockf( self.__pipe, fcntl.LOCK_UN )


    def __update(self, parsers, offset, line):
        """
        Update the contents of the shared communication file, for example with
        the new input file position after a line has been read.
        """
        with self.__lock():
            self.__pipe.seek( 0 )
            self.__pipe.truncate()
            print( parsers, offset, line, file=self.__pipe )
            # Flush the update to disk to circumvent caching, which might delay
            # propagation of the update to other parsers.
            self.__pipe.flush()
        

import os
import signal
import sys

from datetime import datetime
from optparse import OptionParser, OptionGroup

class AlgorithmRunner:
    """
    An AlgorithmRunner allows fast creation of a feature-rich command line
    program that applies an algorithm to sets of parameters while recording
    the execution profile.
    
    For example, say you have an algorithm (that is, a callable) @c f(x,y) and
    want to apply it to every parameter set listed in the file @c params.lst.
    Furthermore suppose you want to record the calling profile (see the
    @c cProfile module), the execution time, and the result of each
    application. Then a script containing the following code is your program
    (@c prog.py):
    @code
    def f(x, y, output):
        # Do calculations here
        print( "The ultimate truth is:", result, file=output )
        return result
    
    r = AlgorithmRunner( f )
    r.run()
    @endcode
    You then invoke
    @code
    python prog.py -d profiles/ -p -i params.lst
    @endcode
    and it will apply @c f() to each line of @c params.lst and store the
    respective profile and timing information in the @c profiles/ directory.
    Use the "-h" command line switch to get a list of all available options.
    
    AlgorithmRunner uses ParallelParser to read the input files. It therefore
    supports multiple program instances working on the same parameter list.
    Each line will be read by only one instance. 
    
    Send the signal @c SIGUSR1 to an AlgorithmRunner instance to "soft" kill
    it. It will then properly shut down, unregistering its ParallelParser etc.,
    all of which does not happen if it is just killed.
    
    @see ParallelParser and DataRecorder
    """
    
    def __init__(self, algorithm, arguments=sys.argv[1:], algorithm_version="<unknown>" ):
        """
        Construct a new AlgorithmRunner for executing the given @p algorithm.
        
        @param     algorithm   A callable that takes @f$ n+1 @f$ arguments,
                               where @f$ n @f$ is the number of entries per line
                               in parameter lists (or given on the command line).
                               The last argument is @c output, which gives the
                               algorithm a way to write logging information.
                               The return value of @p algorithm will be stored
                               alongside the timing information.
        @param     arguments   A list of command line argument strings for the
                               runner.
        @param     algorithm_version   The algorithm version will be stored
                                       together with the timing information.
                                       Use it to recall which revision of an
                                       algorithm was used in a particular
                                       profile.
        """
        self.__algorithm = algorithm
        self.__algorithm_version = algorithm_version
        options, arguments = self._parse_arguments( arguments, algorithm_version )
        
        # __input is a list of pairs (<name>, <iterable>);
        # <iterable> is expected to return pairs (<item_number>, <item>).
        # See run().
        self.__input = []
        if arguments:
            self.__input.append( ( "<stdin>", [ (0, tuple( arguments ) ) ] ) )
        # Fail early: immediately try to open the file
        if options.input_file:
            input_parser = ParallelParser( options.input_file )
            self.__input.append( ( options.input_file, input_parser ) )
        
        # Initialize the remaining attributes.
        self._open_output( options.output_file )

        self.__create_profile = options.create_profile
        self.__profile_directory = options.profile_directory
        self.__timelimit = options.timelimit
        
        if self.__create_profile:
            self._ensure_directory( options.profile_directory )


    def run(self):
        """
        Start execution and apply the algorithm to all provided parameters.
        """
        if not self.__input:
            self.__parser.print_usage()
        
        # Listen for signals to allow the user to interrupt the execution.
        signal.signal( signal.SIGUSR1, self._raise_signal )
        
        terminated = False    
        for name, iterable in self.__input:
            for item_number, item in iterable:
                try:
                    # Raise a TimeOutException if the pass takes too long
                    if self.__timelimit > 0:
                        signal.signal( signal.SIGALRM, self._raise_signal )
                        signal.alarm( self.__timelimit )
                        
                    if self.__create_profile:
                        dump_filename = self._generate_dump_name( *item )
                        recorder = DataRecorder(
                                        dump_filename,
                                        self.__profile_directory,
                                        
                                    )
                    try:
                        result = self.__algorithm( *item, output=self.__output)
                    
                    except TimeOutException:
                        terminated = "timeout after {0}s".format( self.__timelimit )
                    
                    except SoftKillException:
                        terminated = "killed by user signal"
                    
                    if self.__create_profile:
                        recorder.stop()
                        extra_information = {
                                     "algorithm": self.__algorithm.__name__,
                                     "version": self.__algorithm_version,
                                     "input": item,
                                 }

                        if terminated:
                            extra_information["terminated"] = terminated
                        else:
                            extra_information["result"] = result

                        recorder.dump_data( extra_information )
    
                except TypeError:
                    message = ">>> Algorithm input in '{name}':{i} has the " \
                              "wrong type. Ignoring it."
                    print( message.format(
                                  name = name,
                                  i = item_number + 1
                              ),
                              file = sys.stderr
                          )
                except IOError:
                    pass # output failure
                
                if terminated:
                    message = ">>> Terminated prematurely. Reason: {0}"
                    print( message.format( terminated ), file=sys.stderr ) 
                    return 1
        
        # Stop listening for signals.
        signal.signal( signal.SIGUSR1, signal.SIG_DFL )
        signal.signal( signal.SIGALRM, 0 )


    def _ensure_directory(self, path):
        """
        Make sure that the directory @p path exists.
        """
        if not os.path.exists( path ):
            os.makedirs( path )
            
        elif not os.path.isdir( path ):
            message = "file already exists and is not a path: '{0}'"
            raise IOError( message.format( path ) )


    # TODO: Distinguish results, errors, and log
    def _open_output(self, filename, default = sys.stdout):
        """
        Make sure that @p filename is ready for writing.
        """
        if filename and os.path.exists( filename ):
            raise IOError( "output file already exists" )
        
        if filename:
            self.__output = open( filename, mode="wt" )
        else:
            self.__output = default

    
    def _generate_dump_name(self, *input_item):
        """
        Return a generic file name for profiling information.
        """
        name = "{date}-{args}".format(
                   date = datetime.now().strftime("%Y%m%d_%H%M%S"),
                   args = "_".join( input_item )
               )
        return name


    def _parse_arguments( self, arguments, algorithm_version ):
        """
        Parse the command line arguments and set the options accordingly.
        """
        usage_string = """%prog <algorithm input>"""
        version_string ="""%prog {0}""".format( algorithm_version )
        
        parser = OptionParser( usage = usage_string, version = version_string )
        
        parser.add_option( "-t",
                           "--timelimit",
                           dest="timelimit",
                           type="int",
                           default=0,
                           metavar="SECONDS",
                           help="stop execution if an algorithm pass takes "
                           "longer than SECONDS seconds."
                       )

        io_group = OptionGroup(parser, "Input and Output")
        io_group.add_option( "-i", "--input-file", metavar="FILE",
                             dest="input_file",
                             type="string",
                             default=None,
                             help="read input line by line from FILE")
        
        io_group.add_option( "-o", "--output-file", metavar="FILE",
                             dest="output_file",
                             type="string",
                             default=None,
                             help="write results to FILE")

        # TODO: Add overwrite option.
        parser.add_option_group( io_group )

        
        profiling_group = OptionGroup(parser, "Profiling")
        profiling_group.add_option( "-p", "--create-profile",
                           action="store_true", dest="create_profile",
                           default=False,
                           help="create a profile for each algorithm run"
                           )
        
        profiling_group.add_option( "-d", "--profile-directory", metavar="DIR",
                           dest="profile_directory",
                           type="string",
                           default=os.getcwd(),
                           help="store profiles in directory DIR")
        
        parser.add_option_group( profiling_group )
        
        self.__parser = parser
        return parser.parse_args( arguments )
    
    
    def _raise_signal( self, signum, frame ):
        """
        Asynchronous signal handler that raises the respective exceptions.
        
        @see TimeOutException, SoftKillException
        """
        if signum == signal.SIGALRM:
            raise TimeOutException
        elif signum == signal.SIGUSR1:
            raise SoftKillException


class TimeOutException( Exception ):
    """
    An @c Exception to signal that an algorithm pass in the AlgorithmRunner
    exceeded the time limit.
    """
    pass

class SoftKillException( Exception ):
    """
    An @c Exception to signal that the user demanded the AlgorithmRunner
    to terminate.
    """
    pass
    