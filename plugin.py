# -*- Encoding: UTF-8 -*-
# Copyright (c) 2008 Henri Häkkinen
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
import sys

class UbuntuManError(Exception):
    """Ubuntu manual page exception.  Raised when an expected section is
    not found from the manual page or other parsing related error is
    encountered."""
    pass

class UbuntuManParser:
    """Ubunutu manual page parser."""

    def skipToSection(self, fd, section):
        """Skips lines until '<h3>SECTION</h3>' is found and returns the
        rest of the line as a string with whitespaces normalized and HTML
        tags removed.  'section' can be a string or a tuple of strings."""
        if section.__class__ == str: # check if section is a string
            section = (section, )
        while True:
            ln = fd.readline()
            if not ln:
                raise UbuntuManError('Section %s not found.' % \
                        ', '.join(section))
            for s in section:
                tag = '<h3>%s</h3>' % s
                idx = ln.find(tag)
                if idx > -1:
                    ln = ln[idx + len(tag) + 5:]
                    ln = utils.web.htmlToText(ln, tagReplace='')
                    ln = utils.str.normalizeWhitespace(ln)
                    return ln

    def parseName(self, fd, section='NAME'):
        """Parse the NAME section."""
        self.name = self.skipToSection(fd, section)

    def parseSynopsis(self, fd, section='SYNOPSIS'):
        """Parse the SYNOPSIS section.  Only the first line is read."""
        self.synopsis = self.skipToSection(fd, section)

    def parseDesc(self, fd, section='DESCRIPTION'):
        """Parse the DESCRIPTION section.  Only the first paragraph is
        read."""
        self.desc = self.skipToSection(fd, section)
        while True:
            ln = fd.readline()
            if not ln or ln.startswith(' </pre>') or len(ln) == 0:
                break
            if ln.endswith('\xe2\x80\x90\x0a'):
                self.desc += ln[:len(ln) - 4]
            else:
                self.desc += ln.strip() + ' '
        self.desc = utils.web.htmlToText(self.desc, tagReplace='')
        self.desc = utils.web.normalizeWhitespace(self.desc)

    def parse(self, fd, command):
        """Parse the HTML manual page from the given file descriptor."""
        self.command = command
        for x in range(43):
            fd.readline()
        self.parseName(fd)
        self.parseSynopsis(fd)
        self.parseDesc(fd)

class UbuntuManParser_en(UbuntuManParser):
    """Ubuntu manual page parser for English."""
    pass

class UbuntuManParser_es(UbuntuManParser):
    """Ubuntu manual page parser for Spanish."""

    def parseName(self, fd):
        UbuntuManParser.parseName(self,fd, ('NOMBRE', 'NAME'))

    def parseSynopsis(self, fd):
        UbuntuManParser.parseSynopsis(self, fd, ('SINOPSIS', 'SINTAXIS',
            'SYNOPSIS'))

    def parseDesc(self, fd):
        # Should be just DESCRIPCIÓN, but meh :/
        UbuntuManParser.parseDesc(self, fd,
                                  ('DESCRIPCI   N',
                                   'DESCRIPCI?N',
                                   'DESCRIPCION',
                                   'DESCRIPTION',
                                   'DESCRIPCIÓN'))

class UbuntuManParser_de(UbuntuManParser):
    """Ubunutu manual page parser for German."""

    def parseName(self, fd):
        UbuntuManParser.parseName(self, fd, ('BEZEICHNUNG', 'NAME'))

    def parseSynopsis(self, fd):
        # German synopsis sections aren't formated right, taking that into
        # account..
        section = 'BERSICHT'
        while True:
            ln = fd.readline()
            if not ln:
                raise UbuntuManError('Section %s not found.' % section)
            tag = section
            offs = ln.find(tag)
            if offs == -1:
                continue
            ln = fd.readline()
            ln = utils.web.htmlToText(ln, tagReplace='')
            ln = utils.str.normalizeWhitespace(ln)
            break
        self.synopsis = ln

    def parseDesc(self, fd):
        UbuntuManParser.parseDesc(self, fd, section='BESCHREIBUNG')

