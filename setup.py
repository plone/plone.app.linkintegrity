from setuptools import setup, find_packages

setup(name = 'plone.app.linkintegrity',
      version = '1.0b2',
      description = 'Manage link integrity in Plone.',
      keywords = 'link integrity plone',
      author = 'Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://svn.plone.org/svn/plone/plone.app.linkintegrity/',
      download_url = 'http://cheeseshop.python.org/pypi/plone.app.linkintegrity/',
      license = 'GPL',
      packages = find_packages(),
      namespace_packages = ['plone.app'],
      include_package_data = True,
      install_requires = ['setuptools',],
      platforms = 'Any',
      zip_safe = False,
      classifiers = [
        'Development Status :: 4 - Beta',
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
      long_description = """\
        This package tries to integrate PLIP 125, link integrity checking,
        into Plone using the zope3 event system. """,
)

