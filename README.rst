Description
===========

Simple command line bookmark and/or tagging utility.

One way to see this program is to consider it a simple hashmap utility for
bash that associates a set of strings (the tags) to another one (the url).
Feel free to find other ways to use this program!

It is based on a sqlite database but supports input/output in json or msgpack
and can even serve a web page for better integration with the browser.

This script is written using python3.

THIS VERSION IS IN DEVELOPMENT.


Documentation
=============
::

   Simple command line browser independant bookmark utility

   Usage: bm add    URL TAG...
          bm list   [-f FMT] [-w] [-v] [TAG]...
          bm tags   [-f FMT] [-w] [URL]...
          bm remove URL TAG...
          bm delete URL...
          bm import [-f FMT] FILE...

   Commands:
       add           Tag a URL
       list          List URLs matching some tags
                     If TAG is empty, outputs all urls
       tags          List tags associated to URLs
                     If URLs is empty, outputs all tags with statistics
       remove        Remove TAGs from URLs
       delete        Remove URLs from the database
       import        Import URLs into the database

   Arguments:
       URL     An URL or path; if '-', looks for a list of URLs on stdin
       TAG     A tag
       FILE    Path to a file for import
       GROUP   A set of tags; Using a group sets all the tags within that group

   Options:
       -h, --help          Print this help and exit
       --version           Print current version number and exit
       -d, --database DB   Path to the database to use
       -f, --format FMT    Input/Output format: text, json, msgpack, web
       -v, --verbose       Display tags alongside the URL while listing

   Conventions:
       bm supports the use of sets of tags.
       Anything starting with the symbol + will be understood as a tag set.
       If used instead of a URL it will add tags to the set.
       If used instead of a tag it will act as if all tags in the set were listed.

Example
=======

::

    $ bm add "http://duckduckgo.com" bad search engine

    $ bm add "http://google.com" bad search engine

    $ bm add "http://python.org" python official

    $ bm list search engine
    http://duckduckgo.com
    http://google.com

    $ bm remove "http://duckduckgo.com" bad

    $ bm add "http://duckduckgo.com" cool

    $ bm tags "http://duckduckgo.com"
    cool
    engine
    search

    $ bm list search engine
    http://duckduckgo.com
    http://google.com

    $ bm list bad search engine
    http://google.com

    $ bm list
    http://duckduckgo.com
    http://google.com
    http://python.org

    $ bm tags
    cool
    engine
    search
    bad
    python
    official

    # Add all tags from a url to another
    $ bm tags http://duckduckgo.com | xargs bm add http://google.com

    # Add tags to a set of urls
    $ bm list search engine | xargs -I{} bm add {} website find data


And you, how do you use it?
===========================

As many cli tools, bm is designed the Unix way: with composability in mind.
This is why its output is mainly plain text, one entry per line with simple
separators.

I use urxvt and the urxvt-perls that allow fast link openning from the
terminal.

My main browser is qutebrowser but I had bm linked with dwb or firefox
before. To do that I keep in my configuration two keybindings that execute
external commands:

::

    set-cmd-text -s :spawn -- bm add '{url}'
        b
    set-cmd-text -s :spawn -- bm list -v -f web
        B

That way, when on a page, I press b to bookmark the current url and just type
the tags on the browser prompt. B is for searching, note how it uses the html
display with -f web to open the results in a new tab.

For synchronisation I relie on a script that scp's the bookmark file between
my computers and then does a local file import.

These are only some personal examples, I hope you'll find yours!


Dependencies
============

Required
--------

docopt   https://github.com/docopt/docopt or "pip install docopt"

Optional
--------

msgpack  http://msgpack.org/ or "pip install msgpack-python"

License
=======

This program is under the GPLv3 License.

You should have received a copy of the GNU General Public License
along with this program. If not, see http://www.gnu.org/licenses/.

Contact
=======

::

    Main developper: Cédric Picard
    Email:           cpicard@purrfect.fr
