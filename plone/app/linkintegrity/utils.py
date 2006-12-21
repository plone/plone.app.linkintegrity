from base64 import b64encode, b64decode
from zlib import compress, decompress
from pickle import dumps, loads


def encode(obj):
    """ pickle, compress and encode an object """
    data = dumps(obj, -1)               # pickle using highest protocol
    return b64encode(compress(data))    # compress and encode


def decode(data):
    """ decode, uncompress and unpickle an object """
    data = decompress(b64decode(data))
    return loads(data)

