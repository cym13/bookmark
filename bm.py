#!/usr/bin/env python3

"""
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

# Debug log function, by defaults prints nothing.
global debug
debug = lambda *x,**kx: None

class Database:
    def __init__(self, path):
        import sqlite3

        debug("Initializing database from file " + path)
        self.path = path
        self.conn = sqlite3.connect(path)
        self._init_db()


    def _init_db(self):
        if not os.path.exists(self.path):
            try:
                os.mkdir(os.path.split(self.path)[0])
            except FileExistsError:
                pass

        c = self.conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url STRING NOT NULL, UNIQUE(url)
            );
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name STRING NOT NULL, UNIQUE(name)
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
                name STRING NOT NULL, UNIQUE(name)
            );
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS x_tag_set (
                id_tag INTEGER NOT NULL,
                id_set INTEGER NOT NULL,
                PRIMARY KEY (id_tag, id_set)
            );
        """)

        c.execute("""
            CREATE VIEW IF NOT EXISTS v_tag_url (url, tag) AS
            SELECT url,name FROM urls,tags,x_tag_url
            WHERE urls.id=id_url
            AND   tags.id=id_tag;
        """)

        self.conn.commit()


    def add(self, url, tags):
        debug("Adding {} to {}".format(tags, url))

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
        debug("List urls with tags {}" .format(tags))

        c = self.conn.cursor()

        if tags:
            stmt = " INTERSECT ".join("SELECT url FROM v_tag_url WHERE tag=?"
                                      for _ in tags)
            debug(stmt)
            c.execute(stmt, tags)

        else:
            c.execute("SELECT url FROM urls ORDER BY url")

        urls = { u[0]: None for u in c.fetchall() }

        if list_tags:
            for url in urls.keys():
                c.execute("""
                    SELECT name FROM tags,x_tag_url,urls
                    WHERE id_url = urls.id
                    AND   id_tag = tags.id
                    AND   url    = ?
                    ORDER BY url;
                """, [url])
                urls[url] = [ t[0] for t in c.fetchall() ]

        return urls


    def remove(self, url, tags):
        debug("Removing {} from {}".format(tags, url))

        c = self.conn.cursor()

        c.executemany("""
            DELETE FROM x_tag_url
            WHERE id_url = (SELECT id FROM urls WHERE url=?)
            AND   id_tag = (SELECT id FROM tags WHERE name=?);
        """, ((url, tag) for tag in tags))

        self.conn.commit()

        debug("Cleaning unaffilliated tags")

        c.execute("""
            DELETE FROM tags
            WHERE NOT EXISTS (
                SELECT id_url FROM x_tag_url
                WHERE id_tag=tags.id
            );
        """);

        debug("Cleaning unaffilliated urls")

        c.execute("""
            DELETE FROM urls
            WHERE NOT EXISTS (
                SELECT id_tag FROM x_tag_url
                WHERE id_url=urls.id
            );
        """);

        self.conn.commit()


    def delete(self, urls):
        debug("Deleting {}".format(urls))

        c = self.conn.cursor()

        c.executemany("DELETE FROM urls WHERE url=?", [urls])

        debug("Cleaning unaffilliated XREF")

        c.execute("""
            DELETE FROM x_tag_url
            WHERE NOT EXISTS (
                SELECT id FROM urls
                WHERE id_url=urls.id
            );
        """)

        debug("Cleaning unaffilliated tags")

        c.execute("""
            DELETE FROM tags
            WHERE NOT EXISTS (
                SELECT id_url FROM x_tag_url
                WHERE id_tag=tags.id
            );
        """);

        self.conn.commit()

    def import_file(self, data, fmt):
        debug("Importing data in {}".format(fmt))

        if fmt == "html":
            print("Error: html is not supported for import")
            return

        if fmt == "msgpack":
            import msgpack
            content = msgpack.loads(data, encoding="utf-8")

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

    def tags(self, urls):
        c = self.conn.cursor()

        if not urls:
            debug("Listing all tags")

            c.execute("""
                SELECT name,count(id_url) FROM tags,x_tag_url
                WHERE id_tag=id
                GROUP BY name
                ORDER BY 2;
            """)

            return { t[0]: t[1] for t in c.fetchall() }

        debug("Listing tags from {}".format(urls))
        stmt = " UNION ".join("SELECT tag FROM v_tag_url WHERE url=?"
                              for _ in urls)
        c.execute(stmt, urls)

        return { t[0]: None for t in c.fetchall() }


    def close(self):
        debug("Closing database")
        self.conn.close()


