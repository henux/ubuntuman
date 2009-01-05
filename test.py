# -*- Encoding: UTF-8 -*-
# Copyright (c) 2008 Henri Häkkinen
#
# This file is part of the UbuntuMan Supybot IRC plugin.
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

from supybot.test import *

UbuntuMan = plugin.loadPluginModule('UbuntuMan')
UMConf = conf.supybot.plugins.UbuntuMan

class UbuntuManTestCase(PluginTestCase):
    plugins = ('UbuntuMan',)

    def testMan(self):
        self.assertRegexp('man grep', '^grep.*\|')
        self.assertRegexp('man ls', '^ls.*\|')
        self.assertRegexp('man asdasd', '^No manual page for')

    def testManurl(self):
        (base, rel, lang) = (UMConf.baseurl, UMConf.release, UMConf.language)
        url = '%s/%s/%s/man1/cat.1.html' % (base, rel, lang)
        self.assertResponse('manurl cat', url)

    def testLanguages(self):
        for s in ('en','es','de'):
            self.assertNotRegexp('man ls --lang %s' % s, '^Failed to parse')
        self.assertNotRegexp('man su --lang fi', '^Failed to parse')


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
