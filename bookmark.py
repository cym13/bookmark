#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2014 Cédric Picard
#
# LICENSE
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# END_OF_LICENSE
#
"""
Simple command line browser independant bookmark utility.

Usage: bookmark [options] [-r] URL TAG...
       bookmark [options]  -d  URL
       bookmark [options]  -l  [TAG]...
       bookmark [options]  -L  TAG...
       bookmark [options]  URL
       bookmark [options]  -t

Arguments:
    URL     The url to bookmark
            If alone, print the tags associated with URL
            If the url corresponds to an existing file,
            the absolute path is substituted to URL
            If URL is '-', then the program looks for a list of URL
            comming from the standard input.
    TAG     The tags to use with the url.

Options:
    -h, --help          Print this help and exit
    -r, --remove        Remove TAG from URL
    -d, --delete        Delete an url from the database
    -l, --list-any      List the urls with any of TAG
                        If no tag is given, list all urls
    -L, --list-every    List the urls with every of TAG
    -f, --file FILE     Use FILE as the database
                        Default is ~/.bookmarks
    -t, --tags          List every tag present in the database
    -n, --no-path-subs  Disable file path substitution
"""

import os
import yaml
from docopt import docopt

def add(database, url, tags):
    if url in database:
        for tag in tags:
            database[url].append(tag)
    else:
        database[url] = list(tags)


def remove(database, url, tags):
    try:
        for tag in tags:
            database[url].remove(tag)
    except ValueError:
        pass


def delete(database, url):
    try:
        database.pop(url)
    except KeyError:
        pass


def list_any(database, tags):
    for url in database:
        if set(tags).intersection(set(database[url])) != set() or tags == []:
            yield url


def list_every(database, tags):
    for url in database:
        if set(tags).issubset(set(database[url])):
            yield url


def list_every_tags(database):
    result = set()
    for each in database:
        result = result.union(set(database[each]))
    return result


def manage_url(url, tags, d_file, database, args):
    if url and os.path.exists(url) and not args["--no-path-subs"]:
        url = os.path.abspath(url)

    if args["--delete"]:
        delete(database, url)
        yaml.dump(database, open(d_file, 'w'))

    elif args["--list-any"]:
        result = list(list_any(database, tags))
        result.sort()

        for url in result:
            print(url)

    elif args["--list-every"]:
        result = list(list_every(database, tags))
        result.sort()

        for url in list_every(database, tags):
            print(url)

    elif args["--remove"]:
        remove(database, url, tags)
        yaml.dump(database, open(d_file, 'w'))

    elif args["--tags"]:
        result = list(list_every_tags(database))
        result.sort()
        for tag in result:
            print(tag)

    elif args["TAG"]:
        add(database, url, tags)
        yaml.dump(database, open(d_file, 'w'))

    else:
        for tag in database[url]:
            print(tag)


def main():
    args = docopt(__doc__)

    if args["URL"] == '-':
        urls = os.sys.stdin.read().splitlines()
    else:
        urls = [ args["URL"] ]

    d_file = args["--file"] or os.environ["HOME"] + "/.bookmarks"
    try:
        if not os.path.exists(d_file):
            print('The file "' + d_file + '" does not exists: creating it.',
                    file=os.sys.stderr)
            open(d_file, "a+").close()

        database = yaml.load(open(d_file)) or {}

    except PermissionError as e:
        os.sys.exit(e)

    tags = args["TAG"]
    for url in urls:
        manage_url(url, tags, d_file, database, args)


if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        print("No such bookmark:", e, file=os.sys.stderr)
        os.sys.exit(1)
