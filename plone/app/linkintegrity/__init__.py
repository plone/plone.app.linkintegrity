from AccessControl import allow_module, allow_class
from os.path import abspath, dirname, basename

packageHome = abspath(dirname(__file__))
packageName = basename(packageHome)
packageGlobals = globals()

referencedRelationship = 'isReferencing'

def initialize(context):
    
    # install the wrapper around zpublisher_exception_hook
    from monkey import installExceptionHook
    installExceptionHook()
    
    # allow access to the exception in the folder_delete script
    from OFS.ObjectManager import BeforeDeleteException
    allow_module('OFS.ObjectManager')
    allow_class(BeforeDeleteException)

