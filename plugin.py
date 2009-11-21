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

import supybot.log as log
import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks

import sys

class UbuntuManError(Exception):
    """Ubuntu manual page exception.  Raised when an expected section is
    not found from the manual page or other parsing related error is
    encountered."""
    pass

def cut(s, limit):
    """Function for cutting a string nicely at the end of a word."""
    idx = s[:limit - 3].rfind(' ')
    s = '%s ...' % s[:idx]
    return s

class KeywordsParser:
    """Class for check which sections of the manpage are needed."""
    def __init__(self):
        self.keys = ('description', 'name', 'synopsis')
        self.reset()

    def reset(self):
        self.keysParsed = list()
        for key in self.keys:
            setattr(self, key, False)

    def checkKeywords(self, format):
        L = list()
        for key in self.keys:
            if ('$' + key) in format:
                setattr(self, key, True)
                L.append(key)
            else:
                setattr(self, key, False)
        self.keysParsed = L


class UbuntuManParser:
    """Ubunutu manual page parser."""

    def __init__(self):
        self.keywords = KeywordsParser()
        for key in self.keywords.keys:
            setattr(self, key, '')

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
                tag = '<h4><b>%s</b></h4>' % s
                idx = ln.find(tag)
                if idx > -1:
                    ln = fd.readline()
                    ln = utils.web.htmlToText(ln, tagReplace='')
                    ln = utils.str.normalizeWhitespace(ln)
                    return ln

    def parseName(self, fd, section='NAME'):
        """Parse the NAME section."""
        #log.debug('UbuntuManParser.parseName() parsing ...')
        self.name = self.skipToSection(fd, section).split()[0]

    def parseSynopsis(self, fd, section='SYNOPSIS'):
        """Parse the SYNOPSIS section.  Only the first line is read."""
        #log.debug('UbuntuManParser.parseSynopsis() parsing ...')
        self.synopsis = self.skipToSection(fd, section)

    def parseDesc(self, fd, section='DESCRIPTION'):
        """Parse the DESCRIPTION section.  Only the first sentences that fit a
        150 char limit are read."""
        #log.debug('UbuntuManParser.parseDesc() parsing ...')
        description = self.skipToSection(fd, section)
        while len(description) < 300:
            ln = fd.readline()
            if not ln or ln.startswith(' </pre>') or len(ln) == 0:
                break
            if ln.endswith('\xe2\x80\x90\x0a'):
                description += ln[:len(ln) - 4]
            else:
                description = '%s%s ' %(description, ln.strip())
        description = utils.web.htmlToText(description, tagReplace='')
        description = utils.web.normalizeWhitespace(description)
        idx = description[:150].rfind('.')
        if idx < 1:
            description = cut(description, 150)
        else:
            description = description[:idx + 1]
        self.description = description

    def parse(self, fd, command, format):
        """Parse the HTML manual page from the given file descriptor."""
        self.command = command
        self.keywords.checkKeywords(format)
        for x in range(43):
            fd.readline()
        self.keywords.name and self.parseName(fd)
        self.keywords.synopsis and self.parseSynopsis(fd)
        self.keywords.description and self.parseDesc(fd)

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
        # FIXME aptitude manpage fails
        UbuntuManParser.parseSynopsis(self, fd, ('SYNOPSIS', 'YLEISKATSAUS'))

    def parseDesc(self, fd):
        UbuntuManParser.parseDesc(self, fd, 'KUVAUS')

class UbuntuManParser_it(UbuntuManParser):
    """Ubuntu manual page parser for Italian."""

    def parseName(self, fd):
        UbuntuManParser.parseName(self, fd, ('NOME', 'NAME'))

    def parseSynopsis(self, fd):
        UbuntuManParser.parseSynopsis(self, fd, ('SINTASSI', 'SYNOPSIS'))

    def parseDesc(self, fd):
        UbuntuManParser.parseDesc(self, fd, ('DESCRIZIONE', 'DESCRIPTION'))


class UbuntuManParser_fr(UbuntuManParser):
    """Ubuntu manual page parser for French."""

    def parseName(self, fd):
        UbuntuManParser.parseName(self, fd, ('NOM', 'NAME'))


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
        if "UbuntuMan.plugin" in sys.modules:
            module = sys.modules["UbuntuMan.plugin"]
        else:
            module = sys.modules['ubuntuman.plugin']
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
                #self.log.debug('UbuntuMan: Trying url %s' % url)
                fd = self.__tryUrl(url)
                if fd:
                    #self.log.debug('UbuntuMan: Success')
                    self.__setParser(lang)
                    self.parser.url = url
                    self.parser.command = command
                    return fd
        return None

    def __formatReply(self):
        """Format the data for the IRC reply."""
        format = self.registryValue('format')
        vars = {
                'url':self.parser.url,
                'command':self.parser.command,
                'name':self.parser.name,
                'synopsis':self.parser.synopsis,
                'description':self.parser.description,
               }
        replace = lambda : utils.str.perlVariableSubstitute(vars, format)
        msg = replace()
        length = conf.supybot.reply.mores.length()
        if not length:
            length = self.registryValue('maxLength')
        if len(msg) > length:
            # if we exceed in length lest try to cut one of the vars
            # without ruining the format.
            for var in self.parser.keywords.keysParsed:
                cutLength = len(msg) - length
                vars[var] = cut(vars[var], - cutLength)
                msg = replace()
                break
            if len(msg) > length:
                # alright, length is really just too short
                msg = '%s ...' %(msg[:length - 4])
        return msg

    def man(self, irc, msg, args, command, optlist):
        """<command> [--rel <release>] [--lang <language>]

        Displays a manual page from the Ubuntu Manpage Repository."""
        release = None
        language = self.registryValue('language')
        format = self.registryValue('format')
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
            self.parser.parse(fd, command, format)
            #for var in self.parser.keywords.keysParsed:
            #    log.debug('UbuntuMan.man() %s=\'%s\'' % (var,
            #        getattr(self.parser, var)))
            fd.close()
            msg = self.__formatReply()
            irc.reply(msg)
        except UbuntuManError, e:
            irc.reply('Failed to parse the manpage for \'%s\': %s' % (command,
                e.message))
            self.log.info(
                'plugins.UbuntuMan: Failed to parse the manpage in \'%s\'. ' \
                'Report it to the plugin maintainer.' % self.parser.url)

    man = wrap(man, ['something', getopts({'rel':'something',
                                           'lang':'something'})])

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

    manurl = wrap(manurl, ['something', getopts({'rel':'something',
                                                 'lang':'something'})])


Class = UbuntuMan


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
