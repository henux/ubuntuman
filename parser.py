# -*- Encoding: UTF-8 -*-
# Copyright (c) 2009 Henri Häkkinen, Elián Hanisch.
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

class ManpageParser:
    """
    Manual page parser interface.

    Derived classes are expected to implement `parse(fd)` method to parse a
    manual page for a specific language from the given file descriptor. The
    manual page is given as a groff source and the returned value is expected
    to be a dictionary containing elements for each parsed data.

    Parser objects are 'one shot' only -- once the manual page is parsed, the
    parser is not used again and is thrown away.
    """
    pass

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
