# Copyright (C) 2008 Henri Hakkinen
#

###

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    UbuntuMan = conf.registerPlugin('UbuntuMan', True)

    if advanced == False:
        return

    print "UbuntuMan uses the following formula for constructing a manual"
    print "page URL:"
    print "  baseurl '/' release '/' section '/' page '.html'"
    print

    print "The 'baseurl' should usually be set to http://manpages.ubuntu.com/manpages."
    print "This is the root of the Canonical's Ubuntu Manpages Repository."
    print
    baseurl = something("""What value should be used for baseurl?""",
                        default="http://manpages.ubuntu.com/manpages")

    print "The 'release' determines the Ubuntu Linux release the manpage is fetched"
    print "for.  You can specify here a default value which is used when no release is"
    print "given in the command line."
    print
    release = expect("""What value should be used for the default release?""",
                     possibilities=['dapper', 'feisty', 'gutsy', 'hardy', 'intrepid'],
                     default='hardy')

    print "The 'section' determines the man section used to look for the page."
    print "You can give here a space separated list of enabled sections."
    print
    sections = something("""What manual page sections should be used?""",
                         default='man1 man5 man8')

    UbuntuMan.baseurl.setValue(baseurl)
    UbuntuMan.release.setValue(release)
    UbuntuMan.sections.setValue(sections)


UbuntuMan = conf.registerPlugin('UbuntuMan')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(UbuntuMan, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))

conf.registerGlobalValue(UbuntuMan, 'baseurl',
    registry.String('http://manpages.ubuntu.com/manpages',
             """Determines the base URL of the manpage repository.
                Do not end this value with '/'."""))

conf.registerGlobalValue(UbuntuMan, 'release',
    registry.String('hardy',
             """Determines the default release for fetching the manpage for."""))

conf.registerGlobalValue(UbuntuMan, 'language',
    registry.String('en',
             """Determines the default language for fetching the manpage for."""))

conf.registerGlobalValue(UbuntuMan, 'sections',
    registry.SpaceSeparatedListOfStrings(['man1', 'man5', 'man8'],
             """Determines the list of enabled manual page sections."""))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
