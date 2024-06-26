from setuptools import find_packages
from setuptools import setup


version = "4.0.7.dev0"

setup(
    name="plone.app.linkintegrity",
    version=version,
    description="Manage link integrity in Plone.",
    long_description="\n\n".join(
        [
            open("README.rst").read(),
            open("CHANGES.rst").read(),
        ]
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "Intended Audience :: Other Audience",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
    ],
    keywords="link integrity plone",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://github.com/plone/plone.app.linkintegrity",
    license="GPL version 2",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "plone.app.intid",
        "plone.app.relationfield",
        "plone.base",
        "plone.dexterity",
        "Products.GenericSetup",
        "Products.statusmessages",
        "plone.app.textfield",
        "plone.app.uuid",
        "plone.registry",
        "plone.uuid",
        "Zope",
        "z3c.relationfield",
        "zc.relation",
        "zope.intid",
        "zope.keyreference",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.namedfile",
            "plone.testing",
        ],
    },
    platforms="Any",
    zip_safe=False,
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
