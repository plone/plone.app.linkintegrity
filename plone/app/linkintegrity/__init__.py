from os.path import abspath, dirname, basename

packageHome = abspath(dirname(__file__))
packageName = basename(packageHome)
packageGlobals = globals()

referencedRelationship = 'isReferencing'

def initialize(context):
    
    # install the wrapper around zpublisher_exception_hook
    from monkey import installExceptionHook
    installExceptionHook()

