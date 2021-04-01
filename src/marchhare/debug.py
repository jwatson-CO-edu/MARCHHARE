########## Printing ###############################################################################


def cerr( *args ):
    """ `print()` a message to STDERR """
    print( *args, file = sys.stderr )