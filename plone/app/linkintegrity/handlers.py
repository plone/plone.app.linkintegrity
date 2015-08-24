# -*- coding: utf-8 -*-
from Acquisition import aq_get
from Acquisition import aq_parent
from Products.Archetypes.Field import TextField
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from ZODB.POSException import ConflictError
from plone.app.linkintegrity.parser import extractLinks
from plone.app.textfield import RichText
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from urllib import unquote
from urlparse import urlsplit
from z3c.relationfield import RelationValue
from z3c.relationfield.event import _setRelation
from zExceptions import NotFound
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.intid.interfaces import IIntIds
from zope.keyreference.interfaces import NotYet
from zope.publisher.interfaces import NotFound as ztkNotFound
from zope.schema import getFieldsInOrder
import logging

logger = logging.getLogger(__name__)
referencedRelationship = 'isReferencing'


def findObject(base, path):
    """ traverse to given path and find the upmost object """
    if path.startswith('/'):
        # Make an absolute path relative to the portal root
        obj = getToolByName(base, 'portal_url').getPortalObject()
        portal_path = '/'.join(obj.getPhysicalPath()) + '/'
        if path.startswith(portal_path):
            path = path[len(portal_path):]
    else:
        obj = aq_parent(base)   # relative urls start at the parent...

    components = path.split('/')

    # Support resolveuid/UID paths explicitely, without relying
    # on a view or skinscript to do this for us.
    if 'resolveuid' in components:
        uid = components[components.index('resolveuid') + 1]
        obj = uuidToObject(uid)
        if obj:
            return obj, path

    while components:
        child_id = unquote(components[0])
        try:
            try:
                child = obj.unrestrictedTraverse(child_id)
            except AttributeError:
                request = aq_get(obj, 'REQUEST')
                child = request.traverseName(obj, child_id)
        except ConflictError:
            raise
        except (AttributeError, KeyError,
                NotFound, ztkNotFound, UnicodeEncodeError):
            return None, None
        if not IDexterityContent.providedBy(child) and \
                not IBaseObject.providedBy(child) and \
                not IPloneSiteRoot.providedBy(child):
            break
        obj = child
        components.pop(0)
    return obj, '/'.join(components)


def getObjectsFromLinks(base, links):
    """ determine actual objects refered to by given links """
    intids = getUtility(IIntIds)
    objects = set()
    url = base.absolute_url()
    scheme, host, path, query, frag = urlsplit(url)
    for link in links:
        s, h, path, q, f = urlsplit(link)
        # relative or local url
        if (not s and not h) or (s == scheme and h == host):
            # Paths should always be strings
            if isinstance(path, unicode):
                path = path.encode('utf-8')

            obj, extra = findObject(base, path)
            if obj and not IPloneSiteRoot.providedBy(obj):
                objid = intids.getId(obj)
                relation = RelationValue(objid)
                objects.add(relation)
    return objects


def modifiedArchetype(obj, event):
    """ an archetype based object was modified """
    if not check_linkintegrity_dependencies(obj):
        return
    refs = set()
    for field in obj.Schema().fields():
        if isinstance(field, TextField):
            accessor = field.getAccessor(obj)
            encoding = field.getRaw(obj, raw=1).original_encoding
            if accessor is not None:
                value = accessor()
            else:
                # Fields that have been added via schema extension do
                # not have an accessor method.
                value = field.get(obj)
            links = extractLinks(value, encoding)
            refs |= getObjectsFromLinks(obj, links)
    updateReferences(obj, refs)


def modifiedDexterity(obj, event):
    """ a dexterity based object was modified """
    if not check_linkintegrity_dependencies(obj):
        return
    fti = getUtility(IDexterityFTI, name=obj.portal_type)
    schema = fti.lookupSchema()
    additional_schema = getAdditionalSchemata(context=obj,
                                              portal_type=obj.portal_type)
    schemas = [i for i in additional_schema] + [schema]
    refs = set()
    for schema in schemas:
        for name, field in getFieldsInOrder(schema):
            if isinstance(field, RichText):
                # Only check for "RichText" ?
                value = getattr(schema(obj), name)
                if not value or not getattr(value, 'raw', None):
                    continue
                links = extractLinks(value.raw)
                refs |= getObjectsFromLinks(obj, links)
    updateReferences(obj, refs)


def updateReferences(obj, refs):
    """Renew all linkintegritry-references.

    Search the zc.relation catalog for linkintegritry-references for this obj.
    Drop them all and set the new ones.
    TODO: Might be improved by not changing anything if the links are the same.
    """
    intids = getUtility(IIntIds)
    try:
        int_id = intids.getId(obj)
    except KeyError:
        # In some cases a object is not yet registered by the intid catalog
        try:
            int_id = intids.register(obj)
        except NotYet:
            return
    catalog = getUtility(ICatalog)
    # unpack the rels before deleting
    old_rels = [i for i in catalog.findRelations(
        {'from_id': int_id,
         'from_attribute': referencedRelationship})]
    for old_rel in old_rels:
        catalog.unindex(old_rel)
    for ref in refs:
        _setRelation(obj, referencedRelationship, ref)


def check_linkintegrity_dependencies(obj):
    if not getToolByName(obj, 'portal_url', None):
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
