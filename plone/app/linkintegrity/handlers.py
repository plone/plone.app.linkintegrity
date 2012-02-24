from logging import getLogger
from Acquisition import aq_get
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IReference
from Products.Archetypes.Field import TextField
from Products.Archetypes.exceptions import ReferenceException
from OFS.interfaces import IItem
from ZODB.POSException import ConflictError
from zExceptions import NotFound
from zope.publisher.interfaces import NotFound as ztkNotFound
from exceptions import LinkIntegrityNotificationException
from interfaces import ILinkIntegrityInfo, IOFSImage
from urlparse import urlsplit
from parser import extractLinks
from urllib import unquote

# To support various Plone versions, we need to support various UUID resolvers
# This follows Kupu, TinyMCE and plone.app.uuid methods, in a similar manner to
# plone.outputfilters.browser.resolveuid
try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite
try:
    from plone.app.uuid.utils import uuidToObject
except ImportError:
    def uuidToObject(uuid):
        catalog = getToolByName(getSite(), 'portal_catalog', None)
        res = catalog and catalog.unrestrictedSearchResults(UID=uuid)
        if res and len(res) == 1:
            return res[0].getObject()

def _resolveUID(uid):
    res = uuidToObject(uid)
    if res is not None:
        return res
    kupu_hook = getattr(getSite(), 'kupu_resolveuid_hook', None)
    if kupu_hook is not None:
        return kupu_hook(uid)
    return None


referencedRelationship = 'isReferencing'


def findObject(base, path):
    """ traverse to given path and find the upmost object """
    obj = base
    components = path.split('/')

    # Support resolveuid/UID paths explicitely, without relying
    # on a view or skinscript to do this for us.
    if len(components) == 2 and components[0] == 'resolveuid':
        obj = _resolveUID(components[1])
        if obj:
            return obj, path

    while components:
        child_id = unquote(components[0])
        try:
            try:
                child = obj.restrictedTraverse(child_id)
            except AttributeError:
                request = aq_get(obj, 'REQUEST')
                child = request.traverseName(obj, child_id)
        except ConflictError:
            raise
        except (AttributeError, KeyError, NotFound, ztkNotFound):
            return None, None
        if not IItem.providedBy(child):
            break
        obj = child
        components.pop(0)
    return obj, '/'.join(components)


def getObjectsFromLinks(base, links):
    """ determine actual objects refered to by given links """
    objects = set()
    url = base.absolute_url()
    scheme, host, path, query, frag = urlsplit(url)
    for link in links:
        s, h, path, q, f = urlsplit(link)
        if (not s and not h) or (s == scheme and h == host):    # relative or local url
            obj, extra = findObject(base, path)
            if obj:
                if IOFSImage.providedBy(obj):
                    obj = aq_parent(obj)    # use atimage object for scaled images
                objects.add(obj)
    return objects


def modifiedArchetype(obj, event):
    """ an archetype based object was modified """
    try:    # TODO: is this a bug or a needed workaround?
        existing = set(obj.getReferences(relationship=referencedRelationship))
    except AttributeError:
        return
    refs = set()
    for field in obj.Schema().fields():
        if isinstance(field, TextField):
            accessor = field.getAccessor(obj)
            links = extractLinks(accessor())
            refs = refs.union(getObjectsFromLinks(obj, links))
    for ref in refs.difference(existing):   # add new references and...
        try:
            obj.addReference(ref, relationship=referencedRelationship)
        except ReferenceException:
            pass
    for ref in existing.difference(refs):   # removed leftovers
        try:
            obj.deleteReference(ref, relationship=referencedRelationship)
        except ReferenceException:
            try:
                # try to get rid of the dangling reference, but let's not
                # have this attempt to clean up break things otherwise...
                # iow, the `try..except` is there, because internal methods
                # of the reference catalog are being used directly here.  any
                # changes regarding these shouldn't break things over here,
                # though...
                refcat = getToolByName(obj, 'reference_catalog')
                uid, dummy = refcat._uidFor(obj)
                brains = refcat._queryFor(uid, None, relationship=referencedRelationship)
                objs = refcat._resolveBrains(brains)
                for obj in objs:
                    refcat._deleteReference(obj)
            except ConflictError:
                raise
            except:
                getLogger(__name__).warning('dangling "linkintegrity" '
                    'reference to %r could not be removed.', obj)


def referenceRemoved(obj, event):
    """ store information about the removed link integrity reference """
    assert IReference.providedBy(obj)
    assert obj is event.object          # just making sure...
    if not obj.relationship == referencedRelationship:
        return                          # skip for other removed references
    # if the object the event was fired on doesn't have a `REQUEST` attribute
    # we can safely assume no direct user action was involved and therefore
    # never raise a link integrity exception...
    request = aq_get(obj, 'REQUEST', None)
    if not request:
        return
    storage = ILinkIntegrityInfo(request)
    breaches = storage.getIntegrityBreaches()
    breaches.setdefault(obj.getTargetObject(), set()).add(obj.getSourceObject())
    storage.setIntegrityBreaches(breaches)


def referencedObjectRemoved(obj, event):
    """ check if the removal was already confirmed or redirect to the form """
    # if the object the event was fired on doesn't have a `REQUEST` attribute
    # we can safely assume no direct user action was involved and therefore
    # never raise a link integrity exception...
    request = aq_get(obj, 'REQUEST', None)
    if not request:
        return
    info = ILinkIntegrityInfo(request)
    # first we check if link integrity checking was enabled
    if not info.integrityCheckingEnabled():
        return

    # since the event gets called for every subobject before it's
    # called for the item deleted directly via _delObject (event.object)
    # itself, but we do not want to present the user with a confirmation
    # form for every (referred) subobject, so we remember and skip them...
    info.addDeletedItem(obj)
    if obj is not event.object:
        return

    # if the number of expected events has been stored to help us prevent
    # multiple forms (i.e. in folder_delete), we wait for the next event
    # if we know there will be another...
    if info.moreEventsToExpect():
        return

    # at this point all subobjects have been removed already, so all
    # link integrity breaches caused by that have been collected as well;
    # if there aren't any (after things have been cleaned up),
    # we keep lurking in the shadows...
    if not info.getIntegrityBreaches():
        return

    # if the user has confirmed to remove the currently handled item in a
    # previous confirmation form we won't need it anymore this time around...
    if info.isConfirmedItem(obj):
        return

    # otherwise we raise an exception and pass the object that is supposed
    # to be removed as the exception value so we can use it as the context
    # for the view triggered by the exception;  this is needed since the
    # view is an adapter for the exception and a request, so it gets the
    # exception object as the context, which is not very useful...
    raise LinkIntegrityNotificationException(obj)
