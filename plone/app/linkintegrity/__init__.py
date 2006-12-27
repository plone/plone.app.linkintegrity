from os.path import abspath, dirname

packageHome = abspath(dirname(__file__))

def initialize(context):
    
    # install the wrapper around zpublisher_exception_hook
    from monkey import installExceptionHook
    installExceptionHook()

