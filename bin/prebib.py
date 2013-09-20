#!/usr/bin/env python
# ---------------------------------------------------------------------
# Soft-dev Bibtex Preprocessor
# ---------------------------------------------------------------------
# Note this requires Python 3 and the bibtexparser module.
#
# Copyright (c) 2013 Edd Barrett <vext01@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys, re, io

import yapbib.biblist as biblist

# Stuff that we don't want to see in the bibtex file (per-class)
# In the future we may allow the user to adjust this by command line
# flags. But let's cross that bridge when we encounter it.
EXCLUDE_MAP = {
    "book"          : [],
    "article"       : ["abstract", "location", "publisher"],
    "techreport"    : ["abstract", "location", "publisher"],
    "inproceedings" : ["abstract", "location", "publisher"],
    "incollection"  : ["abstract", "location", "publisher"],
}

# Warn if fields match a regex
REGEX_WARNINGS = {
    "booktitle" : [".*Proc\.", ".*Proceedings"],
    "author" : [".*[Ee]dward [Bb]arrett"] # Prefer "Edd"
}

def usage():
    print("usage: prebib.py <infile>")
    sys.exit(1)

def encode(st):
    """
    The bibtex parser undoes escaping, so we have to put it back.
    This kinda sucks...
    """
    for (k, v) in unicode_to_crappy_latex1.items(): # yes, i know...
        st = st.replace(k, v)

    return st

def format_entry(bclass, key, data):
    """ Throws out a nicely formatted bibtex entry """
    s = "@%s{%s,\n" % (bclass, key)

    for (k, v) in data.items():
        s += "    %s = {%s},\n" % (k, v)

    return s + "}\n"

def process(infile):
    """ Process a file by name """
    b=biblist.BibList()
    b.import_bibtex(infile) # XXX comments etc..

    entries = b.get_items()
    new_entries = [ process_entry(x) for x in entries ]

    # stuff the items back into a new biblist
    biblist2 = biblist.BibList()
    for e in new_entries: biblist2.add_item(e)

    # chuck to stdout
    biblist2.export_bibtex()

def msg(msg, fatal=False):
    """ Display a warning or error """
    if not fatal:
        sys.stderr.write("***warn: %s\n" % msg)
    else:
        sys.stderr.write("***error: %s\n" % msg)

    sys.stderr.flush()
    if fatal: sys.exit(1)

def regex_warn(key, data):
    """ Warn about common error that can be detected by regex """
    for (f, v) in data.items():

        if f == "author": # library splits authors
            v = u"and".join([ u" ".join(x) for x in v])

        try:
            regexes = REGEX_WARNINGS[f]
        except KeyError:
            continue # no regexes to test

        for r in regexes:
            if re.match(r, v):
                msg("Entry '%s': '%s={%s}'\n  fires a naughty regex '%s'" % \
                        (key, f, v, r))

def process_entry(entry):
    bclass = entry["_type"]
    key = entry["_code"]

    try:
        excludes = EXCLUDE_MAP[bclass]
    except KeyError:
        msg("undefined excludes for bibtex class '%s'" % (bclass))
        excludes = [] # exclude nothing

    # filter out junk we don't want
    filtered_data = { k : v for (k, v) in entry.items() if k not in excludes }
    regex_warn(key, filtered_data)
    return filtered_data

if __name__ == "__main__":
    if len(sys.argv) != 2: usage()
    process(sys.argv[1])
