from zope.interface import Interface


class ILinkIntegrityNotificationException(Interface):
    """ an exception indicating a prevented link integrity breach """


class ILinkIntegrityTool(Interface):
    """ interface of link integrity tool """


class ILinkIntegrityInfo(Interface):
    """ a place to store information about link integrity, i.e. breaches;
        the storage is assumed to be unique per browser request """
    
    def getIntegrityInfo():
        """ return stored information regarding link integrity """
    
    def setIntegrityInfo(info):
        """ stored information regarding link integrity """
    
    def getEnvMarker():
        """ return the marker string used to pass the already confirmed
            items across the retry exception """
    
    def isConfirmedItem(obj):
        """ indicate if the removal of the given object was confirmed """
    
    def encodeConfirmedItems(additions):
        """ return the list of previously confirmed (for removeal) items,
            optionally adding the given items, encoded for usage in a form """


class IOFSImage(Interface):
    """ interface for OFS.Image.Image """


