from plone.app.textfield import RichTextValue
from zope.lifecycleevent import modified


def set_text(obj, text):
    obj.text = RichTextValue(text)
    modified(obj)
