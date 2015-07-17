# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from plone.app.linkintegrity.handlers import referencedRelationship
from zExceptions import BadRequest
from zc.relation.interfaces import ICatalog
from zlib import compress, decompressobj
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def isLinked(obj):
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    l = catalog.findRelations({
        'to_id': intids.getId(obj),
        'from_attribute': referencedRelationship,
    })
    return l


def decompress(data, maxsize=262144):

    dec = decompressobj()
    data = dec.decompress(data, maxsize)
    if dec.unconsumed_tail:
        raise BadRequest
    del dec

    return data


def encodeStrings(strings):
    """ compress and encode a list of strings into a single string """
    def _encode(strings):
        for string in strings:
            yield '%d:%s' % (len(string), string)
    return b64encode(compress(''.join(_encode(strings))))


def decodeStrings(data):
    """ decode and uncompress a string as a generator """
    data = decompress(b64decode(data))
    while data:
        pos = data.find(':')
        end = pos + int(data[:pos]) + 1
        yield data[pos + 1:end]
        data = data[end:]


def encodeRequestData((body, env)):
    """ encode the relevant request data, i.e. body and env """
    def _iterdata():
        yield body
        for key, val in env.iteritems():
            if isinstance(key, basestring) and isinstance(val, basestring):
                yield str(key)
                yield str(val)
    return encodeStrings(_iterdata())


def decodeRequestData(data):
    """ decode the relevant request data, i.e. body and env """
    def _pertwo():
        while True:
            yield data.next(), data.next()
    data = decodeStrings(data)
    return data.next(), dict(_pertwo())
