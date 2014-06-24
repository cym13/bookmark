#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

URLS = [
        "http://99-bottles-of-beer.net",
        "http://c0de517e.blogspot.ca/2014/06/where-is-my-c-replacement.html",
        "http://code.dlang.org/",
        "http://cryptography.readthedocs.org/en/latest/",
        "http://ddili.org/ders/d.en/index.html",
        "http://dlang.org/",
        "http://nomad.so/2013/07/templates-in-d-explained/",
        "http://nuitka.net/posts/try-finally-python-quiz.html",
        "http://outspeaking.com/words-of-technology/why-perl-didnt-win.html",
        "http://paper.li/johnhubner/1385333810",
        "http://pyvideo.org/",
        "http://radare.org/y/?",
        "http://rosettacode.org/wiki/Rosetta_Code",
        "http://rounin.livejournal.com/24465.html",
        "http://sametmax.com/",
        "http://sametmax.com/creer-un-decorateur-a-la-volee/",
        "http://scratch.mit.edu/projects/editor/?tip_bar=getStarted",
        "http://sebastianraschka.com/Articles/2014_multiprocessing_intro.html",
        "http://senko.net/maybe-monad-in-python",
        "http://tutorialzine.com/2014/06/guess-the-programming-language/",
        "http://www.dabeaz.com/generators-uk/",
        "http://www.digitalmars.com/d/1.0/index.html",
        "http://www.dprogramming.com/",
        "http://www.linuxjournal.com/article/3882",
        "http://www.matthieuamiguet.ch/blog/diy-guitar-effects-python",
        "http://www.pyexpert.com/tutorials/pseudoprivate.html",
        "http://www.stavros.io/posts/bloom-filter-search-engine/",
        "http://www.stavros.io/posts/python-fuse-filesystem/",
        "https://archive.org/details/dconf2014-day-01-talk06",
        "https://codeboom.wordpress.com/2011/12/20/teaching-students-to-think/",
        "https://codility.com/c/intro/demoPRM9Y5-7WV",
        "https://denibertovic.com/posts/celery-best-practices/",
        "https://hackerone.com/programs",
        "https://tavianator.com/2014/06/the-visitor-pattern-in-python/",
        "https://www.bountysource.com/"
        ]

ABS_PATHS = [
        "/bin",
        "/root",
        "/usr/",
        "/usr/bin",
        "/usr/bin/",
        "/lib"
        ]

PATH = [
        "test",
        "test/",
        "test/a",
        "test/a/"
        ]

MISC = [
        "dog",
        "cat",
        "1546",
        "~/'\\,+«»—",
        "  _ "
        ]

def generalTest(database, urls, tags):
    for url in url:
        bm.add(database, url, tags)
        yield bm.list_any(database, [tags[0], tags[1]])
        yield bm.list_every(database, [tags[0], tags[1]])
        bm.add(database, url, tags)
        yield bm.list_any(database, [tags[0], tags[1]])
        yield bm.list_every(database, [tags[0], tags[1]])
        bm.remove(database, url, tags[0])
        yield bm.list_any(database, [tags[0], tags[1]])
        yield bm.list_every(database, [tags[0], tags[1]])
        bm.add(database, url, tags)
        yield bm.list_any(database, [tags[0], tags[1]])
        yield bm.list_every(database, [tags[0], tags[1]])
        bm.delete(database, url)
        yield bm.list_any(database, [tags[0], tags[1]])
        yield bm.list_every(database, [tags[0], tags[1]])
        bm.add(database, url, tags)
        bm.remove(database, url, tags)
        yield bm.list_any(database, [tags[0], tags[1]])
        yield bm.list_every(database, [tags[0], tags[1]])


def test():
    pass
