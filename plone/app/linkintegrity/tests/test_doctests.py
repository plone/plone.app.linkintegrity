# -*- coding:utf-8 -*-
from plone.testing import layered
from plone.app.linkintegrity import testing

import doctest
import os
import re
import unittest2

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

pattern = re.compile('^test.*\.(txt|rst)$')


def test_suite():
    tests = []
    for layer in (testing.PLONE_APP_LINKINTEGRITY_AT_FUNCTIONAL_TESTING,
                  testing.PLONE_APP_LINKINTEGRITY_DX_FUNCTIONAL_TESTING):

        test_directory = layer.__bases__[-1].directory
        path = os.path.join(os.path.dirname(testing.__file__),
                            test_directory, 'tests')

        # Skip non-existing directories
        if not os.path.isdir(path):
            continue

        for name in os.listdir(path):
            if pattern.search(name):
                tests.append(
                    layered(
                        doctest.DocFileSuite(
                            '{0:s}/tests/{1:s}'.format(test_directory, name),
                            package='plone.app.linkintegrity',
                            optionflags=OPTIONFLAGS,
                        ),
                        layer=layer
                    )
                )

    return unittest2.TestSuite(tests)
