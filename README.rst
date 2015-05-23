Description
===========

Simple command line bookmark and/or tagging utility.

In order to help using it to tag files and directories as well as urls, it
recognises if the URL given is that of an existing file. If so, the absolute
path is substituted to help scripting by piping the output and to escape
ambiguity. This behaviour can be stopped by using the "--no-path-subs" option.

One way to see this program is to consider it a simple hashmap utility for
bash that associates a set of strings (the tags) to another one (the url).
Feel free to find other ways to use this program!

Msgpack is used as is it highly portable, language agnostic and yet highly
efficient.

This script is written using python3.


THIS VERSION IS STABLE.


Documentation
=============
::

    Usage: bm [options] [-r] URL TAG...
           bm [options]  -d  URL
           bm [options]  -l  [TAG]...
           bm [options]  -L  TAG...
           bm [options]  URL
           bm [options]  -i  SOURCE...
           bm [options]  -t

    Arguments:
        URL     The url to bookmark
                If alone, print the tags associated with URL
                If the url corresponds to an existing file,
                the absolute path is substituted to URL
                If URL is '-', then the program looks for a list of URL
                comming from the standard input.
        TAG     The tags to use with the url.
        SOURCE  When uniting, the paths to the source files.

    Options:
        -h, --help          Print this help and exit
        -r, --remove        Remove TAG from URL
        -d, --delete        Delete an url from the database
        -l, --list-every    List the urls with every of TAG
                            If no tag is given, list all urls
        -L, --list-any      List the urls with any of TAG
        -f, --file FILE     Use FILE as the database, can be an url
                            Default is ~/.bookmarks
        -t, --tags          List every tag present in the database
                            with how many times it is used.
                            Output is sorted from the least to the most used
        -i, --import        Import bookmarks from sources into the database.
        -n, --no-path-subs  Disable file path substitution
        -v, --verbose       Displays the list of tags of each url when listing
        -w, --web           Open the results in a web browser
        --version           Print current version number

Example
=======

::

    $ bm "http://duckduckgo.com" bad search engine

    $ bm "http://google.com" bad search engine

    $ bm -l search engine
    http://duckduckgo.com
    http://google.com

    $ bm -r "http://duckduckgo.com" bad

    $ bm "http://duckduckgo.com" cool

    $ bm "http://duckduckgo.com"
    cool
    engine
    search

    $ bm -L search engine
    http://duckduckgo.com
    http://google.com

    $ bm -L bad search engine
    http://google.com

    $ bm -l
    cool
    engine
    search
    bad

    $ cat urls | bm - atag


Installation
============

The simplest method is to use:

::

    pip install bm

Otherwise, you can do when in this directory

::

    python3 setup install

This should install the dependancies as well.

An AUR package is available for archlinux as well:

::

    yaourt -S bm


And you, how do you use it?
===========================

As many cli tools, bm is thought the Unix way: with composability in mind.
This is why it's output is mainly plain text, one entry per line with simple
separators.

I use urxvt and the urxvt-perls that allow fast link openning from the
terminal.

My main browser is qutebrowser but I had bm linked with dwb or firefox
before. To do that I keep in my configuration two keybindings that execute
external commands:

::

    set-cmd-text -s :spawn -- bm '{url}'
        b
    set-cmd-text -s :spawn -- bm -w -v -l
        B

That way, when on a page, I press b to bookmark the current url and just type
the tags on the browser prompt. B is for searching, note how it uses the html
display with -w to open the results in a new tab.

For synchronisation I relay on a script that scp's the bookmark file between
my computers and then does a local file import.

As I work on some very big projects, I also use bm to bookmark paths and
files so that I can quickly find an given set of files. To do that I have an
alias in order not to mix this work and other urls.

::

    alias fbm="bm -f ~/.path_bm"

As bm automatically expands relative paths it is well suited to this usage.

These are only some personal examples, I hope you'll find yours!


Dependencies
============

docopt   https://github.com/docopt/docopt or "pip install docopt"

msgpack  http://msgpack.org/ or "pip install msgpack-python"

requests https://github.com/kennethreitz/requests or "pip install requests"

License
=======

This program is under the GPLv3 License.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Contact
=======

::

    Main developper: Cédric Picard
    Email:           cedric.picard@efrei.net
    Twitter:         @Cym13
    GPG:             383A 76B9 D68D 2BD6 9D2B  4716 E3B9 F4FE 5CED 42CB
