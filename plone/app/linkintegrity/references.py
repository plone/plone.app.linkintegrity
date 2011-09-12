# helpers related to reference handling
#
# the following functions can prove helpful outside of `p.a.linkintegrity`,
# but they should really be integrated into `Archetypes` before anybody
# starts using them.  so for now they are provided as a convenience for
# the `plone.app.referenceintegrity` package, but other than that please
# bear in mind the gently reminder that...
#
#	NOBODY ELSE SHOULD IMPORT FROM HERE!!!
#
# you have been warned! :)

from logging import getLogger
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.exceptions import ReferenceException
from ZODB.POSException import ConflictError


def updateReferences(obj, relationship, newrefs):
    existing = set(obj.getReferences(relationship=relationship))
    for ref in newrefs.difference(existing):   # add new references and...
        try:
            obj.addReference(ref, relationship=relationship)
        except ReferenceException:
            pass
    for ref in existing.difference(newrefs):   # removed leftovers
        try:
            obj.deleteReference(ref, relationship=relationship)
        except ReferenceException:
            removeDanglingReference(obj, relationship)


def removeDanglingReference(obj, relationship):
    # try to get rid of the dangling reference, but let's not
    # have this attempt to clean up break things otherwise...
    # iow, the `try..except` is there, because internal methods
    # of the reference catalog are being used directly here.  any
    # changes regarding these shouldn't break things over here,
    # though...
    try:
        refcat = getToolByName(obj, 'reference_catalog')
        uid, dummy = refcat._uidFor(obj)
        brains = refcat._queryFor(uid, None, relationship=relationship)
        objs = refcat._resolveBrains(brains)
        for obj in objs:
            refcat._deleteReference(obj)
    except ConflictError:
        raise
    except:
        getLogger(__name__).warning('dangling "linkintegrity" '
            'reference to %r could not be removed.', obj)
