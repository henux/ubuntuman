# -*- Encoding: UTF-8 -*-
# Copyright (c) 2009 Henri Häkkinen, Elián Hanisch.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import supybot.log as log
import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks

import sys

class UbuntuMan(callbacks.Plugin):
    """This plugin provides commands for displaying UNIX manual pages from
    the Ubuntu Manpage repository."""

    def __init__(self, irc):
        self.__parent = super(UbuntuMan, self)
        self.__parent.__init__(irc)

    def man(self, irc, msg, args, command, optlist):
        """<command> [--rel <release>] [--lang <language>] [--nocache]

        Displays a manual page from the Ubuntu Manpage Repository."""
        # TO BE IMPLEMENTED
        pass

    def manurl(self, irc, msg, args, command, optlist):
        """<command> [--rel <release>] [--lang <language>]

        Gives the URL to the full manual page in the Ubuntu Manpage
        Repository."""
        # TO BE IMPLEMENTED
        pass

    def mancache(self, irc, msg, args, command, optlist):
        """<operation>

        Operates the local manual page cache. <operation> can be:
        flush [<command>]
        size
        """
        # TO BE IMPLEMENTED
        pass

    man = wrap(man, ['something', getopts({'rel':'something', 'lang':'something', 'nocache':'something'}))
    manurl = wrap(manurl, ['something', getopts({'rel':'something', 'lang':'something'})])
    mancache = wrap(mancache, ['something'])


Class = UbuntuMan


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
