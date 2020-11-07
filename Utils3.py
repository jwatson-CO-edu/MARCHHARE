#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2018-03-23

"""
Utils3.py
James Watson, 2019 April
[M]odule [ARCH]ive for a [H]obby [A]nd [R]esearch [E]nvironment
Helper functions
NOTE: This file is the 3.6 replacement for the 2.7 "marchhare.py"
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

# === PATH AND ENVIRONMENT ===========================================================================================================

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

if _AUTOLOAD_CONST:
    install_constants()
    
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

# ___ END PATH & ENV _________________________________________________________________________________________________________________


# === STRING OPERATIONS ==============================================================================================================

def format_dec_list( numList , places = 2 ): 
    """ Return a string representing a list of decimal numbers limited to 'places' """
    rtnStr = "[ "
    for nDex , num in enumerate( numList ):
        if isinstance( numList , np.ndarray ):
            scalar = num.item()
        else:
            scalar = num 
        if nDex < len(numList) - 1:
            rtnStr += ('{0:.' + str( places ) + 'g}').format( scalar ) + ' , '
        else:
            rtnStr += ('{0:.' + str( places ) + 'g}').format( scalar )
    rtnStr += " ]"
    return rtnStr

def pretty_list( pList ):
    """ Print a list that is composed of the '__str__' of each of the elements in the format "[ elem_0 , ... , elem_n ]" , 
    separated by commas & spaces """
    prnStr = "[ "
    for index , elem in enumerate( pList ):
        if index < len( pList ) - 1:
            prnStr += str( elem ) + " , "
        else:
            prnStr += str( elem ) + " ]"
    return prnStr

def yesno( pBool ):
    """ Return YES if True, Otherwise return NO """
    return ( "YES" if pBool else "NO" )

nowTimeStamp = lambda: datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # http://stackoverflow.com/a/5215012/893511
""" Return a formatted timestamp string, useful for logging and debugging """

nowTimeStampFine = lambda: datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f') # http://stackoverflow.com/a/5215012/893511
""" Return a formatted timestamp string, useful for logging and debugging """

def lists_as_columns_with_titles( lists , titles = [] , padSpaces = 4 , output = 0 ):
    """ Return a string with each of the 'lists' as columns with the appropriate 'titles' """
    longestList = 0
    longestItem = 0
    prntLists   = []
    pad         = padSpaces * ' '
    rtnStr      = ""
    
    assert ( len( titles ) == len( lists ) ) or ( len( titles ) == 0 ) ,
           "Titles " + str( len( titles ) ) + " and lists " + str( len( lists ) ) + " of unequal length."
    
    titleOut = len( titles )
    
    if titleOut:
        for title in titles:
            if len( title ) > longestItem:
                longestList = len( title )
    
    for lst in lists:
        if len( lst ) > longestItem:
            longestList = len( lst )
        prntLists.append( [] )
        for item in lst:
            strItem = str( item )
            prntLists[-1].append( strItem )
            if len( strItem ) > longestItem:
                longestItem = len( strItem )
    if titleOut:
        line = ''
        for title in titles:
            line += title[ : len( pad ) + longestItem -1 ].rjust( len( pad ) + longestItem , ' ' )
        if output:  print( line )
        rtnStr += line + endl
    for index in range( longestList ):
        line = ''
        for lst in prntLists:
            if index < len( lst ):
                line += pad + lst[ index ].ljust( longestItem , ' ' )
            else:
                line += pad + longestItem * ' '
        if output:  print( line )
        rtnStr += line + endl
    return rtnStr

def levenshteinDistance( str1 , str2 ):
    """ Compute the edit distance between strings , Return:
        'ldist': Number of edits between the strings 
        'ratio': Number of edits over the sum of the lengths of 'str1' and 'str2' """
    # URL , Levenshtein Distance: https://rosettacode.org/wiki/Levenshtein_distance#Python
    m = len( str1 )
    n = len( str2 )
    lensum = float( m + n )
    d = []           
    for i in range( m + 1 ):
        d.append( [i] )        
    del d[0][0]    
    for j in range( n + 1 ):
        d[0].append(j)       
    for j in range( 1 , n+1 ):
        for i in range( 1 , m+1 ):
            if str1[ i-1 ] == str2[ j-1 ]:
                d[i].insert( j , d[ i-1 ][ j-1 ] )           
            else:
                minimum = min( d[ i-1 ][ j ] + 1   , 
                               d[ i ][ j-1 ] + 1   , 
                               d[ i-1 ][ j-1 ] + 2 )
                d[i].insert( j , minimum )
    ldist = d[-1][-1] 
    ratio = ( lensum - ldist ) / lensum
    return { 'distance' : ldist , 'ratio' : ratio }

def levenshtein_diff_score( keyWord , compareWord ):
    """ Return a difference score that is edit distance over `keyWord` length """
    return 1.0 * levenshteinDistance( keyWord , compareWord )['distance'] / len( keyWord )

# ___ END STRING _____________________________________________________________________________________________________________________


# === CONTAINER FUNCTIONS ==================================================================================================================
    
def size( struct ):
    """ Return the size of a rectangual nD array """
    # NOTE: This function assumes that the first element of each list reflects the size of all other elements at the same level
    dims = []
    level = struct
    while 1:
        try:
            dims.append( len( level ) )
            level = level[0]
        except Exception:
            break
    return dims

def concat_arr( *arrays ):
    """ Concatenate all 'arrays' , any of which can be either a Python list or a Numpy array """
    # URL , Test if any in an iterable belongs to a certain class : https://stackoverflow.com/a/16705879
    if any( isinstance( arr , np.ndarray ) for arr in arrays ): # If any of the 'arrays' are Numpy , work for all cases , 
        if len( arrays ) == 2: # Base case 1 , simple concat    # but always returns np.ndarray
            return np.concatenate( ( arrays[0] , arrays[1] ) )
        elif len( arrays ) > 2: # If there are more than 2 , concat the first two and recur
            return concat_arr( 
                np.concatenate( ( arrays[0] , arrays[1] ) ) , 
                *arrays[2:] 
            )
        else: # Base case 2 , there is only one arg , return it
            return arrays[0]
    if len( arrays ) > 1: # else no 'arrays' are Numpy 
        rtnArr = arrays[0]
        for arr in arrays[1:]: # If there are more than one , just use addition operator in a line
            rtnArr += arr
        return rtnArr
    else: # else there was only one , return it
        return arrays[0] 

def build_sublists_by_cadence( flatList , cadence ): 
    """ Return a list in which each element is a list of consecutive 'flatList' elements of length 'cadence' elements if elements remain """
    rtnList = []
    for flatDex , flatElem in enumerate( flatList ):
        if flatDex % cadence == 0:
            rtnList.append( [] )
        rtnList[-1].append( flatElem )
    return rtnList

def tandem_sorted( keyList , *otherLists ): 
    """ Sort multiple lists of equal length in tandem , with the elements of each in 'otherLists' reordered to correspond with a sorted 'keyList' """
    # URL , Sort two lists in tandem: http://stackoverflow.com/a/6618543/893511
    bundle = sorted( zip( keyList , *otherLists ) , key = lambda elem: elem[0] ) # Sort the tuples by the key element
    # print "DEBUG , zipped lists:" , bundle
    rtnLists = [ [] for i in xrange( len( bundle[0] ) ) ]
    for elemTuple in bundle:
        for index , elem in enumerate( elemTuple ):
            rtnLists[ index ].append( elem ) # Send the element to the appropriate list
    return rtnLists

# ___ END CONTAINER FUNC _____________________________________________________________________________________________________________


# === CONTAINER CLASSES ==============================================================================================================

class PriorityQueue( list ): # Requires heapq 
    """ Implements a priority queue data structure. """ 
    # NOTE: PriorityQueue does not allow you to change the priority of an item. 
    #       You may insert the same item multiple times with different priorities. 

    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )   
        self.count = 0
        self.s = set([])    

    def push( self , item , priority , hashable = None ):
        """ Push an item on the queue and automatically order by priority , optionally provide 'hashable' version of item for set testing """
        entry = ( priority , self.count , item )
        heapq.heappush( self , entry )
        self.count += 1
        if hashable:
            self.s.add( hashable ) 

    def contains( self , hashable ): 
        ''' Test if 'node' is in the queue '''
        return hashable in self.s

    def pop( self ):
        """ Pop the lowest-priority item from the queue """
        priority , count , item = heapq.heappop( self )
        return item

    def pop_with_priority( self ):
        """ Pop the item and the priority associated with it """
        priority , count , item = heapq.heappop( self )
        return item , priority

    def pop_opposite( self ):
        """ Remove the item with the longest priority , opoosite of the usual pop """
        priority , count , item = self[-1]
        del self[-1]
        return item

    def isEmpty(self):
        """ Return True if the queue has no items, otherwise return False """
        return len( self ) == 0

    # __len__ is provided by 'list'

    def unspool( self , N = infty , limit = infty ):
        """ Pop all items as two sorted lists, one of increasing priorities and the other of the corresponding items """
        vals = []
        itms = []
        count = 0
        while not self.isEmpty() and count < N and self.top_priority() <= limit:
            item , valu = self.pop_with_priority()
            vals.append( valu )
            itms.append( item )
            count += 1
        return itms , vals

    def peek( self ):
        """ Return the top priority item without popping it """
        priority , count , item = self[0]
        return item

    def peek_opposite( self ):
        """ Return the bottom priority item without popping it """
        priority , count , item = self[-1]
        return item

    def top_priority( self ):
        """ Return the value of the top priority """
        return self[0][0]

    def btm_priority( self ):
        """ Return the value of the bottom priority """
        return self[-1][0]

    def get_priority_and_index( self , item , eqFunc = pyEq ):
        """ Return the priority for 'item' and the index it was found at , using the secified 'eqFunc' , otherwise return None if 'item' DNE """
        for index , elem in enumerate( self ): # Implement a linear search
            if eqFunc( elem[-1] , item ): # Check the contents of each tuple for equality
                return elem[0] , index # Return priority if a match
        return None , None # else search completed without match , return None

    def reprioritize_at_index( self , index , priority ):
        """ Replace the priority of the element at 'index' with 'priority' """
        temp = list.pop( self , index ) # Remove the item at the former priority
        self.push( temp[-1] , priority ) # Push with new priority , this item should have the same hashable lookup
    
class Stack(list): 
    """ LIFO container based on 'list' """    

    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )

    def push( self , elem ):
        """ Push 'elem' onto the Stack """
        self.append( elem )

    def top( self ):
        """ Return the top of the stack """
        return self[-1]

    # 'Stack.pop' is inherited from 'list'

    def is_empty(self):
        """ Returns true if the Stack has no elements """
        return len(self) == 0
        
class RollingList( list ): 
    """ A rolling window based on 'list' """ 

    def __init__( self , winLen , *args ):
        """ Normal 'list' init """
        list.__init__( self , [ 0 for i in range( winLen ) ] , *args )
        self.limit = winLen

    def trim_front( self ):
        """ Drop leading elements until the length condition is met """
        while len( self ) > self.limit:
            del self[0]

    def trim_back( self ):
        """ Drop trailing elements until the length condition is met """
        while len( self ) > self.limit:
            del self[-1]

    def append( self , item ):
        """ Append an item to the back of the list """
        list.append( self , item )
        self.trim_front()

    def prepend( self , item ):
        """ Prepend an item to the front of the list """
        self.insert( 0 , item )
        self.trim_back()

    def extend( self , addedList ):
        """ Extend the list and enforce limits """
        list.extend( self , addedList )
        self.trim_front()

    def get_average( self ):
        """ Get the rolling average """
        # NOTE: Calling this function after inserting non-numeric or non-scalar elements will result in an error
        return sum( self ) * 1.0 / len( self )

# ___ END CONTAINER CLASS ____________________________________________________________________________________________________________


# === ITERABLE STRUCTURES ============================================================================================================

def incr_min_step( bgn , end , stepSize ):
    """ Return a list of numbers from 'bgn' to 'end' (inclusive), separated by at LEAST 'stepSize'  """
    # NOTE: The actual step size will be the size that produces an evenly-spaced list of trunc( (end - bgn) / stepSize ) elements
    return np.linspace( bgn , end , num = trunc( (end - bgn) / stepSize ) , endpoint=True )

def incr_max_step( bgn , end , stepSize ):
    """ Return a list of numbers from 'bgn' to 'end' (inclusive), separated by at MOST 'stepSize'  """
    numSteps = ( end - bgn ) / ( stepSize * 1.0 )
    rtnLst = [ bgn + i * stepSize for i in xrange( trunc(numSteps) + 1 ) ]
    if numSteps % 1 > 0: # If there is less than a full 'stepSize' between the last element and the end
        rtnLst.append( end )
    return rtnLst

def iter_contains_None( listOrTuple ):
    """ Return True if any of 'listOrTuple' is None or contains None , Otherwise return False """
    if isinstance( listOrTuple , ( list , tuple ) ): # Recursive Case: Arg is an iterable , inspect each
        for elem in listOrTuple:
            if iter_contains_None( elem ):
                return True
        return False
    else: # Base Case: Arg is single value
        return True if listOrTuple == None else False
    
def elemw( iterable , i ): 
    """ Return the 'i'th index of 'iterable', wrapping to index 0 at all integer multiples of 'len(iterable)' , Wraps forward and backwards """
    seqLen = len( iterable )
    if i >= 0:
        return iterable[ i % ( seqLen ) ]
    else:
        revDex = abs( i ) % ( seqLen )
        if revDex == 0:
            return iterable[ 0 ]
        return iterable[ seqLen - revDex ]

# ___ END ITERABLE ___________________________________________________________________________________________________________________


# === Hash/Dict Structures =============================================================================================

def assoc_lists( keys , values ):
    """ Return a dictionary with associated 'keys' and 'values' """
    return dict( zip( keys , values ) )
    
class Counter( dict ): 
    """ The counter object acts as a dict, but sets previously unused keys to 0 , in the style of CS 6300 @ U of Utah """

    def __init__( self , *args , **kw ):
        """ Standard dict init """
        dict.__init__( self , *args , **kw )
        if "default" in kw:
            self.defaultReturn = kw['default']
        else:
            self.defaultReturn = 0

    def set_default( self , val ):
        """ Set a new default value to return when there is no """
        self.defaultReturn = val

    def __getitem__( self , a ):
        """ Get the val with key , otherwise return 0 if key DNE """
        if a in self: 
            return dict.__getitem__( self , a )
        return 0

    # __setitem__ provided by 'dict'

    def sorted_keyVals( self ):
        """ Return a list of sorted key-value tuples """
        sortedItems = self.items()
        sortedItems.sort( cmp = lambda keyVal1 , keyVal2 :  np.sign( keyVal2[1] - keyVal1[1] ) )
        return sortedItems
    
    def unroll_to_lists( self ):
        """ Return keys and values in associated pairs """
        rtnKeys = list( self.keys() )
        rtnVals = [ self[k] for k in rtnKeys ] # Positions must match, iterate over above list
        return rtnKeys , rtnVals

    def sample_until_unique( self , sampleFromSeq , sampleLim = int( 1e6 ) ):
        """ Sample randomly from 'sampleFromSeq' with a uniform distribution until a new key is found or the trial limit is reached , return it """
        # NOTE: If 'sampleLim' set to 'infty' , the result may be an infinite loop if the Counter has a key for each 'sampleFromSeq'
        trial = 1
        while( trial <= sampleLim ):
            testKey = choice( sampleFromSeq )
            if self[ testKey ] == 0:
                return testKey
            trial += 1
        return None

# ___ End Hash/Dict ____________________________________________________________________________________________________


# === System Helpers ===================================================================================================

def confirm_or_crash( msg = "Text to Crash, Empty to Continue: " ):
    """ If the input is anything other than empty, then Crash the program """
    crash = raw_input( msg )
    if len( crash ):
        exit()
        
# = class LogMH =

class LogMH:
    """ Text buffer object to hold script output, with facilities to write contents """

    def __init__( self ):
        """ String to store logs """
        self.totalStr = ""

    def prnt( self , *args ):
        """ Print args and store them in a string """
        for arg in args:
            self.totalStr += ascii( arg ) + " "
            print( ascii( arg ) , end=" " )
        print
        self.totalStr += endl

    def sep( self , title = "" , width = 6 , char = '=' , strOut = False ):
        """ Print a separating title card for debug """
        LINE = width * char
        self.prnt( LINE + ' ' + title + ' ' + LINE )
        if strOut:
            return LINE + ' ' + title + ' ' + LINE

    def write( self , *args ):
        """ Store 'args' in the accumulation string without printing """
        numArgs = len( args )
        for i , arg in enumerate( args ):
            self.totalStr += ascii( arg ) + ( " " if i < numArgs-1 else "" )

    def out_and_clear( self , outPath ):
        """ Write the contents of 'totalStr' to a file and clear """
        outFile = file( outPath , 'w' )
        outFile.write( self.totalStr )
        outFile.close()
        self.clear()

    def clear( self ):
        """ Clear the contents of 'accum.totalStr' """
        self.totalStr = ""

# _ End LogMH _

def parse_args( argList ):
    """ Parse a dictionary of terminal parameters and their arguments """
    # NOTE: This function assumes that each terminal parameter begins with a dash "-param"
    # NOTE: This function assumes that a terminal argument follows the parameter that it must be assigned to,
    #       and that no parameters begin with a dash
    
    def parse_arg( arg ):
        """ Attempt to parse the argument as a float, int, or string; in that order """
        rtnVal = None
        try:
            rtnVal = int( arg )
        except ValueError:
            try:
                rtnVal = float( arg )
            except ValueError:
                rtnVal = str( arg )
        return rtnVal
    
    stashedParam = ''
    argLookup    = {}
    argLen       = len( argList )
    # 1. For each item
    for i , arg_i in enumerate( argList ):
        # 2. If it is a parameter
        if arg_i[0] == '-':
            # 3. If there is a previously stashed parameter, then assign it the value of `True` -OR-
            if stashedParam:
                argLookup[ stashedParam ] = True
            # 4. If we are at the end of the list, then assign the current parameter the value of `True`
            if i+1 == argLen:
                argLookup[ arg_i  ] = True
            # 5. Stash the current parameter name
            stashedParam = arg_i
        # 6. Else it is an argument
        else:
            # 7. If there is a parameter stashed, then parse it and assign the argument to the parameter
            if stashedParam:
                argLookup[ stashedParam ] = parse_arg( arg_i )
                stashedParam = ''
            # 8. Else, ignore the argument
            else:
                pass
    # 9. Return
    return argLookup

# ___ End System _______________________________________________________________________________________________________





# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass


# ___ End Tests ____________________________________________________________________________________________________________________________
