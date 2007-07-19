def initialize(context):

    # install the wrapper around zpublisher_exception_hook
    from monkey import installExceptionHook
    installExceptionHook()

