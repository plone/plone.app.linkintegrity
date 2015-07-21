# -*- coding: utf-8 -*-
from urllib import unquote
from urlparse import urlsplit

from Acquisition import aq_get
from Acquisition import aq_parent
from Products.Archetypes.Field import TextField
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from plone.app.linkintegrity.parser import extractLinks
from zExceptions import NotFound
from zope.component import getUtility
from zope.publisher.interfaces import NotFound as ztkNotFound
from zope.schema import getFieldsInOrder

# To support various Plone versions, we need to support various UUID resolvers
# This follows Kupu, TinyMCE and plone.app.uuid methods, in a similar manner to
# plone.outputfilters.browser.resolveuid
from plone.app.uuid.utils import uuidToObject
from Products.CMFPlone.interfaces import IPloneSiteRoot

# We try to import dexterity related modules, or modules used just if
# dexterity is around
from plone.app.textfield import RichText
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from z3c.relationfield import RelationValue
from z3c.relationfield.event import _setRelation
from zope.intid.interfaces import IIntIds


def _resolveUID(uid):
    res = uuidToObject(uid)
    if res is not None:
        return res
    return None


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
        obj = _resolveUID(uid)
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
    pu = getToolByName(obj, 'portal_url', None)
    if pu is None:
        # `getObjectFromLinks` is not possible without access
        # to `portal_url`
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
    for ref in refs:
        _setRelation(obj, referencedRelationship, ref)


def modifiedDexterity(obj, event):
    """ a dexterity based object was modified """
    pu = getToolByName(obj, 'portal_url', None)
    if pu is None:
        # `getObjectFromLinks` is not possible without access
        # to `portal_url`
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
                if not value:
                    continue
                links = extractLinks(value.raw)
                refs |= getObjectsFromLinks(obj, links)
    for ref in refs:
        _setRelation(obj, referencedRelationship, ref)
