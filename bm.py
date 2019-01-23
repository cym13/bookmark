#!/usr/bin/env python3

"""
Simple command line browser independant bookmark utility

Usage: bm add    URL TAG...
       bm list   [-f FMT] [-w] [-v] [TAG]...
       bm remove URL TAG...
       bm delete URL...
       bm import [-f FMT] FILE...
       bm tags   [-f FMT] [-w]

Commands:
    add           Tag a URL
    list          List URLs matching some tags
    remove        Remove TAGs from URLs
    delete        Remove URLs from the database
    import        Import URLs into the database
    tags          List tags from the database

Arguments:
    URL     An URL or path; if '-', looks for a list of URLs on stdin
    TAG     A tag
    FILE    Path to a file for import
    GROUP   A set of tags; Using a group sets all the tags within that group

Options:
    -h, --help          Print this help and exit
    --version           Print current version number and exit
    -d, --database DB   Path to the database to use
    -f, --format FMT    Input/Output format: text, json, msgpack, html
    -w, --web           Output to a minimal web server
    -v, --verbose       Display tags alongside the URL while listing

Conventions:
    bm supports the use of sets of tags.
    Anything starting with the symbol + will be understood as a tag set.
    If used instead of a URL it will add tags to the set.
    If used instead of a tag it will act as if all tags in the set were listed.
"""
VERSION = "2.0.0"

import os
import sys
from docopt import docopt

# Log function, by defaults prints nothing.
global log
log = lambda *x,**kx: None

class Database:
    def __init__(self, path):
        import sqlite3

        log("Initializing database from file " + path)
        self.path = path
        self.conn = sqlite3.connect(path)
        self._init_db()


    def _init_db(self):
        log

        if not os.path.exists(self.path):
            try:
                os.mkdir(os.path.split(self.path)[0])
            except FileExistsError:
                pass

        c = self.conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url STRING NOT NULL,
                UNIQUE(url)
            );
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name STRING NOT NULL,
                UNIQUE(name)
            );
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS x_tag_url (
                id_tag INTEGER NOT NULL,
                id_url INTEGER NOT NULL,
                PRIMARY KEY (id_tag, id_url)
            );
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS tagset (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name STRING NOT NULL,
                UNIQUE(name)
            );
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS x_tag_set (
                id_tag INTEGER NOT NULL,
                id_set INTEGER NOT NULL,
                PRIMARY KEY (id_tag, id_set)
            );
        """)

        self.conn.commit()


    def add(self, url, tags):
        log("Adding {} to {}".format(tags, url))

        c = self.conn.cursor()

        c.execute("INSERT OR IGNORE INTO urls (url) VALUES (?)", [url])

        # Remove duplicates
        tag = set(tags)

        c.executemany("""
            INSERT OR IGNORE INTO tags (name) VALUES (?)
        """, ([tag] for tag in tags))
        c.executemany("""
            INSERT OR IGNORE INTO x_tag_url (id_url, id_tag) VALUES (
                (SELECT id FROM urls WHERE url=?),
                (SELECT id FROM tags WHERE name=?)
            )
        """, ((url, tag) for tag in tags))

        self.conn.commit()


    def list(self, tags,  list_tags):
        log("List urls with tags {}" .format(tags))

        c = self.conn.cursor()

        if tags:
            stmt = "SELECT url FROM urls WHERE id in ("
            stmt += " INTERSECT ".join(
                "SELECT id_url FROM x_tag_url,tags WHERE id_tag=id AND name=?"
                for _ in tags)
            stmt += ")"

            log(stmt)

            c.execute(stmt, tags)

        else:
            c.execute("SELECT url FROM urls")

        urls = { u[0]: None for u in c.fetchall() }

        if list_tags:
            for url in urls.keys():
                c.execute("""
                    SELECT name FROM tags,x_tag_url,urls
                    WHERE id_url = urls.id
                    AND   id_tag = tags.id
                    AND   url    = ?;
                """, [url])
                urls[url] = [ t[0] for t in c.fetchall() ]

        return urls


    def remove(self, url, tags):
        log("Removing {} from {}".format(tags, url))

    def delete(self, urls):
        log("Deleting {}".format(url))

    def import_file(self, data, fmt):
        log("Importing data in {}".format(fmt))

        if fmt == "html":
            print("Error: html is not supported for import")
            return

        if fmt == "msgpack":
            import msgpack
            content = msgpack.loads(data)

        if fmt == "json":
            import json
            content = json.loads(data.decode("utf8"))

        if fmt == "text":
            data = data.decode("utf8")
            content = {
                l.split(' ')[0]: l.split(' ')[1:]
                for x in data.decode("utf8").splitlines()
            }

        for url,tags in content.items():
            self.add(url, tags)

    def tags(self, fmt, web):
        log("Listing all tags to {} in {}"
            .format("web" if web else "file", fmt))

        c = self.conn.cursor()

        c.execute("SELECT name FROM tags")

        tags = { t[0]: None for t in c.fetchall() }

        return tags

    def close(self):
        log("Closing database")
        self.conn.close()


def output_urls(urls, fmt, web):
    if fmt == "text":
        if None in urls.values():
            for url in urls:
                print(url)
        else:
            for url,tags in urls.items():
                print("{} {}".format(url, ' '.join(tags)))
        return

    if fmt == "json":
        import json
        if None in urls.values():
            print(json.dumps(list(urls.keys())))
        else:
            print(json.dumps(
                { url:list(tags) for url,tags in urls.items() }
            ))
        return

    if fmt == "msgpack":
        import msgpack
        if None in urls.values():
            sys.stdout.buffer.write(msgpack.dumps(list(urls.keys())))
        else:
            sys.stdout.buffer.write(msgpack.dumps(
                { url:list(tags) for url,tags in urls.items() }
            ))
        return

    if fmt == "html":
        return


def main():
    args = docopt(__doc__, version=VERSION)

    possible_formats = ("text", "json", "msgpack", "html")

    if args["--format"] is None:
        args["--format"] = "text"

    elif args["--format"] not in possible_formats:
        print("Error: --format must be one of ", possible_formats)
        return 1

    # To enable debug output, set de DEBUG environment variable
    if os.environ.get("DEBUG"):
        global log
        log = lambda *x,**kx: print("[debug]", *x, file=sys.stderr, **kx)

    db = Database(args.get("--database",
                  os.path.expanduser("~/.config/bm/bookmarks.sqlite")))

    if args["add"]:
        db.add(args["URL"][0], args["TAG"])

    elif args["list"]:
        output_urls(db.list(args["TAG"], args["--verbose"]),
                    args["--format"],
                    args["--web"])

    elif args["remove"]:
        db.remove(args["URL"][0], args["TAG"])

    elif args["delete"]:
        db.remove(args["URL"])

    elif args["import"]:
        for path in (os.path.expanduser(p) for p in args["FILE"]):
            with open(path, "rb") as f:
                db.import_file(f.read(), args["--format"])

    elif args["tags"]:
        db.tags(args["--format"], args["--web"])

    db.close()

if __name__ == "__main__":
    main()
