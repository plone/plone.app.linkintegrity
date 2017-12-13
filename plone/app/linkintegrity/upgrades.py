# -*- coding: utf-8 -*-
from plone.app.linkintegrity.utils import ensure_intid
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.uuid.utils import uuidToObject
try:
    from Products.Archetypes.config import REFERENCE_CATALOG
except ImportError:
    REFERENCE_CATALOG = "reference_catalog"
from Products.CMFCore.utils import getToolByName
from z3c.relationfield import RelationValue
from z3c.relationfield.event import _setRelation
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import logging
log = logging.getLogger(__name__)


def migrate_linkintegrity_relations(context):
    """Migrate linkintegrity-relation from reference_catalog to zc.relation.
    """
    reference_catalog = getToolByName(context, REFERENCE_CATALOG, None)
    intids = getUtility(IIntIds)
    if reference_catalog is not None:
        # Only handle linkintegrity-relations ('isReferencing').
        # [:] copies the full result list to make sure
        # it won't change while we delete references below
        for brain in reference_catalog(relationship=referencedRelationship)[:]:
            try:
                source_obj = uuidToObject(brain.sourceUID)
                target_obj = uuidToObject(brain.targetUID)
            except AttributeError:
                source_obj = target_obj = None
            if source_obj is None or target_obj is None:
                # reference_catalog may be inconsistent
                log.info('Cannot delete relation since the relation_catalog is inconsistent.')   # noqa: E501
                continue
            # Delete old reference
            reference_catalog.deleteReference(
                source_obj, target_obj, relationship=referencedRelationship)

            # Trigger the recreation of linkintegrity-relation in
            # the relation_catalog (zc.relation)
            target_id = ensure_intid(target_obj, intids)
            if target_id is None:
                continue
            rel = RelationValue(target_id)
            _setRelation(source_obj, referencedRelationship, rel)
