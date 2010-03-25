# -*- coding: utf-8 -*-
# $Id$

import cProfile
import os
import platform
import resource
import time

from contextlib import closing

class DataRecorder:
    """
    Profiling and resource information recorder.
    
    Data acquisition starts with object creation. After stopping
    the recording, the data can be dumped to a set of files.
    """
    def __init__(self, basename, path=os.curdir):
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
        # There is no way to restart; stop() is the only method setting
        # this variable.
        return self.__stop_time is None
    

    def stop(self):
        if not self.is_running():
            return
        
        # Stop profiling and resource monitoring.
        self.__profile.disable()
        self.__stop_time = time.time()
        self.__stop_resources = resource.getrusage( resource.RUSAGE_SELF )


    def dump_data(self, extra_information = {}):
        if self.is_running():
            self.stop()
        
        # Yes, this is a race condition.
        self.__profile_file.close()
        self.__profile.dump_stats( self.__profile_file.name )

        wall_time = self.__stop_time - self.__start_time
        user_time =  self.__stop_resources.ru_utime - self.__start_resources.ru_utime
        sys_time = self.__stop_resources.ru_stime - self.__start_resources.ru_stime
        cpu_time = user_time + sys_time
        max_rss = self.__stop_resources.ru_maxrss
        
        with closing( self.__timing_file ) as timing_file:
            print( "platform: {0}".format( platform.platform() ), file = timing_file )
            print( "python: {0}".format( platform.python_version() ), file = timing_file )
            print( "wall time (s): {0}".format( wall_time ), file = timing_file )
            print( "user time (s): {0}".format( user_time ), file = timing_file )
            print( "sys time (s): {0}".format( sys_time ), file = timing_file )
            print( "cpu time (s): {0}".format( cpu_time), file = timing_file )
            print( "max memory (kB): {0}".format( max_rss ), file = timing_file )
            for key, value in sorted( extra_information.items() ):
                print( "{0}: {1}".format( key, value ), file = timing_file )

        
    @staticmethod
    def _available_filename(path, basename, extension):
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
    A simple parser for "separated value" (SV) files. Every line of the parsed
    file is yielded in only one instance operating on it.
    
    Use this class, for instance, to have multiple instances of a program
    operate on the same parameter list. The class makes sure that every line
    is read by only one instance of the program.
    
    The parser supports iterating over a SV file line by line and receiving
    the values from each line as a tuple.
    """
    def __init__(self, file, separator=" "):
        self.__separator = separator
        self.__file = open( file, "rt" )
        
        directory = os.path.dirname( file )
        pipe_file = "{}.pipe".format( os.path.basename( file ) )
        self.__pipe = open( os.path.join( directory, pipe_file ), "at+" )
        self.__locked = False

    def __del__(self):
        with self.__lock() as data:
            remove_pipe = True if data[0] == 0 else False

        if remove_pipe:
            self.__pipe.close()
            os.remove( self.__pipe.name )
        

    @contextmanager
    def __lock(self):
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
        with self.__lock():
            self.__pipe.seek( 0 )
            self.__pipe.truncate()
            print( parsers, offset, line, file=self.__pipe )
            self.__pipe.flush()

        
    def __iter__(self):
        # Register: increase the number of parsers
        with self.__lock() as data:
            parsers, current_offset, current_line = data
            self.__update( parsers + 1, current_offset, current_line )
        
        # Iterate until the file ends
        line = self.__file.readline()
        while line:
            with self.__lock() as data:
                parsers, current_offset, current_line = data
                self.__file.seek( current_offset )
                line = self.__file.readline()
                current_line += 1

                while line and not line.strip() and line.strip().startswith( "#" ):
                    line = self.__file.readline()
                    current_line += 1
            
            if line:
                self.__update( parsers, self.__file.tell(), current_line )
                yield current_line, tuple( line.split( self.__separator ) )
        
        with self.__lock() as data:
            parsers, current_offset, current_line = data
            self.__update( parsers - 1, current_offset, current_line )

        raise StopIteration
        
            

import os
import sys

from datetime import datetime
from optparse import OptionParser, OptionGroup

class AlgorithmRunner:
    def __init__(self, algorithm, arguments=sys.argv[1:], algorithm_version="<unknown>" ):
        self.__algorithm = algorithm
        self.__algorithm_version = algorithm_version
        options, arguments = self._parse_arguments( arguments, algorithm_version )
        
        # __input is a list of pairs (<name>, <iterable>);
        # <iterable> is expected to return pairs (<item_number>, <item>).
        # See run().
        self.__input = [ ( "<stdin>", [ (0, tuple( arguments ) ) ] ) ]
        # Fail early: immediately try to open the file
        if options.input_file:
            input_parser = ParallelParser( options.input_file )
            self.__input.append( ( options.input_file, input_parser ) )
        
        # Initialize the remaining attributes.
        self._open_output( options.output_file )

        self.__create_profile = options.create_profile
        self.__profile_directory = options.profile_directory
        
        if self.__create_profile:
            self._ensure_directory( options.profile_directory )


    def run(self):
        for name, iterable in self.__input:
            for item_number, item in iterable:
                try:
                    if self.__create_profile:
                        dump_filename = self._generate_dump_name( *item )
                        recorder = DataRecorder(
                                        dump_filename,
                                        self.__profile_directory,
                                        
                                    )
                    
                    result = self.__algorithm( *item, output=self.__output)
                    
                    if self.__create_profile:
                        recorder.stop()
                        extra_information = {
                                     "algorithm": self.__algorithm.__name__,
                                     "version": self.__algorithm_version,
                                     "input": item,
                                     "result": result
                                 }
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


    def _ensure_directory(self, path):
        if not os.path.exists( path ):
            os.makedirs( path )
            
        elif not os.path.isdir( path ):
            message = "file already exists and is not a path: '{0}'"
            raise IOError( message.format( path ) )


    # TODO: Distinguish results, errors, and log
    def _open_output(self, filename, default = sys.stdout):
        if filename and os.path.exists( filename ):
            raise IOError( "output file already exists" )
        
        if filename:
            self.__output = open( filename, mode="wt" )
        else:
            self.__output = default

    
    def _generate_dump_name(self, *input_item):
        name = "{date}-{args}".format(
                   date = datetime.now().strftime("%Y%m%d_%H%M%S"),
                   args = "_".join( input_item )
               )
        return name


    def _parse_arguments( self, arguments, algorithm_version ):
        usage_string = """%prog <algorithm input>"""
        version_string ="""%prog {0}""".format( algorithm_version )
        
        parser = OptionParser( usage = usage_string, version = version_string )

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
        
        return parser.parse_args( arguments )
    