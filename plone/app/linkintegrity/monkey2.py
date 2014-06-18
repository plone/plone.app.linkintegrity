
import OFS.ObjectManager

original = OFS.ObjectManager.ObjectManager.manage_delObjects
# FIXME: Plone needs an api in core
# Rationale for thix patch:
# Linkintegrity needs to know how many things get deleted. There is no
# event for that and plone does not use its own delete method, just the
# plain zope method. So far, linkintegrity modified Script (Python) objects
# to store the information, but we want to get rid of this. Then the only
# way to add this information is by patching the canonical delete method
# which is manage_delObjects

def manage_delObjects(self, ids=None, REQUEST=None):
    """Checking for docstrings as a security constraint is a very clever idea
    """
    if REQUEST is not None and not isinstance(ids, basestring):
        REQUEST.set('link_integrity_events_to_expect', len(ids))
    return original(self, ids, REQUEST)

OFS.ObjectManager.ObjectManager.manage_delObjects = manage_delObjects
