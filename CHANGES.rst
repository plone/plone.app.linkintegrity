Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.6.2 (2023-10-16)
------------------

Bug fixes:


- Report sources once per breach in delete_confirmation_info.
  [jaroel] (#95)


3.6.1 (2022-04-28)
------------------

Bug fixes:


- Test fix: only load plone.app.contenttypes migration layer on Python 2.
  [maurits] (#641)


3.6.0 (2022-02-23)
------------------

New features:


- Track link integrity of referenced PDFs and other site objects in IFRAME SRC references. (#84)


3.5.0 (2021-12-29)
------------------

New features:


- Track integrity of video and audio files in HTML source tags. (#77)


3.4.1 (2021-03-02)
------------------

Bug fixes:


- Use base64.decodebytes instead of decodestring when possible.
  Fixes Python 3.9 compatibility in the tests.
  [maurits] (#81)


3.4.0 (2021-02-23)
------------------

New features:


- Drop Plone 5.1 support, due to possible incompatibility with older plone.app.uuid.
  [maurits] (#79)


Bug fixes:


- Fix Unauthorized exception when you edit a page that links to another page that you are not allowed to see.
  Fixes `issue 79 <https://github.com/plone/plone.app.linkintegrity/issues/79>`_.
  [maurits] (#79)


3.3.14 (2020-09-07)
-------------------

Bug fixes:


- Fixed deprecation warning for ComponentLookupError.
  [maurits] (#3130)


3.3.13 (2020-04-20)
-------------------

Bug fixes:


- Minor packaging updates. (#1)


3.3.12 (2019-10-12)
-------------------

Bug fixes:


- Explicitly load zcml of dependencies, instead of using ``includeDependencies``.
  [maurits] (#2952)


3.3.11 (2019-06-27)
-------------------

Bug fixes:


- Add missing i18n:translate calls
  [erral] (#73)


3.3.10 (2019-06-19)
-------------------

Bug fixes:


- Accept to have a broken object w/o aq_parent in test.
  [jensens] (#72)


3.3.9 (2019-05-01)
------------------

Bug fixes:


- Fix wrong i18n:translate to avoid ${DYNAMIC_CONTENT} in translation files
  [erral] (#69)


3.3.8 (2019-02-08)
------------------

No significant changes.


3.3.7 (2018-09-23)
------------------

Bug fixes:

- Fix tests in Python 3
  [pbauer]


3.3.6 (2018-06-19)
------------------

Bug fixes:

- Fix test to work with merged plone.login.
  [jensens]

- Python 3 compatibility.
  [pbauer]


3.3.5 (2018-04-04)
------------------

Bug fixes:

- Mark strings in delete confirmation screen translatable
  [erral]


3.3.4 (2018-02-04)
------------------

Bug fixes:

- Optimize migration of old Archetypes references.
  [davisagli]

- Prepare for Python 2 / 3 compatibility.
  [ale-rt, pbauer]


3.3.3 (2017-10-02)
------------------

New features:

- Prevent linkintegrity-handler from doing anything when it is switched of in the registry.
  This change also prevents some issues in migration from AT to DX since linkintegrity is disabled during the migration.
  [pbauer]

Bug fixes:

- Fix a missing tal condition in `delete_confirmation_info.pt` that caused a
  paragraph to be always visible, even without link breaches.
  [arsenico13]

- Fix view @@updateLinkIntegrityInformation after Language='all' no longer works.
  [pbauer]


3.3.2 (2017-08-14)
------------------

Bug fixes:

- Do not fail on invalid objects in reference_catalog.
  Fixes `issue 32 <https://github.com/plone/plone.app.linkintegrity/issues/32>`_
  and `48 <https://github.com/plone/plone.app.linkintegrity/issues/48>`_.
  [pbauer]

- Fix undeclared hard dependency on Archetypes
  [tomgross]


3.3.1 (2017-06-01)
------------------

Bug fixes:

- Improved code quality.  [gforcada]

- removed unittest2 dependency
  [kakshay21]


3.3 (2017-04-20)
----------------

New features:

- Support for any ``zc.relation`` refercences being checked by ``delete_confirmation_info`` dialog,
  not only references linked in text.
  [thet]

Bug fixes:

- PEP8.
  [thet]

- Update code to follow Plone styleguide.
  [gforcada]

3.2.2 (2017-04-02)
------------------

New features:

- Use plone.namedfile for testing images
  [didrix]

Bug fixes:

- Fix typo in logging method
  [tomgross]


3.2.1 (2017-02-20)
------------------

Bug fixes:

- Show breakage info even if catalog is out of sync
  [tomgross]


3.2.0 (2017-02-12)
------------------

New features:

- Compatibility with ZCatalog 4 (upgrade steps)
  [pbauer, jensens]


3.1 (2016-12-30)
----------------

New features:

- Information about contents within a selected folder for deletion.
  This information contains number of deleted objects,
  number of subfolders and number of published objects.
  [karalics]


3.0.8 (2016-11-09)
------------------

Bug fixes:

- Add coding headers on python files.
  [gforcada]

- Remove hard dependency on Archetypes (again).
  [davisagli]


3.0.7 (2016-09-16)
------------------

Bug fixes:

- Use transaction savepoints while calling @@updateLinkIntegrityInformation
  to keep memory usage under control.
  [ale-rt]


3.0.6 (2016-08-17)
------------------

Bug fixes:

- Fix object url in delete confirmation
  [vangheem]

- Use zope.interface decorator.
  [gforcada]


3.0.5 (2016-04-15)
------------------

Fixes:

- Fix test isolation problems: if a test calls transaction.commit() directly or
  indirectly it can not be an integration test, either avoid the commit or
  change the layer into a functional one.
  Fixes: https://github.com/plone/plone.app.linkintegrity/issues/36
  [gforcada]


3.0.4 (2016-02-02)
------------------

Fixes:

- Handle links that do not have an intid yet. Should help with
  upgrade issues.
  [vangheem]

- make handler.findObject() work when the webserver rewrites the portal name
  [tschorr]


3.0.3 (2015-11-26)
------------------

New:

- Introduce IRetriever adapter for customization flexibility.
  [tomgross]


3.0.2 (2015-09-27)
------------------

- Remove xml:lang and wrong xmlns from delete_confirmation_info.pt.
  [vincentfrentin]


3.0.1 (2015-09-11)
------------------

- Don't show delete_confirmation_info twice in delete_confirmation. Fixes #27
  [pbauer]


3.0 (2015-09-08)
----------------

- Drop the Archetypes-dependency by switching to use zc.relation instead of
  reference_catalog (Products.Archetypes).
  [bloodbare, pbauer, vangheem]

- No longer intercept the request on manage_deleteObjects. Instead only
  inject a warning in delete_confirmation. This means that deleting with
  other methods (like manage_deleteObjects, plone.api.content.delete, ttw
  in the ZMI) no longer warns about linkintegrity-breaches.
  [bloodbare, pbauer, vangheem]

- LinkIntegrityNotificationException is not longer thrown anywhere.
  [bloodbare, pbauer, vangheem]


2.1.2 (2015-05-04)
------------------

- Fix html structure in confirmation.pt
  [vincentfretin]


2.1.1 (2015-03-13)
------------------

- When using the update view for dexterity objects, only call the method if
  object provides IReferenceable
  [frapell]

- Removed Zope 2.10 compatibility from publisher monkey patch.
  [davisagli]


2.1.0 (2014-10-23)
------------------

- Read the enable_link_integrity_checks setting from plone.app.registry
  instead of from the portal_properties.
  [timo]

- Restructure package to fully support dexterity framework. Use two different
  test layers in ``plone.app.testing``, migrate all doctests into real
  TestCases.
  [saily, do3cc]


2.0.0 (2014-04-13)
------------------

- Adapt tests for removal of DT, DD and DL elements.
  Remove DL's from portal message in templates.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink, mrtango]


1.5.6 (2015-08-13)
------------------

- Backport improvements to ``@@updateLinkIntegrityInformation`` from
  plone5 branch.
  [pbauer]


1.5.4 (2014-01-27)
------------------

- Added support for sub path after uid of resolveuid
  [hoka]


1.5.3 (2013-08-13)
------------------

- Set a maxsize when decompressing request data.
  [davisagli]

- Fixed dexterity referenceablebehavior integration.
  [maurits]

- Fix #13681, documents referencing each other will now also trigger a link
  integrity warning.
  [do3cc]


1.5.2 (2013-05-23)
------------------

- Exceptions now return the repr() and not the str() of the object. This way
  we avoid, for File content types, loading the whole object data into memory.
  This closes https://dev.plone.org/ticket/13519
  [ericof]


1.5.1 (2013-03-05)
------------------

- unicode links should not raise errors. Fixes https://dev.plone.org/ticket/13468
  [vangheem]

- Dexterity: use zope.lifecycleevent instead of zope.app.container
  interfaces for Plone 4.3 support.
  [jone]

- Avoid a bug during link integrity check when a source or target of the
  reference has been already removed during the deletion process.
  This can happen during large delete processes.
  [thomasdesvenain]
- Monkey patch the Zope HTTPResponse status_code to include a mapping for
  linkintegritynotificationexception, to return a 200 code.
  [thepjot]

1.5.0 (2013-01-17)
------------------
- Fix a remove confirmation view bug.
  Displays the portal type title rather than the portal type name.
  This change also broke some tests that were checking for the name
  rather than the title, but I just fixed those.
  [jianaijun]

- Added support for Dexterity content types.  Link integrity
  support for Dexterity requires the plone.app.referenceablebehavior
  behavior to be enabled so that the Dexterity item can be used
  with Archetypes references.
  [jpgimenez]


1.4.7 (2012-10-03)
------------------

- Fixes UnicodeDecodeError on extractLinks
  This closes https://dev.plone.org/ticket/13168
  [ericof]


1.4.6 (2012-07-02)
------------------

- No more zope.app dependencies.
  [hannosch]

- Remove hard dependency on Archetypes.
  [davisagli]

1.4.5 - 2012-02-24
------------------

- Fix an error in handling absolute links to objects within the portal,
  which prevented references from being created based on those links.
  This closes https://dev.plone.org/ticket/12402
  [davisagli]

- Stabilize the sort order of breach sources returned for the
  confirmation view.
  [davisagli]

- Use the `get` method to retrieve the field value if the instance
  does not provide an accessor method. This is the case for instance
  for fields which have been added via schema extension.
  [malthe]

- Support resolveuid/UID references explicitely, by parsing and resolving
  these ourselves instead of relying on a view or script (which doesn't work).
  This fixes linkintegrity for sites with link-by-uid turned on.
  This closes https://dev.plone.org/ticket/12104
  [mj]

1.4.4 - 2011-10-04
------------------

- Add integrity references for cloned content items.
  This fixes http://dev.plone.org/plone/ticket/12254.
  [gotcha]

- Skip events subscribers during copy&paste of content items.
  This fixes http://dev.plone.org/plone/ticket/12206.
  [gotcha]

- Provide Archetypes-only fallback if `plone.uuid` is not available,
  restoring compatibility with Plone 4.0.x.
  [witsch]


1.4.3 - 2011-09-14
------------------

- Fix integrity reference generation for content not accessible by the editor.
  [witsch]

- Fix handling of relative links instead of relying on Acquisition.
  [witsch]


1.4.2 - 2011-07-04
------------------

- Objects that don't have a UUID cannot cause linkintegrity-breaches.
  This fixes http://dev.plone.org/plone/ticket/11904.
  [WouterVH]

- Adjust tests to the changed URL used for the `folder_contents` view.
  This refs http://dev.plone.org/plone/ticket/10122.
  [gotcha]

- Add new tests to prove `isLinked` can now be used safely.
  This refs http://dev.plone.org/plone/ticket/7784.
  [gotcha]


1.4.1 - 2011-05-12
------------------

- Fix decoding of colon-delimited list of confirmed oids in the request
  when one of the oids contains a colon.
  [davisagli]

- Add MANIFEST.in.
  [WouterVH]


1.4.0 - 2011-01-03
------------------

- Use `plone.uuid` to look up content UUIDs.
  [toutpt, davisagli]


1.3.3 - 2011-07-05
------------------

- Add new tests to prove `isLinked` can now be used safely.
  This refs http://dev.plone.org/plone/ticket/7784.
  [gotcha]


1.3.2 - 2011-05-12
------------------

- Fix decoding of colon-delimited list of confirmed oids in the request
  when one of the oids contains a colon.
  [davisagli]


1.3.1 - 2010-08-08
------------------

- Adjusted tests to no longer rely on sub-collections.
  [hannosch]

- Use the official ``aq_get`` API to acquire the request from a context.
  [hannosch]


1.3.0 - 2010-07-18
------------------

- Update license to GPL version 2 only.
  [hannosch]


1.3b2 - 2010-06-13
------------------

- Avoid using the deprecated five:implements directive.
  [hannosch]


1.3b1 - 2010-06-03
------------------

- Fix findObject to also catch the ZTK NotFound exception which may be
  raised by request.traverseName. Fixes
  http://dev.plone.org/plone/ticket/10549
  [davisagli]


1.3a5 - 2010-05-01
------------------

- Properly handle retry exception instead of getting the special-casing of
  exception handling when publishing with debug=1
  [davisagli]


1.3a4 - 2010-03-06
------------------

- Do not abort if a text field is `None`. In that case the HTML parser
  raises a `TypeError` instead of an `HTMLParseError`.
  [wichert]


1.3a3 - 2010-02-18
------------------

- Updated templates to match recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981
  [spliter]

- Convert test setup to `collective.testcaselayer`.
  [witsch]

- Updated tests to not rely on specific CSS classes or ids.
  Refs http://dev.plone.org/plone/ticket/10231
  [limi, witsch]


1.3a2 - 2009-12-02
------------------

- Fix issue with the final submission of the delete confirmation page in
  Zope 2.12. This closes http://dev.plone.org/plone/ticket/9699.
  [davisagli]


1.3a1 - 2009-11-17
------------------

- Access the subtopics page directly since the tab is now hidden by default.
  [davisagli]

- Partially disable the test regarding the undo log as the outcome differs
  between Plone 3 and 4, probably due to changes in the test setup.
  Refs http://dev.plone.org/plone/ticket/7784
  [witsch]

- Add test to verify undo log entries are not longer missing after removing
  items via the "delete" action.  Refs http://dev.plone.org/plone/ticket/7784
  [witsch]


1.2 - 2009-10-10
----------------

- Also catch `NotFound` exceptions when trying to resolve linked objects.
  [optilude]


1.1 - 2009-08-31
----------------

- Make compatible with repoze.zope2. See README.txt for notes on how to
  deploy.
  [optilude]

- Don't use id() to record confirmed items. It can change on request
  boundaries. Use an encoded _p_oid instead.
  [optilude]

- Also regard traversal adapters when trying to resolve links into their
  corresponding objects.
  [witsch]

- Fix some tests to make sure that text values are treated as text/html
  in Zope 2.12, whose zope.contenttype is stricter when guessing the
  mimetype.
  [davisagli]

- Don't install the exception hook in Zope 2.12 where it is no longer
  needed and breaks exception handling.
  [davisagli]


1.0.12 - 2009-06-03
-------------------

- Compare UIDs instead of objects during cleanup of breach information in
  order to avoid expensive hashing in "... in ..." expressions.  This
  makes removing linked objects much faster.
  [regebro]


1.0.11 - 2008-11-15
-------------------

- Fix code to not silently swallow `ConflictErrors`.
  [witsch]

- Fix issue with dangling references to already removed objects.
  Fixes http://dev.plone.org/plone/ticket/8349 and
  http://dev.plone.org/plone/ticket/8390.
  [witsch]


1.0.10 - 2008-07-07
-------------------

- Fixed the recognizing of links to files (or any object) with a
  space in the id.  Fixes http://dev.plone.org/plone/ticket/8167.
  [maurits]

- Updated tests to work with LinguaPlone by unmarking the creation
  flag on new objects.
  [maurits]


1.0.9 - 2008-05-08
------------------

- Use acquisition API to support the "philikon-aq" branch.
  [witsch]

- Fix a problem with updating link integrity references during a
  request which trying to delete multiple other objects.
  [witsch]


1.0.8 - 2008-04-21
------------------

- Added missing i18n markup to `confirmation.pt`, also fixing
  http://dev.plone.org/plone/ticket/7995.
  [witsch]


1.0.7 - 2008-03-27
------------------

- Fixed accidental removal of references not related to link integrity.
  [dunny]


1.0.6 - 2008-03-08
------------------

- Added missing namespace declaration to avoid the warning about it.
  [wiggy]


1.0.5 - 2008-02-13
------------------

- Added missing i18n markup to confirmation.pt. This closes
  http://dev.plone.org/plone/ticket/7688.
  [hannosch]


1.0.4 - 2008-01-03
------------------

- Handle `IObjectRemovedEvents` with no attached request object.
  [witsch]

- Updated tests to work with Plone 4.0.
  [hannosch]

- Referencing items are now listed in alphabetical order
  [witsch]


1.0.3 - 2007-12-05
------------------

- Fixed setting up the test layer after GenericSetup update
  [witsch]


1.0.2 - 2007-11-07
------------------

- Fixed parser error when handling malformed HTML
  [witsch]

- Fixed security issue due to using pickles (see CVE-2007-5741)
  [witsch]


1.0.1 - 2007-09-10
------------------

- Added view for updating link integrity information for all site content
  [witsch]

- Made code in info.py more tolerant when encountering missing property
  sheets.
  [hannosch]


1.0 - 2007-08-16
----------------

- Minor bug fixes and enhancements
  [witsch]


1.0rc1.1 - 2007-07-12
---------------------

- Bug and test fixes after upgrade to Zope 2.10.4
  [witsch]


1.0rc1 - 2007-07-08
-------------------

- Bugfixes & additional tests
  [witsch]


1.0b3 - 2007-05-04
------------------

- No changes.

1.0b2 - 2007-04-30
------------------

- Integration of Plone's "delete confirmation" page
  [witsch]


1.0b1 - 2007-03-03
------------------

- Fix tests in regard to changed `folder_contents` and unicode issues
  [witsch]

- Updates to the monkey patch needed for five exceptions
  [wiggy]


1.0a2 - 2007-02-07
------------------

- Bugfixes & other minor enhancements
  [witsch]

- Eggification and move into plone.app namespace
  [optilude]

- Proof of concept & initial version
  [witsch]

- Initial package structure.
  [zopeskel]
