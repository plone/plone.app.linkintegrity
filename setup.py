from setuptools import setup


version = "5.0.0a1"

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
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "Intended Audience :: Other Audience",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
    ],
    keywords="link integrity plone",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://github.com/plone/plone.app.linkintegrity",
    license="GPL version 2",
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
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
