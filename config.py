# Copyright (c) 2008 Henri Hakkinen
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

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    from supybot.questions import expect, anything, something, yn
    UbuntuMan = conf.registerPlugin('UbuntuMan', True)

    if advanced == False:
        return

    baseurl = something("""What value should be used for base URL?""",
                        default="http://manpages.ubuntu.com/manpages")

    release = expect("""What value should be used as the default Ubuntu release?""",
                     possibilities=['dapper', 'feisty', 'gutsy', 'hardy', 'intrepid'],
                     default='hardy')

    sections = something("""What manual page sections should be enabled?""",
                         default='1 5 8')

    language = expect("""Which language should be used by default?""",
                      possibilities=['en', 'es', 'de', 'fi'],
                      default='en')

    UbuntuMan.baseurl.setValue(baseurl)
    UbuntuMan.release.setValue(release)
    UbuntuMan.sections.setValue(sections)
    UbuntuMan.language.setValue(language)


UbuntuMan = conf.registerPlugin('UbuntuMan')

conf.registerGlobalValue(UbuntuMan, 'baseurl',
    registry.String('http://manpages.ubuntu.com/manpages',
             """Determines the base URL of the manpage repository.
                Do not end this variable to slash."""))

conf.registerGlobalValue(UbuntuMan, 'release',
    registry.String('hardy',
             """Determines the default release to fetch the manual pages for."""))

conf.registerGlobalValue(UbuntuMan, 'sections',
    registry.SpaceSeparatedListOfStrings(['1', '5', '8'],
             """Determines the list of enabled manual page sections."""))

conf.registerGlobalValue(UbuntuMan, 'language',
    registry.String('en',
             """Determines the default language. Currently supported: en, es, de, fi"""))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
