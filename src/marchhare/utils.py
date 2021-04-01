#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2018-03-23

"""
Utils3.py
James Watson, 2021 April
[M]odule [ARCH]ive for a [H]obby [A]nd [R]esearch [E]nvironment
General Helper functions
"""

# ~~~ Imports ~~~
# ~~ Standard ~~
import os , builtins , operator , time
from math import pi , sqrt
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
_AUTOLOAD_CONST = True

########## PATH AND ENVIRONMENT ###################################################################

def install_constants():
    """ Add the constants that you use the most """
    # NOTE: No, I don't feel guilty for adding keywords to Python in this way
    if 'EPSILON' not in dir( builtins ):
        builtins.EPSILON = 1e-7 # ------ Assume floating point errors below this level
        builtins.infty   = 1e309 # ----- URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
        builtins.endl    = os.linesep #- Line separator
        builtins.pyEq    = operator.eq # Default python equality
        builtins.piHalf  = pi/2
        print( "Constants now available in `builtins`" )

def test_constants():
    """ Test if the standard MARCHHARE constants have been loaded """
    try:
        EPSILON
        infty
        endl 
        pyEq 
        piHalf
        return True
    except NameError:
        return False


if _AUTOLOAD_CONST:
    install_constants()
    assert test_constants() , "MARCHHARE constants FAILED to load!"


def fetch_module_name_from_path( name , path ):
    """ Import a file to the global scope """
    spec = importlib.util.spec_from_file_location( 
        name , 
        os.path.expanduser( path )
    )
    modl = importlib.util.module_from_spec( spec )
    spec.loader.exec_module( modl )
    return modl


def add_expanded_path( path ):
    """ Expand the path and add to the system path """
    sys.path.append(  os.path.expanduser( path )  )



########## Utilities ##############################################################################


def get_progress_bar( div = 25, char = '>', between = ' ', counter = 0 ):
    """ Enclose a counter and return a function that emits a char every `div` calls """
    
    def progchar():
        """ Emit progress character ever `div` iter """
        nonlocal div, char, between, counter
        counter += 1
        if counter % div == 0:
            print( char , end = between , flush = 1 )
            return True
        else:
            return False
    
    return progchar



########## File Operations ########################################################################


def ensure_dir( dirName , gracefulErr = 1 ):
    """ Create the directory if it does not exist """
    if not os.path.exists( dirName ):
        try:
            os.makedirs( dirName )
        except Exception as err:
            if gracefulErr:
                print( "ensure_dir: Could not create" , dirName , '\n' , err )
            else:
                raise IOError( "ensure_dir: Could not create" + str( dirName ) + '\n' + str( err ) )
                
                
def npy_to_array( path, dtype = 'float' ):
    """ Return the NPY file as an array """
    return np.array( np.load( path ) ).astype( dtype = dtype )


def listpaths( srcDir ):
    """ Return all the names in `srcDir` as full paths """
    rtnPaths = []
    srcNames = os.listdir( srcDir )
    for name in srcNames:
        rtnPaths.append( os.path.join( srcDir, name ) )
    return rtnPaths


def change_filename_EXT( name_or_path, nuEXT, suppressPath = 0 ):
    """ Return a version of `name_or_path` so that that it has a `nuEXT` """
    parts = str( name_or_path ).split('/')
    if len( parts ) > 1:
        name    = parts[-1]
        path    = parts[:-1]
        wasPath = 1
    else:
        name    = parts[0]
        path    = ""
        wasPath = 0
    nuName = name.split('.')[0] + '.' + nuEXT
    if suppressPath or (not wasPath):
        return nuName
    else:
        return os.path.join( *path, nuName )


########## Dictionary Queries #####################################################################


def set_val_if_dict( dct, key, val ):
    """ Set the { ... `key`:`val` ... } only if `dct` is a dictionary """
    try:
        dct[ key ] = val
        return True
    except (TypeError, KeyError):
        return False


def p_dict_has_key( dct, key ):
    """ If `dct` is a dictionary AND has the `key`, then return True, Otherwise return False """
    return ( isinstance( dct, dict ) and (key in dct) )


def get_val_by_key( dct, key, defaultVal = None ):
    """ Fetch the value assoc with `key` within `dct` if the key exists, Else """
    try:
        return dct[ key ]
    except (TypeError, KeyError):
        return defaultVal



########## Logical Ops ############################################################################
    
    
def XNOR( A, B ):
    """ Return the Exclusive-NOR of `A` and `B` """
    return int( ( A or (not B) )  and  ( (not A) or B ) )


def AND( *args ):
    """ 'AND' all of the `args` together and return the result """
    result = 1
    for arg in args:
        result = result and arg
    return int( result )