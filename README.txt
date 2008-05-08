plone.app.linkintegrity
=======================

Overview
--------

This package tries to integrate `PLIP 125`_, link integrity checking,
into Plone.  It is making use of the zope3 event system in order to modify
Plone itself as little as possible.

  .. _`PLIP 125`: http://plone.org/products/plone/roadmap/125
  .. |---| unicode:: U+2014  .. em dash

Status
------

The code handles one of the two use cases of `PLIP 125`_, deleting an item.
Whenever an object that is referred to by another one via an `<a>` or `<img>`
tag is going to be deleted, Plone's regular flow of actions is "interrupted"
and a confirmation form is presented to the user.  If they then decide to
indeed delete the object, the original request will be replayed and this time
followed through, thereby breaching link integrity of the site.

This process is implemented independently of how the object is deleted (as
long as `OFS.ObjectManager`'s `_delObject` is used ultimatively) and what
request is used to do it.  A more detailed |---| albeit slightly outdated
|---| explanation of how this works can be found in `NOTES.txt`.

The second use case of `PLIP 125`_, which provides better handling of moved
items, is implemented by `plone.app.redirector`__.

  .. __: http://pypi.python.org/pypi/plone.app.redirector/

