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

Using plone.app.linkintegrity in a WSGI application using repoze.zope2
----------------------------------------------------------------------

If you are deploying Plone using repoze.zope2 in a WSGI pipeline, then
the stock LinkIntegrity won't work. To make it work, you need the following:

 - repoze.zope2 1.0.2 or later
 - ZODB 3.8.2 or later

These two will ensure that the "views on exceptions" functionality, which
plone.app.linkintegrity uses, is available.

Next, make sure that the repoze.retry#retry middleware is used, and that
it will handle stock Retry exceptions. With repoze.retry 0.9.3 or later,
that is the default. With earlier versions, you can configure it explicitly.
For example::

    [app:zope2]
    paste.app_factory = repoze.obob.publisher:make_obob
    repoze.obob.get_root = repoze.zope2.z2bob:get_root
    repoze.obob.initializer = repoze.zope2.z2bob:initialize
    repoze.obob.helper_factory = repoze.zope2.z2bob:Zope2ObobHelper
    zope.conf = /Users/optilude/Development/Plone/Code/Build/uber/plone3.x-repoze/parts/instance-debug/etc/zope.conf

    [filter:retry]
    use = egg:repoze.retry#retry
    retryable = ZODB.POSException:ConflictError ZPublisher.Publish:Retry

    [filter:errorlog]
    use = egg:repoze.errorlog#errorlog
    path = /__error_log__
    keep = 50
    ignore = 
        paste.httpexceptions:HTTPUnauthorized
        paste.httpexceptions:HTTPNotFound
        paste.httpexceptions:HTTPFound
    
    [pipeline:main]
    pipeline =
        retry
        egg:repoze.tm#tm
        egg:repoze.vhm#vhm_xheaders
        errorlog
        zope2

    [server:main]
    use = egg:Paste#http
    host = 127.0.0.1
    port = 8080
    threadpool_workers = 1
    threadpool_spawn_if_under = 1

