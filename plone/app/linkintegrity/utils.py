from base64 import b64encode, b64decode
from zlib import compress, decompress


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
        yield data[pos+1:end]
        data = data[end:]


def encodeRequestData((body, env)):
    """ encode the relevant request data, i.e. body and env """
    def _iterdata():
        yield body
        for key, val in env.iteritems():
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


def encodeInts(ints):
    """ encode a list of integers into a string """
    return ':'.join(map(str, ints))


def decodeInts(data):
    """ decode a string to a list of integers """
    return map(int, data.split(':'))

