from setuptools import setup, find_packages

version = '1.3b2'

setup(name = 'plone.app.linkintegrity',
      version = version,
      description = 'Manage link integrity in Plone.',
      long_description = open("README.txt").read() + '\n' +
                         open('CHANGES.txt').read(),
      keywords = 'link integrity plone',
      author = 'Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://pypi.python.org/pypi/plone.app.linkintegrity',
      license = 'GPL',
      packages = find_packages(),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data = True,
      install_requires = [
        'setuptools',
      ],
      extras_require = { 'test': [
        'collective.testcaselayer',
      ]},
      platforms = 'Any',
      zip_safe = False,
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Zope2',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
      ],
      entry_points = '''
        [z3c.autoinclude.plugin]
        target = plone
      ''',
)
