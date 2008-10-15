UbuntuMan is a Supybot plugin for browsing online manual pages from the
Ubuntu Manpage Repository (http://manpages.ubuntu.com).  It provides two
commands:

man <page> [<release>]

    Displays a UNIX manual page for the given Ubuntu release.  Possible
    values for release are: dapper, feisty, gutsy, hardy and intrepid.  If
    release is not given, uses the configured default value.

manurl <page> [<release>]

    Displays the URL where man command would fetch the manual page from.
    Values for release are the same as for man.


The behaviour of UbuntuMan may be configured throught the following
configuration variables:

supybot.plugins.UbuntuMan.baseurl

    The base URL where manual pages are fetched from.  In all normal cases
    this should be set to `http://manpages.ubuntu.com/manpages' which is
    the root of the Canonical's Ubuntu Manpage Repository.

supybot.plugins.UbuntuMan.release

    The default release to fetch the manual pages for.  This value is used
    when one is not given in the command line of man or manurl.

supybot.plugins.UbuntuMan.sections

    Space separated list of section names used to look for manual pages.
    Each string in this is list is used sequentially when a manual page for
    some command is looked for.


The formula used for constructing an URL for a specific manual page is the
following:

  baseurl `/' release `/' section `/' the page given in the command `.html'
