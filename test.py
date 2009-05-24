# -*- Encoding: UTF-8 -*-
# Copyright (c) 2009 Henri Häkkinen, Elián Hanisch.
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
        # test length limit
        m = self.getMsg('man grep')
        self.assertTrue(len(m.args[1]) <= 300)

    def testManurl(self):
        (base, rel, lang) = (UMConf.baseurl, UMConf.release, UMConf.language)
        url = '%s/%s/%s/man1/cat.1.html' % (base, rel, lang)
        self.assertResponse('manurl cat', url)
        url = '%s/%s/%s/man1/cp.1.html' % (base, 'dapper', 'es')
        self.assertResponse('manurl cp --rel dapper --lang es', url)
        self.assertRegexp('manurl asdasd', '^No manual page for')

    def testLanguages(self):
        for s in ('en', 'es', 'de', 'it', 'fr'):
            self.assertNotRegexp('man ls --lang %s' % s, '^Failed to parse')
            self.assertNotRegexp('man bash --lang %s' % s, '^Failed to parse')
        self.assertNotRegexp('man su --lang fi', '^Failed to parse')
        # this fails for now
        #self.assertNotRegexp('man aptitude --lang fi', '^Failed to parse')

    def testFormat(self):
        cmd = 'grep'
        confbak = conf.supybot.plugins.UbuntuMan.format()
        try:
            self.assertNotRegexp('man %s' % cmd, r'\$')
            conf.supybot.plugins.UbuntuMan.format.setValue('$command')
            self.assertResponse('man %s' % cmd, cmd)
            conf.supybot.plugins.UbuntuMan.format.setValue('$url')
            self.assertRegexp('man %s' % cmd,
                    r'^http://manpages\.ubuntu\.com/manpages/\w+/en/.+html')
            conf.supybot.plugins.UbuntuMan.format.setValue('$name')
            self.assertRegexp('man %s' % cmd, r'^%s.{10}' % cmd)
            conf.supybot.plugins.UbuntuMan.format.setValue('$synopsis')
            self.assertRegexp('man %s' % cmd, r'^%s \[OPTIONS\]' % cmd)
            conf.supybot.plugins.UbuntuMan.format.setValue('$description')
            self.assertRegexp('man %s' % cmd, r'^%s.{10}' % cmd)
            conf.supybot.plugins.UbuntuMan.format.setValue(
                   'prefix | $name | $url | $description | $synopsis | subfix')
            self.assertRegexp('man %s' % cmd, r'^prefix.*subfix$')
        finally:
            conf.supybot.plugins.UbuntuMan.format.setValue(confbak)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