def format_urls(urls, fmt, search=[]):
    debug("Outputing {} urls in {}")

    verbose = not None in urls.values()

    if fmt == "msgpack":
        import msgpack
        if not verbose:
            return msgpack.dumps(list(urls.keys()))
        else:
            return msgpack.dumps(
                { url:list(tags) for url,tags in urls.items() }
            )

    if fmt == "text":
        if not verbose:
            result =  '\n'.join(urls)
        else:
            result = '\n'.join("{} {}".format(url, ' '.join(tags))
                               for url,tags in urls.items())

    elif fmt == "json":
        import json
        if not verbose:
            result = json.dumps(list(urls.keys()), indent=4)
        else:
            result = json.dumps({ url:list(tags) for url,tags in urls.items() },
                                indent=4)

    elif fmt == "web":
        if not search:
            result = html_generator(["All urls"], urls)
        else:
            result = html_generator(search, urls)

    return (result + "\n").encode("utf-8")


def output_tags(tags, fmt, web):
    if fmt == "msgpack":
        import msgpack
        if None in tags.values():
            return msgpack.dumps(tags.keys())
        else:
            return msgpack.dumps(
                { tag:count for tag,count in tags.items() }
            )

    if fmt == "text":
        if None in tags.values():
            result =  '\n'.join(tags)
        else:
            result = '\n'.join("{} {}".format(tag, count)
                               for tag,count in tags.items())

    elif fmt == "json":
        import json
        if None in tags.values():
            result = json.dumps(tags.keys(), indent=4)
        else:
            result = json.dumps({ tag:count for tag,count in tags.items() },
                                indent=4)

    elif fmt == "web":
        print("Error: web output not supported for tag listing")

    return (result + "\n").encode("utf-8")


def output(data, fmt):
    if fmt != "web":
        sys.stdout.buffer.write(data)
        return

    import webbrowser

    temp_dir = "/tmp/bm-{}/".format(os.getuid())

    try:
        os.mkdir(temp_dir)
    except FileExistsError:
        if os.stat(temp_dir).st_uid != os.getuid():
            print("Error: wrong directory permissions")
            return
    path = temp_dir + "bm.html"
    with open(path, "wb") as f:
        f.write(data)
        webbrowser.open(path)


def html_generator(search, sites):
    template = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8" />
        <title>bookmark</title>
      </head>
      <body>
        <h1>
          {tags}
        </h1>
        <ol>
          {sites}
        </ol>
      </body>
    </html>
    """

    li_html  = '<li><a href="{u}">{u}</a><p>{t}</p></li>'

    li_items = []
    for url,tags in sites.items():
        if tags is None:
            tags = []
        li_items.append(li_html.format(u=url, t=','.join(tags)))

    template = template.format(tags=', '.join(search),
                               sites=('\n'+' '*10).join(li_items))
    debug(template)
    return template

def main():
    supported_formats = ("text", "json", "msgpack", "web")

    args = docopt(__doc__, version=VERSION)

    if args["--format"] is None:
        args["--format"] = "text"

    elif args["--format"] not in supported_formats:
        print("Error: --format must be one of ", supported_formats)
        return 1

    # To enable debug output, set de DEBUG environment variable
    if os.environ.get("DEBUG"):
        global debug
        debug = lambda *x,**kx: print("[debug]", *x, file=sys.stderr, **kx)

    db = Database(args.get("--database",
                  os.path.expanduser("~/.config/bm/bookmarks.sqlite")))

    if args["add"]:
        db.add(args["URL"][0], args["TAG"])

    elif args["list"]:
        output(format_urls(db.list(args["TAG"],
                                   args["--verbose"]),
                           args["--format"],
                           search=args["TAG"]),
               args["--format"])

    elif args["remove"]:
        db.remove(args["URL"][0], args["TAG"])

    elif args["delete"]:
        db.delete(args["URL"])

    elif args["import"]:
        for path in (os.path.expanduser(p) for p in args["FILE"]):
            if path == "-":
                db.import_file(sys.stdin.buffer.read(), args["--format"])
            else:
                with open(path, "rb") as f:
                    db.import_file(f.read(), args["--format"])

    elif args["tags"]:
        output_tags(db.tags(args["URL"]),
                    args["--format"],
                    args["--web"])

    db.close()

if __name__ == "__main__":
    main()
