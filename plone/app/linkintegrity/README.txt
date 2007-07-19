plone.app.linkintegrity

Description

  This product tries to integrate PLIP 125 into Plone using the zope3 event
  system in order to modify Plone itself as little as possible.

Status

  At the moment the code handles one of the two use cases of PLIP 125,
  deleting an item. Whenever an object that is referred to by another one by
  an <a> or <img> tag is going to be deleted, Plone's regular flow of actions
  is "interrupted" and a confirmation form is presented to the user. If they
  then decide to indeed delete the object the original request is followed
  through, hereby breaching link integrity of the site.

  This process is implemented independently of how the object is deleted (as
  long as ObjectManager's `_delObject` is used ultimatively) and what request
  is used to do it. A more detailed explanation of how this works can be found
  in NOTES.txt.

  The second use case of PLIP 125, which is provides better handling of moved
  items, is implemented by plone.app.redirector, available from
  https://svn.plone.org/svn/plone/plone.app.redirector/.
