"""
MIT License

Copyright (c) 2020, James Watson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# === FILE OPERATIONS ======================================================================================================================

def lines_from_file( fPath ): 
    """ Open the file at 'fPath' , and return lines as a list of strings """
    with open( fPath , 'r' ) as f:
        lines = f.readlines()
    return lines

def strip_endlines_from_lines( lines ):
    """ Remove the endlines from a list of lines read from a file """
    rtnLines = []
    for line in lines:
        currLine = ''
        for char in line:
            if char != '\n' and char != '\r':
                currLine += char
        rtnLines.append( currLine )
    return rtnLines

def strip_comments_from_lines( lines ):
    """ Remove everything after each # """
    rtnLines = []
    for line in lines:
        rtnLines.append( str( line.split( '#' , 1 )[0] ) )
    return rtnLines

def purge_empty_lines( lines ):
    """ Given a list of lines , Remove all lines that are only whitespace """
    rtnLines = []
    for line in lines:
        if ( not line.isspace() ) and ( len( line ) > 0 ):
            rtnLines.append( line )
    return rtnLines

def parse_lines( fPath , parseFunc ):
    """ Parse lines with 'parseFunc' while ignoring Python-style # comments """
    rtnExprs = []
    # 1. Fetch all the lines
    lines = lines_from_file( fPath )
    # 2. Scrub comments from lines
    lines = strip_comments_from_lines( lines )
    # 3. Purge empty lines
    lines = purge_empty_lines( lines )
    # 3.5. Remove newlines
    lines = strip_endlines_from_lines( lines )
    # 4. For each of the remaining lines , Run the parse function and save the results
    for line in lines:
        rtnExprs.append( parseFunc( line ) )
    # 5. Return expressions that are the results of processing the lines
    return rtnExprs

def parse_lines_into_columns( fPath , parseFunc ):
    """ Parse lines with 'parseFunc' into equal-length columns of data, while ignoring Python-style # comments """
    prsdExprs = parse_lines( fPath , parseFunc )
    numCols   = len( prsdExprs[0] )
    rntCols   = [ [] for i in range( numCols ) ]
    for expr in prsdExprs:
        if len( expr ) != numCols:
            print( "WARNING: " )
            return rntCols
        for j in range( numCols ):
            rntCols[j].append( expr[j] )
    return rntCols
        
def tokenize_with_char( rawStr , separator = ',' ,  evalFunc = str ): 
    """ Return a list of tokens taken from 'rawStr' that is partitioned with a separating character, transforming each token with 'evalFunc' """
    return [ evalFunc( rawToken ) for rawToken in rawStr.split( separator ) ]

def get_tokenizer_with_char( separator = ',' ,  evalFunc = str ):
    """ Return a function that returns a list of tokens from 'rawStr' that is split on separating character, transforming each token with 'evalFunc' """
    def rtnFunc( rawStr ):
        return [ evalFunc( rawToken ) for rawToken in rawStr.split( separator ) ]
    return rtnFunc

def strip_EXT( fName ):
    """ Return the filepath before the extension """
    return os.path.splitext( fName )[0]

def get_EXT( fName , CAPS = 1 ):
    """ Return the filepath before the extension """
    ext = os.path.splitext( fName )[1][1:]
    return ( ext.upper() if CAPS else ext )

def struct_to_pkl( struct , pklPath ): 
    """ Serialize a 'struct' to 'pklPath' """
    f = open( pklPath , 'wb') # open a file for binary writing to receive pickled data
    cPickle.dump( struct , f ) # changed: pickle.dump --> cPickle.dump
    f.close()

def load_pkl_struct( pklPath ): 
    """ Load a pickled object and return it, return None if error """
    fileLoaded = False
    rtnStruct = None
    try:
        f = open( pklPath , 'rb')
        fileLoaded = True
    except Exception as err:
        print( "load_pkl_struct: Could not open file,",pklPath,",",err )
    if fileLoaded:
        try:
            rtnStruct = cPickle.load( f )
        except Exception as err:
            print( "load_pkl_struct: Could not unpickle file,",pklPath,",",err )
        f.close()
    return rtnStruct

def unpickle_dict( filename ):
    """ Return the dictionary stored in the file , Otherwise return an empty dictionary if there were no items """
    try:
        infile = open( filename , 'rb' )
        rtnDict = cPickle.load( infile )
        is_container_too_big( rtnDict )
        if len( rtnDict ) > 0:
            return rtnDict
        else:
            return {}
    except IOError:
        return {}

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

def ensure_dirs_writable( *dirList ):
    """ Return true if every directory argument both exists and is writable, otherwise return false """
    # NOTE: This function exits on the first failed check and does not provide info for any subsequent element of 'dirList'
    # NOTE: Assume that a writable directory is readable
    for directory in dirList:
        ensure_dir( directory )
    return validate_dirs_writable( *dirList )

def flatten_dir_files( rootDir , _VRB = 0 ):
    """ Move all files to the top of `rootDir`, Then delete all subfolders """
    # 1. Walk the entire directory from root to leaf
    for ( dirpath , dirs , files ) in os.walk( rootDir , topdown = False ):
        # 2. For each file
        for filename in files:
            # 3. Consruct full paths
            fPath = os.path.join( dirpath , filename )
            dPath = os.path.join( rootDir , filename )
            # 4. If the file exists, then move it
            if os.path.isfile( fPath ):
                try:
                    if _VRB: print( "Moving" , fPath , "--to->\n\t" , dPath )
                    os.rename( fPath , dPath )
                    if _VRB: print( "\tSuccess!" )
                except:
                    if _VRB: print( "\tFailure!" )
        try:
            os.rmdir( dirpath )
            if _VRB: print( "\t\tRemoved" , dirpath )
        except OSError as ex:
            if _VRB: print( "\t\tAttempted to remove" , dirpath , "but:" , ex )

# ___ END FILE _____________________________________________________________________________________________________________________________