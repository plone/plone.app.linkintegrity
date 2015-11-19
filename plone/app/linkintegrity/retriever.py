""" Link Integrity - link retriever methods """

from plone.app.linkintegrity.interfaces import IRetriever
from plone.app.linkintegrity.parser import extractLinks
from zope.component import adapter
from zope.interface import implementer
from Products.Archetypes.Field import TextField
from Products.Archetypes.interfaces import IBaseObject


@implementer(IRetriever)
@adapter(IBaseContent)
class ATGeneral(object):
    """General retriever for AT that extracts URLs from (rich) text fields.
    """

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
	links = set()
	for field in self.context.Schema().fields():
	    if isinstance(field, TextField):
		accessor = field.getAccessor(obj)
		encoding = field.getRaw(obj, raw=1).original_encoding
		if accessor is not None:
		    value = accessor()
		else:
		    # Fields that have been added via schema extension do
		    # not have an accessor method.
		    value = field.get(obj)
		links |= extractLinks(value, encoding)
	return links


@implementer(IRetriever)
@adapter(IDexterityContent)
class ATGeneral(object):
    """General retriever for DX that extracts URLs from (rich) text fields.
    """

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schema = fti.lookupSchema()
        additional_schema = getAdditionalSchemata(
            context=self.context, portal_type=self.context.portal_type)
        schemas = [i for i in additional_schema] + [schema]
        links = set()
        for schema in schemas:
            for name, field in getFieldsInOrder(schema):
                if isinstance(field, RichText):
                   value = getattr(schema(obj), name)
                   if not value or not getattr(value, 'raw', None):
                      continue
                   links |= extractLinks(value.raw)
        return links

