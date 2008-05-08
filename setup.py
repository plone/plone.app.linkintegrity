from setuptools import setup, find_packages
from os.path import join

name = 'plone.app.linkintegrity'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read().replace(name + ' - ', '')

setup(name = name,
      version = version,
      description = 'Manage link integrity in Plone.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'link integrity plone',
      author = 'Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://svn.plone.org/svn/plone/plone.app.linkintegrity/',
      download_url = 'http://cheeseshop.python.org/pypi/plone.app.linkintegrity/',
      license = 'GPL',
      packages = find_packages(),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data = True,
      install_requires = ['setuptools',],
      platforms = 'Any',
      zip_safe = False,
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Zope2',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
      ],
)

