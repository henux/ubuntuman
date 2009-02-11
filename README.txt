UbuntuMan README

Copyright (C) 2008 Henri Häkkinen

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.


To download the latest version of this software, please visit:

    http://henux.nor.fi/coding/projects/9-other/7-ubuntuman
    http://github.com/henux/ubuntuman/tree/master


INTRODUCTION

UbuntuMan is a Supybot plugin for browsing online manual pages from the
Ubuntu Manpage Repository (http://manpages.ubuntu.com) in an IRC channel.

The plugin arose from a need to have a fancy manual page browser in
##club-ubuntu IRC channel at irc.freenode.net server.  Several versions of
the plugin was made by the same author, until the Ubuntu Manpage Repository
was decided on.

Thanks to emma and bascule for their continued support and several others
in ##club-ubuntu for bug testing.  Also thanks to Terence Simpson for his
contribution and to Elián Hanisch for non-English manual page support.


USAGE

The plugin provides the following new Supybot commands:

man <command> [--rel <release>] [--lang <language>]

    Prints a short version of the manual page from the Ubuntu Manpage
    Repository. The format is defined in UbuntuMan.format configuration
    variable.

manurl <command> [--rel <release>] [--lang <language>]

    Gives the URL of the full manual page in the Ubuntu Manpage Repository.

Commands accept --rel and --lang options, which can be used to override the
default Ubuntu release and language the manual pages are fetched for.  For
example, to see the Spanish manual page for the 'ls' command as it exists
in Ubuntu Hardy , use "man ls --rel hardy --lang es".  If these options are
not given, the configured defaults are used.


CONFIGURATION VARIABLES

supybot.plugins.UbuntuMan.baseurl

    The base URL to the Canonical's Ubuntu Manpage Repository.  In all
    normal cases, the default value should be used.  This variable should
    never end in slash!
    Default value: http://manpages.ubuntu.com/manpages

supybot.plugins.UbuntuMan.release

    The default release to fetch the manual pages for.  This should be one
    of the following: dapper, gutsy, hardy, intrepid, jaunty.
    Default value: intrepid

supybot.plugins.UbuntuMan.sections

    Space separated list of enabled sections.  Note this variable has a
    different syntax than in the version 1.0.
    Default value: 1 5 8

supybot.plugins.UbuntuMan.language

    The default language used to fetch the manual pages for.  This should
    be one of the following: de, en, es, fi, fr, it.
    Default value: en

supybot.plugins.UbuntuMan.format

    The format of the 'man' command. This should be a string containing any
    of the following keywords:
    $name - manpage NAME section.
    $synopsis - manpage SYNOPSIS section.
    $description - manpage DESCRIPTION section.
    $command - the name of the command.
    $url - the url address where the manpage is located.
    Default value:
    $name | $synopsis | $description

supybot.plugins.UbuntuMan.maxLength

    Maximun number of characters the 'man' command can use. If the output
    excess this value one of the manpage sections (normally DESCRIPTION) is
    cut for fit the limit, if still is too long then the whole reply is cut.
    Note that supybot.reply.mores.length takes priority over this variable if
    its value is other than zero.
    Default value: 300

