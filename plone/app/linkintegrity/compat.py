# If Archetypes is not installed, define dummy objects
# to replace Archetypes imports.

try:
    from Products.Archetypes.interfaces import IBaseObject
    from Products.Archetypes.Field import TextField
except ImportError:
    from zope.interface import Interface

    class IBaseObject(Interface):
        pass

    class TextField(object):
        pass
