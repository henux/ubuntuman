# Copyright (c) 2008 Henri Hakkinen
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.registry as registry
import supybot.conf as conf
import urllib

class UbuntuManError(Exception):
    """Ubuntu manual page exception.  Raised when an expected section is
    not found from the manual page or other parsing related error is
    encountered."""
    pass

class UbuntuManParser:
    """Ubunutu manual page parser."""

    def __skipToSection(self, fd, sect):
        """Skips lines until '<h3>SECTION</h3>' is found and returns the
        rest of the line as a string with whitespaces normalized and HTML
        tags removed."""
        while True:
            ln = fd.readline()
            if not ln:
                raise UbuntuManError('Section ' + sect + ' not found.')
            tag = '<h3>' + sect + '</h3>'
            offs = ln.find(tag)
            if offs == -1:
                continue
            ln = ln[offs + len(tag) + 5:]
            ln = utils.web.htmlToText(ln, tagReplace='')
            ln = utils.str.normalizeWhitespace(ln)
            return ln

    def __parseName(self, fd):
        """Parse the NAME section."""
        self.name = self.__skipToSection(fd, 'NAME')

    def __parseSynopsis(self, fd):
        """Parse the SYNOPSIS section.  Only the first line is read."""
        self.synopsis = self.__skipToSection(fd, 'SYNOPSIS')

    def __parseDesc(self, fd):
        """Parse the DESCRIPTION section.  Only the first paragraph is
        read."""
        self.desc = self.__skipToSection(fd, 'DESCRIPTION')
        while True:
            ln = fd.readline()
            if not ln or ln.startswith(" </pre>") or len(ln) == 0:
                break
            if ln.endswith('\xe2\x80\x90\x0a'):
                self.desc += ln[:len(ln) - 4]
            else:
                self.desc += ln.strip() + ' '
        self.desc = utils.web.htmlToText(self.desc, tagReplace='')
        self.desc = utils.web.normalizeWhitespace(self.desc)

    def parse(self, fd):
        """Parse the HTML manual page from the given file descriptor."""
        for x in range(43):
            fd.readline()
        self.__parseName(fd)
        self.__parseSynopsis(fd)
        self.__parseDesc(fd)

class UbuntuMan(callbacks.Plugin):
    """This plugin provides commands for displaying UNIX manual pages from
    the Ubuntu Manpage repository."""

    def __init__(self, irc):
        self.__parent = super(UbuntuMan, self)
        self.__parent.__init__(irc)
        self.conf = conf.supybot.plugins.UbuntuMan
        self.parser = UbuntuManParser()

    def __buildUrl(self, release, section, command):
        """Build URL to a manual page."""
        url = self.conf.baseurl.value + '/'
        if release:
            url += urllib.quote_plus(release) + '/'
        else:
            url += urllib.quote_plus(self.conf.release.value) + '/'
        url += 'man' + urllib.quote_plus(section) + '/'
        url += urllib.quote_plus(command) + '.html'
        return url

    def __tryUrl(self, url):
        """Try to open the given URL.  If succeeds, returns it's file
        descriptor; otherwise returns None."""
        try:
            return utils.web.getUrlFd(url)
        except utils.web.Error:
            return None

    def __getManPageFd(self, release, command):
        """Get a file descriptor to the manual page in the Ubuntu Manpage
        Repository."""
        for section in self.conf.sections.value:
            url = self.__buildUrl(release, section, command)
            fd = self.__tryUrl(url)
            if fd:
                return fd
        return None

    def __formatReply(self, name, synopsis, desc):
        """Format the data for the IRC reply."""
        msg = self.parser.name + ' | ' \
            + self.parser.synopsis + ' | ' \
            + self.parser.desc
        msg = msg[:conf.supybot.reply.mores.length.value + 1]
        idx = msg.rfind('.')
        return msg[:idx + 1]

    def man(self, irc, msg, args, command, optlist):
        """<command> [--rel <release>]

        Displays a manual page from the Ubuntu Manpage Repositor."""
        release = None
        for (opt, arg) in optlist:
            if opt == 'rel':
                release = arg
        try:
            fd = self.__getManPageFd(release, command)
            if not fd:
                irc.reply("No manual page for " + command)
                return
            self.parser.parse(fd)
            del fd
            msg = self.__formatReply(self.parser.name,
                                     self.parser.synopsis,
                                     self.parser.desc)
            irc.reply(msg)
        except UbuntuManError, e:
            irc.reply('Failed to parse the manpage: ' + e.message)

    def manurl(self, irc, msg, args, command, optlist):
        """<command> [--rel <release>]

        Gives the URL to the full manual page in the Ubuntu Manpage
        Repository."""
        release = None
        for (opt, arg) in optlist:
            if opt == 'rel':
                release = arg
        for section in self.conf.sections.value:
            try:
                url = self.__buildUrl(release, section, command)
                fd = self.__tryUrl(url)
                if fd:
                    irc.reply(url)
                    del fd
                    return
                del fd
            except utils.web.Error:
                pass
        irc.reply("No manual page for " + command)

    man = wrap(man, ['something', getopts({'rel': 'something'})])
    manurl = wrap(manurl, ['something', getopts({'rel': 'something'})])


Class = UbuntuMan


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
