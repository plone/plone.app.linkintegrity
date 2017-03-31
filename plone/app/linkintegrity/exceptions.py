# -*- coding: utf-8 -*-
from OFS.ObjectManager import BeforeDeleteException
from zope.interface import implementer
from zope.interface import Interface


class ILinkIntegrityNotificationException(Interface):
    """An exception indicating a prevented link integrity breach.
    """


@implementer(ILinkIntegrityNotificationException)
class LinkIntegrityNotificationException(BeforeDeleteException):
    """An exception indicating a prevented link integrity breach.
    """

    def __str__(self):
        args = self.args
        if args and isinstance(args, tuple):
            return repr(args[0])
        return super(LinkIntegrityNotificationException, self).__str__()
