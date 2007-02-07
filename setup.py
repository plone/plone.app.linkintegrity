from setuptools import setup, find_packages
import sys, os

version = '1.0a2'

setup(name='plone.app.linkintegrity',
      version=version,
      description="link integrity management",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='link integrity plone',
      author='Andi Zeidler',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://svn.plone.org/svn/plone/plone.app.linkintegrity',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
