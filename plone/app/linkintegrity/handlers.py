from Acquisition import aq_get
from Acquisition import aq_parent
from plone.app.linkintegrity.interfaces import IRetriever
from plone.app.linkintegrity.utils import ensure_intid
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.base.interfaces import IEditingSchema
from plone.base.interfaces import IPloneSiteRoot
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from urllib.parse import unquote
from urllib.parse import urlsplit
from z3c.relationfield import RelationValue
from z3c.relationfield.event import _setRelation
from zc.relation.interfaces import ICatalog
from zExceptions import NotFound
from ZODB.POSException import ConflictError
from zope.component import getUtility
from zope.interface.interfaces import ComponentLookupError
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces import NotFound as ztkNotFound

import logging


logger = logging.getLogger(__name__)


def findObject(base, path):
    """traverse to given path and find the upmost object"""
    if path.startswith("/"):
        # Make an absolute path relative to the portal root
        obj = getToolByName(base, "portal_url").getPortalObject()
        portal_path = obj.absolute_url_path() + "/"
        if path.startswith(portal_path):
            path = path[len(portal_path) :]
    else:
        obj = aq_parent(base)  # relative urls start at the parent...

    components = path.split("/")

    # Support resolveuid/UID paths explicitly, without relying
    # on a view or skinscript to do this for us.
    if "resolveuid" in components:
        uid = components[components.index("resolveuid") + 1]
        # This may be a link to a page that once was published but not anymore,
        # or the current editor does not have View permission.
        # In that case uuidToObject(uid) could fail with Unauthorized.
        brain = uuidToCatalogBrain(uid)
        if brain is not None:
            # Note: _unrestrictedGetObject starts with an underscore,
            # but it is documented in ZCatalog.interfaces,
            # so should be safe to rely on.
            obj = brain._unrestrictedGetObject()
            if obj:
                return obj, path

    while components:
        child_id = unquote(components[0])
        try:
            try:
                child = obj.unrestrictedTraverse(child_id)
            except AttributeError:
                request = aq_get(obj, "REQUEST")
                child = request.traverseName(obj, child_id)
        except ConflictError:
            raise
        except (AttributeError, KeyError, NotFound, ztkNotFound, UnicodeEncodeError):
            return None, None
        if not IDexterityContent.providedBy(child) and not IPloneSiteRoot.providedBy(
            child
        ):
            break
        obj = child
        components.pop(0)
    return obj, "/".join(components)


def getObjectsFromLinks(base, links):
    """Determine actual objects referred to by given links.

    return set of RelationValue
    """
    intids = getUtility(IIntIds)
    objects = set()
    url = base.absolute_url()
    scheme, host, path, query, frag = urlsplit(url)
    for link in links:
        s, h, path, q, f = urlsplit(link)
        # relative or local url
        if (not s and not h) or (s == scheme and h == host):
            obj, extra = findObject(base, path)
            if obj and not IPloneSiteRoot.providedBy(obj):
                objid = ensure_intid(obj, intids)
                if objid is None:
                    # if we get a NotYet error, the object is not
                    # attached yet and we will need to get links
                    # at a later time when the object has an intid
                    continue
                relation = RelationValue(objid)
                objects.add(relation)
    return objects


def modifiedContent(obj, event):
    """Object was modified, cloned or created."""
    if not check_linkintegrity_dependencies(obj):
        return
    retriever = IRetriever(obj, None)
    if retriever is not None:
        links = retriever.retrieveLinks()
        refs = getObjectsFromLinks(obj, links)
        updateReferences(obj, refs)


def removedContent(obj, event):
    if not check_linkintegrity_dependencies(obj):
        return

    intids = getUtility(IIntIds)
    try:
        int_id = intids.getId(obj)
    except KeyError:
        return

    catalog = getUtility(ICatalog)
    rels = catalog.findRelations(
        {"from_id": int_id, "from_attribute": referencedRelationship}
    )
    for rel in list(rels):
        catalog.unindex(rel)


# BBB
modifiedArchetype = modifiedContent
modifiedDexterity = modifiedContent


def updateReferences(obj, refs):
    """Renew all linkintegritry-references.

    Search the zc.relation catalog for linkintegritry-references for this obj.
    Drop them all and set the new ones.
    TODO: Might be improved by not changing anything if the links are the same.
    """
    int_id = ensure_intid(obj)
    if int_id is None:
        return
    catalog = getUtility(ICatalog)
    # unpack the rels before deleting
    old_rels = [
        i
        for i in catalog.findRelations(
            {"from_id": int_id, "from_attribute": referencedRelationship}
        )
    ]
    for old_rel in old_rels:
        catalog.unindex(old_rel)
    for ref in refs:
        _setRelation(obj, referencedRelationship, ref)


def check_linkintegrity_dependencies(obj):
    try:
        reg = getUtility(IRegistry)
        editing_settings = reg.forInterface(IEditingSchema, prefix="plone")
    except (ComponentLookupError, KeyError):
        return False
    if not editing_settings.enable_link_integrity_checks:
        return False
    if not getToolByName(obj, "portal_url", None):
        # `getObjectFromLinks` is not possible without access
        # to `portal_url`
        return False
    try:
        getUtility(IIntIds)
        getUtility(ICatalog)
    except ComponentLookupError:
        # Linkintegrity not possible without zope.intid-
        # and zc.relation-catalog
        return False
    return True
