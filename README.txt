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
contribution.


USAGE

The plugin provides the following new Supybot commands:

man <command> [--rel <release>]

    Prints a short version of the manual page from the Ubuntu Manpage
    Repository.

manurl <command> [--rel <release>]

    Gives the URL of the full manual page in the Ubuntu Manpage Repository.

Commands accept --rel option, which can be used to override the default
Ubuntu release the manual pages are fetched for.  For example, to see
manual page for the 'ls' command as it exists in Ubuntu Intrepid , use "man
ls --rel intrepid".  If the option is not given, the configured default is
used.


CONFIGURATION VARIABLES

supybot.plugins.UbuntuMan.baseurl

    The base URL to the Canonical's Ubuntu Manpage Repository.  In all
    normal cases, the default value should be used.  This variable should
    never end in slash!
    Default value: http://manpages.ubuntu.com/manpages

supybot.plugins.UbuntuMan.release

    The default release to fetch the manual pages for.  This should be one
    of the following: dapper, feisty, gutsy, hardy, intrepid.
    Default value: hardy

supybot.plugins.UbuntuMan.sections

    Space separated list of enabled sections.  Note this variable has a
    different syntax than in the version 1.0.
    Default value: 1 6 8
