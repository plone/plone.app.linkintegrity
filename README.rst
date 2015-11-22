plone.app.linkintegrity
=======================

Overview
--------

This package implement link integrity checking in Plone.  It makes use of the
zope3 event system in order to modify Plone itself as little as possible.


Features
--------

This package handles deleting an item in the Plone-User-interface (i.e.
deleting items in the view `folder_contents` via Actions / Delete).

Whenever an object that is referred to by another one via an `<a>` or `<img>`
tag is going to be deleted, a confirmation form is presented to the user.
They can then decide to indeed delete the object, breaching link
integrity of the site or first edit the objects that link to the item in
question.

Changes in 3.0
--------------

- Linkintegrity-relations are no longer stored in reference_catalog of
  Products.Archetypes. Instead it used zc.relation.

- No longer intercept the request on ``manage_deleteObjects``.
  This means that deleting with other methods (like manage_deleteObjects,
  plone.api.content.delete, ttw in the ZMI) no longer warns about
  linkintegrity-breaches. It now simply adds information about
  linkintegrity-breaches in the user-interface.

- LinkIntegrityNotificationException is not longer thrown anywhere.



Refresh the linkintegrity site status
-------------------------------------

In the case you'll need to update/refresh the linkintegrity status of the
whole site, you can call the ``@@updateLinkIntegrityInformation`` view.

It can be really slow operation.

Customization
-------------

On object created, added, modified events the ``modifiedContent`` handler
is called. This handler adapts an ``IRetriever`` object if found.
The package comes with two general adapters for Dexterity and Archetypes.
You can easily write custom adapters implementing the ``IRetriever``
interface for your contenttype. Look at the ``retriever`` module in this
package for examples.

API
---

To check if there would be breaches when deleting one or more objects
you can use the follwing code:

.. code-block:: python

    from plone import api
    portal = api.portal.get()
    view = api.content.get_view(
        'delete_confirmation_info',
        portal,
        self.request)
    breaches = view.get_breaches([obj1, obj2])

`get_breaches` ignores breaches originating from any items that would also be
deleted by deleting the items (and their chidlren if an item is a folder).

Each breach in `breaches` is a dictionary with a `target` (a dict with some
info on the object to be deleted) and a list of `sources`.
Each source is again a dict with `uid`, `title`, `url` and `accessible`
(a boolean telling you if the user can access that source).


To check items for links in html-fields you can use the methods in
``plone.app.linkintegrity.utils``:



``utils.hasIncomingLinks(obj)``
    Test if an object is linked to by other objects

``utils.hasOutgoingLinks(obj)``
    Test if an object links to other objects

``utils.getIncomingLinks(obj)``
    Return a generator of incoming relations

``utils.getOutgoingLinks(obj)``
    Return a generator of outgoing relations

``utils.linkintegrity_enabled()``
    Test if linkintegrity-feature is enables for users
