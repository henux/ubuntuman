# Copyright (c) 2008 Henri Hakkinen
#

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.registry as registry
import supybot.conf as conf
import urllib

subsections = {'en': ('NAME', 'SYNOPSIS', 'DESCRIPTION'),
               'fr': ('NOM', 'SYNOPSIS', 'DESCRIPTION'),
               'nl': ('NAAM', 'OVERZICHT', 'BESCHRIJVING'),
               'fi': ('NIMI', 'YLEISKATSAUS', 'KUVAUS'),
               'sv': ('NAMN', 'SYNOPSIS', 'BESKRIVNING'),
               #'es': ('NOMBRE', 'SINOPSIS', 'DESCRIPCI   N')
               }

class UbuntuManError(Exception):
    """Exception class for UbuntuManParser."""
    pass

class UbuntuManParser:
    """Class for parsing the manpage out of the HTML page markup received
    from the Ubuntu Manpage Repository."""

    def __findSectionData(self, html, sect):
        """Return everything between '<h3>SECTION</h3><pre>' and '</pre>
        tags.""" 
        s = html.find('<h3>' + sect + '</h3><pre>')
        if s == -1:
            raise UbuntuManError('<h3>' + sect + '</h3><pre> not found')
        s += len(sect) + 14
        e = html.find('</pre>', s)
        if e == -1:
            raise UbuntuManError('</pre> not found while parsing ' + sect)
        return html[s:e]

    def __parseName(self, html, sect):
        """Parse the NAME section."""
        data = self.__findSectionData(html, sect)
        self.name = utils.str.normalizeWhitespace(data)

    def __parseSynopsis(self, html, sect):
        """Parse the SYNOPSIS section.  Only the first line is read."""
        data = self.__findSectionData(html, sect)
        data = data[:data.find('\n')]
        data = utils.web.htmlToText(data, tagReplace='')
        self.synopsis = utils.str.normalizeWhitespace(data)

    def __parseDescription(self, html, sect):
        """Parse the DESCRIPTION section.  Only the first paragraph is
        read."""
        data = self.__findSectionData(html, sect)
        data = data[:html.find('\n\n')]
        data = utils.web.htmlToText(data, tagReplace='')
        self.desc = utils.str.normalizeWhitespace(data)

    def parse(self, html, lang):
        """Parse the manpage from the HTML markup.  Results are stored into
        variables 'name', 'synopsis' and 'desc'.  In the case of an error,
        raises UbuntuManError."""
        self.name     = ''
        self.synopsis = ''
        self.desc     = ''
        self.__parseName(html, subsections[lang][0])
        self.__parseSynopsis(html, subsections[lang][1])
        self.__parseDescription(html, subsections[lang][2])

class UbuntuMan(callbacks.Plugin):
    """This plugin provides commands for displaying UNIX manual pages from
    the Ubuntu Manpage repository."""

    def __init__(self, irc):
        self.__parent = super(UbuntuMan, self)
        self.__parent.__init__(irc)
        self.conf = conf.supybot.plugins.UbuntuMan
        self.parser = UbuntuManParser()

    def __buildUrl(self, release, language, section, command):
        """Build a manual page URL."""
        url = self.conf.baseurl.value + '/'
        if release:
            url += urllib.quote_plus(release) + '/'
        else:
            url += urllib.quote_plus(self.conf.release.value) + '/'
        url += urllib.quote_plus(language) + '/'
        url += urllib.quote_plus(section) + '/'
        url += urllib.quote_plus(command) + '.html'
        return url

    def __tryUrl(self, url):
        """Try to open the given URL. If succeeds, returns it's HTML
        source; otherwise returns None."""
        try:
            return utils.web.getUrl(url)
        except utils.web.Error:
            return None

    def __getManPageSource(self, release, language, command):
        """Get the manual pages HTML source."""
        for section in self.conf.sections.value:
            url = self.__buildUrl(release, language, section, command)
            html = self.__tryUrl(url)
            if html:
                return html
        return None

    def __formatMessage(self, lang, name, synopsis, desc):
        msg = self.parser.name \
            + ' // ' + subsections[lang][1] + ': ' + self.parser.synopsis \
            + ' // ' + subsections[lang][2] + ': ' + self.parser.desc
        msg = msg[:conf.supybot.reply.mores.length.value + 1]
        idx = msg.rfind('.')
        return msg[:idx + 1]

    def man(self, irc, msg, args, command, language, release):
        """<command> [<language>] [<release>]

        Displays a UNIX manual page."""
        if language == None:
            language = self.conf.language.value
        elif not language in subsections:
            irc.reply('Language not supported or recognized')
            return
        try:
            html = self.__getManPageSource(release, language, command)
            if html == None:
                irc.reply("No manual page for " + command)
                return
            self.parser.parse(html, language)
            msg = self.__formatMessage(language,
                                       self.parser.name,
                                       self.parser.synopsis,
                                       self.parser.desc)
            irc.reply(msg)
        except UbuntuManError, e:
            irc.reply('Failed to parse the manpage: ' + e.message)

    def manurl(self, irc, msg, args, command, language, release):
        """command [<language>] [<release>]

        Displays the URL where the 'man' command would fetch the manpage
        from."""
        if language == None:
            language = self.conf.language.value
        elif not language in subsections:
            irc.reply('Language not supported or recognized')
            return
        for section in self.conf.sections.value:
            try:
                url = self.__buildUrl(release, language, section, command)
                fd = utils.web.getUrlFd(url)
                irc.reply(url)
                del fd
                return
            except utils.web.Error:
                pass
        irc.reply("No manual page for " + command)

    man = wrap(man, ['something', optional('something'), optional('something')])
    manurl = wrap(manurl, ['something', optional('something'), optional('something')])


Class = UbuntuMan


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