class UbuntuManParser_fi(UbuntuManParser):
    """Ubuntu manual page parser for Finnish."""

    def parseName(self, fd):
        UbuntuManParser.parseName(self, fd, ('NAME', 'NIMI'))

    def parseSynopsis(self, fd):
        UbuntuManParser.parseSynopsis(self, fd, ('SYNOPSIS', 'YLEISKATSAUS'))

    def parseDesc(self, fd):
        UbuntuManParser.parseDesc(self, fd, 'KUVAUS')

class UbuntuMan(callbacks.Plugin):
    """This plugin provides commands for displaying UNIX manual pages from
    the Ubuntu Manpage repository."""

    def __init__(self, irc):
        self.__parent = super(UbuntuMan, self)
        self.__parent.__init__(irc)
        self.currentParser = None

    def __setParser(self, language):
        parserClass  = 'UbuntuManParser_' + language
        if parserClass == self.currentParser:
            # Don't initialise the parser again if it isn't needed.
            return
        module = sys.modules['UbuntuMan.plugin']
        # Looks for the parser class that matchs the language set in the
        # config, or defaults to UbuntuManParser_en.
        self.parser = hasattr(module , parserClass) \
            and getattr(module,parserClass)() \
            or UbuntuManParser_en()
        self.currentParser = parserClass

    def __buildUrl(self, release, section, command, language):
        """Build URL to a manual page."""
        if not release:
            release = self.registryValue('release')
        url = '/%s/%s/man%s/%s.%s.html' % (release, language, section,
                    command, section)
        url = self.registryValue('baseurl') + utils.web.urlquote(url)
        return url

    def __tryUrl(self, url):
        """Try to open the given URL.  If succeeds, returns it's file
        descriptor; otherwise returns None."""
        try:
            return utils.web.getUrlFd(url)
        except utils.web.Error:
            return None

    def __getManPageFd(self, release, command, language):
        """Get a file descriptor to the manual page in the Ubuntu Manpage
        Repository."""
        if language == 'en':
            language = (language, )
        else:
            language = (language, 'en')
        for section in self.registryValue('sections'):
            for lang in language:
                url = self.__buildUrl(release, section, command, lang)
                self.log.debug('UbuntuMan: Trying url %s' % url)
                fd = self.__tryUrl(url)
                if fd:
                    self.log.debug('UbuntuMan: Success')
                    self.__setParser(lang)
                    return fd
        return None

    def __formatReply(self):
        """Format the data for the IRC reply."""
        msg = '%s | %s | %s' % (self.parser.name, self.parser.synopsis,
                self.parser.desc)
        length = conf.supybot.reply.mores.length()
        if not length:
            length = 300
        msg = msg[:length + 1]
        idx = msg.rfind('.')
        if idx < 1:
            return msg[:idx - 3] + '...'
        else:
            return msg[:idx + 1]

    def man(self, irc, msg, args, command, optlist):
        """<command> [--rel <release>] [--lang <language>]

        Displays a manual page from the Ubuntu Manpage Repository."""
        release = None
        language = self.registryValue('language')
        for (opt, arg) in optlist:
            if opt == 'rel':
                release = arg
            elif opt == 'lang':
                language = arg
        try:
            fd = self.__getManPageFd(release, command, language)
            if not fd:
                irc.reply('No manual page for \'%s\'' % command)
                return
            self.parser.parse(fd, command)
            fd.close()
            msg = self.__formatReply()
            irc.reply(msg)
        except UbuntuManError, e:
            irc.reply('Failed to parse the manpage for \'%s\': %s' % (command, e.message))

    def manurl(self, irc, msg, args, command, optlist):
        """<command> [--rel <release>] [--lang <language>]

        Gives the URL to the full manual page in the Ubuntu Manpage
        Repository."""
        release = None
        language = self.registryValue('language')
        for (opt, arg) in optlist:
            if opt == 'rel':
                release = arg
            elif opt == 'lang':
                language = arg
        try:
            fd = self.__getManPageFd(release, command, language)
            if not fd:
                irc.reply('No manual page for \'%s\'' % command)
                return
            irc.reply(fd.url)
            fd.close()
        except:
            pass

    man = wrap(man, ['something', getopts({'rel': 'something',
                                           'lang' : 'something'})])
    manurl = wrap(manurl, ['something', getopts({'rel': 'something',
                                                 'lang' : 'something'})])


Class = UbuntuMan


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
