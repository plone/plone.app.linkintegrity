# -*- coding: utf-8 -*-
"""Link Integrity - link retriever methods.
"""
from .compat import IBaseObject
from .compat import TextField
from plone.app.linkintegrity.interfaces import IRetriever
from plone.app.linkintegrity.parser import extractLinks
from plone.app.textfield import RichText
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.schema import getFieldsInOrder


@implementer(IRetriever)
@adapter(IBaseObject)
class ATGeneral(object):
    """General retriever for AT that extracts URLs from (rich) text fields.
    """

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them.
        """
        links = set()
        for field in self.context.Schema().fields():
            if isinstance(field, TextField):
                accessor = field.getAccessor(self.context)
                encoding = field.getRaw(self.context, raw=1).original_encoding
                if accessor is not None:
                    value = accessor()
                else:
                    # Fields that have been added via schema extension do
                    # not have an accessor method.
                    value = field.get(self.context)
                links |= set(extractLinks(value, encoding))
        return links


@implementer(IRetriever)
@adapter(IDexterityContent)
class DXGeneral(object):
    """General retriever for DX that extracts URLs from (rich) text fields.
    """

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them.
        """
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schema = fti.lookupSchema()
        additional_schema = getAdditionalSchemata(
            context=self.context, portal_type=self.context.portal_type)
        schemas = [i for i in additional_schema] + [schema]
        links = set()
        for schema in schemas:
            for name, field in getFieldsInOrder(schema):
                if isinstance(field, RichText):
                    value = getattr(schema(self.context), name)
                    if not value or not getattr(value, 'raw', None):
                        continue
                    links |= set(extractLinks(value.raw))
        return links
