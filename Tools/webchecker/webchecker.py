#! /usr/bin/env python

"""Web tree checker.

This utility is handy to check a subweb of the world-wide web for
errors.  A subweb is specified by giving one or more ``root URLs''; a
page belongs to the subweb if one of the root URLs is an initial
prefix of it.

File URL extension:

In order to easy the checking of subwebs via the local file system,
the interpretation of ``file:'' URLs is extended to mimic the behavior
of your average HTTP daemon: if a directory pathname is given, the
file index.html in that directory is returned if it exists, otherwise
a directory listing is returned.  Now, you can point webchecker to the
document tree in the local file system of your HTTP daemon, and have
most of it checked.  In fact the default works this way if your local
web tree is located at /usr/local/etc/httpd/htdpcs (the default for
the NCSA HTTP daemon and probably others).

Report printed:

When done, it reports pages with bad links within the subweb.  When
interrupted, it reports for the pages that it has checked already.

In verbose mode, additional messages are printed during the
information gathering phase.  By default, it prints a summary of its
work status every 50 URLs (adjustable with the -r option), and it
reports errors as they are encountered.  Use the -q option to disable
this output.

Checkpoint feature:

Whether interrupted or not, it dumps its state (a Python pickle) to a
checkpoint file and the -R option allows it to restart from the
checkpoint (assuming that the pages on the subweb that were already
processed haven't changed).  Even when it has run till completion, -R
can still be useful -- it will print the reports again, and -Rq prints
the errors only.  In this case, the checkpoint file is not written
again.  The checkpoint file can be set with the -d option.

The checkpoint file is written as a Python pickle.  Remember that
Python's pickle module is currently quite slow.  Give it the time it
needs to load and save the checkpoint file.  When interrupted while
writing the checkpoint file, the old checkpoint file is not
overwritten, but all work done in the current run is lost.

Miscellaneous:

- You may find the (Tk-based) GUI version easier to use.  See wcgui.py.

- Webchecker honors the "robots.txt" convention.  Thanks to Skip
Montanaro for his robotparser.py module (included in this directory)!
The agent name is hardwired to "webchecker".  URLs that are disallowed
by the robots.txt file are reported as external URLs.

- Because the SGML parser is a bit slow, very large SGML files are
skipped.  The size limit can be set with the -m option.

- When the server or protocol does not tell us a file's type, we guess
it based on the URL's suffix.  The mimetypes.py module (also in this
directory) has a built-in table mapping most currently known suffixes,
and in addition attempts to read the mime.types configuration files in
the default locations of Netscape and the NCSA HTTP daemon.

- We follows links indicated by <A>, <FRAME> and <IMG> tags.  We also
honor the <BASE> tag.

- Checking external links is now done by default; use -x to *disable*
this feature.  External links are now checked during normal
processing.  (XXX The status of a checked link could be categorized
better.  Later...)


Usage: webchecker.py [option] ... [rooturl] ...

Options:

-R        -- restart from checkpoint file
-d file   -- checkpoint filename (default %(DUMPFILE)s)
-m bytes  -- skip HTML pages larger than this size (default %(MAXPAGE)d)
-n        -- reports only, no checking (use with -R)
-q        -- quiet operation (also suppresses external links report)
-r number -- number of links processed per round (default %(ROUNDSIZE)d)
-v        -- verbose operation; repeating -v will increase verbosity
-x        -- don't check external links (these are often slow to check)

Arguments:

rooturl   -- URL to start checking
             (default %(DEFROOT)s)

"""

# ' Emacs bait


__version__ = "0.4"


import sys
import os
from types import *
import string
import StringIO
import getopt
import pickle

import urllib
import urlparse
import sgmllib

import mimetypes
import robotparser


# Tunable parameters
DEFROOT = "file:/usr/local/etc/httpd/htdocs/"	# Default root URL
MAXPAGE = 150000			# Ignore files bigger than this
ROUNDSIZE = 50				# Number of links processed per round
DUMPFILE = "@webchecker.pickle"		# Pickled checkpoint
AGENTNAME = "webchecker"		# Agent name for robots.txt parser


# Global variables
verbose = 1
maxpage = MAXPAGE
roundsize = ROUNDSIZE


def main():
    global verbose, maxpage, roundsize
    dumpfile = DUMPFILE
    restart = 0
    checkext = 1
    norun = 0

    try:
	opts, args = getopt.getopt(sys.argv[1:], 'Rd:m:nqr:vx')
    except getopt.error, msg:
	sys.stdout = sys.stderr
	print msg
	print __doc__%globals()
	sys.exit(2)
    for o, a in opts:
	if o == '-R':
	    restart = 1
	if o == '-d':
	    dumpfile = a
	if o == '-m':
	    maxpage = string.atoi(a)
	if o == '-n':
	    norun = 1
	if o == '-q':
	    verbose = 0
	if o == '-r':
	    roundsize = string.atoi(a)
	if o == '-v':
	    verbose = verbose + 1
	if o == '-x':
	    checkext = not checkext

    if verbose > 0:
	print AGENTNAME, "version", __version__

    if restart:
	if verbose > 0:
	    print "Loading checkpoint from %s ..." % dumpfile
	f = open(dumpfile, "rb")
	c = pickle.load(f)
	f.close()
	if verbose > 0:
	    print "Done."
	    print "Root:", string.join(c.roots, "\n      ")
    else:
	c = Checker(checkext)
	if not args:
	    args.append(DEFROOT)

    for arg in args:
	c.addroot(arg)

    if not norun:
	try:
	    c.run()
	except KeyboardInterrupt:
	    if verbose > 0:
		print "[run interrupted]"

    try:
	c.report()
    except KeyboardInterrupt:
	if verbose > 0:
	    print "[report interrupted]"

    if not c.changed:
	if verbose > 0:
	    print
	    print "No need to save checkpoint"
    elif not dumpfile:
	if verbose > 0:
	    print "No dumpfile, won't save checkpoint"
    else:
	if verbose > 0:
	    print
	    print "Saving checkpoint to %s ..." % dumpfile
	newfile = dumpfile + ".new"
	f = open(newfile, "wb")
	pickle.dump(c, f)
	f.close()
	try:
	    os.unlink(dumpfile)
	except os.error:
	    pass
	os.rename(newfile, dumpfile)
	if verbose > 0:
	    print "Done."
	    if dumpfile == DUMPFILE:
		print "Use ``%s -R'' to restart." % sys.argv[0]
	    else:
		print "Use ``%s -R -d %s'' to restart." % (sys.argv[0],
							   dumpfile)


class Checker:

    def __init__(self, checkext=1):
	self.reset()
	self.checkext = checkext

    def reset(self):
	self.roots = []
	self.todo = {}
	self.done = {}
	self.bad = {}
	self.round = 0
	# The following are not pickled:
	self.robots = {}
	self.errors = {}
	self.urlopener = MyURLopener()
	self.changed = 0

    def __getstate__(self):
	return (self.roots, self.todo, self.done, self.bad, self.round)

    def __setstate__(self, state):
	(self.roots, self.todo, self.done, self.bad, self.round) = state
	for root in self.roots:
	    self.addrobot(root)
	for url in self.bad.keys():
	    self.markerror(url)

    def addroot(self, root):
	if root not in self.roots:
	    self.roots.append(root)
	    self.addrobot(root)
	    self.newlink(root, ("<root>", root))

    def addrobot(self, root):
	url = urlparse.urljoin(root, "/robots.txt")
	self.robots[root] = rp = robotparser.RobotFileParser()
	if verbose > 2:
	    print "Parsing", url
	    rp.debug = verbose > 3
	rp.set_url(url)
	try:
	    rp.read()
	except IOError, msg:
	    if verbose > 1:
		print "I/O error parsing", url, ":", msg

    def run(self):
	while self.todo:
	    self.round = self.round + 1
	    if verbose > 0:
		print
		print "Round %d (%s)" % (self.round, self.status())
		print 
	    urls = self.todo.keys()[:roundsize]
	    for url in urls:
		self.dopage(url)

    def status(self):
	return "%d total, %d to do, %d done, %d bad" % (
	    len(self.todo)+len(self.done),
	    len(self.todo), len(self.done),
	    len(self.bad))

    def report(self):
	print
	if not self.todo: print "Final",
	else: print "Interim",
	print "Report (%s)" % self.status()
	self.report_errors()

    def report_errors(self):
	if not self.bad:
	    print
	    print "No errors"
	    return
	print
	print "Error Report:"
	sources = self.errors.keys()
	sources.sort()
	for source in sources:
	    triples = self.errors[source]
	    print
	    if len(triples) > 1:
		print len(triples), "Errors in", source
	    else:
		print "Error in", source
	    for url, rawlink, msg in triples:
		print "  HREF", url,
		if rawlink != url: print "(%s)" % rawlink,
		print
		print "   msg", msg

    def dopage(self, url):
	if verbose > 1:
	    if verbose > 2:
		show("Check ", url, "  from", self.todo[url])
	    else:
		print "Check ", url
	page = self.getpage(url)
	if page:
	    for info in page.getlinkinfos():
		link, rawlink = info
		origin = url, rawlink
		self.newlink(link, origin)
	self.markdone(url)

    def newlink(self, url, origin):
	if self.done.has_key(url):
	    self.newdonelink(url, origin)
	else:
	    self.newtodolink(url, origin)

    def newdonelink(self, url, origin):
	self.done[url].append(origin)
	if verbose > 3:
	    print "  Done link", url

    def newtodolink(self, url, origin):
	if self.todo.has_key(url):
	    self.todo[url].append(origin)
	    if verbose > 3:
		print "  Seen todo link", url
	else:
	    self.todo[url] = [origin]
	    if verbose > 3:
		print "  New todo link", url

    def markdone(self, url):
	self.done[url] = self.todo[url]
	del self.todo[url]
	self.changed = 1

    def inroots(self, url):
	for root in self.roots:
	    if url[:len(root)] == root:
		return self.robots[root].can_fetch(AGENTNAME, url)
	return 0

    def getpage(self, url):
	if url[:7] == 'mailto:' or url[:5] == 'news:':
	    if verbose > 1: print " Not checking mailto/news URL"
	    return None
	isint = self.inroots(url)
	if not isint and not self.checkext:
	    if verbose > 1: print " Not checking ext link"
	    return None
	try:
	    f = self.urlopener.open(url)
	except IOError, msg:
	    msg = sanitize(msg)
	    if verbose > 0:
		print "Error ", msg
	    if verbose > 0:
		show(" HREF ", url, "  from", self.todo[url])
	    self.setbad(url, msg)
	    return None
	if not isint:
	    if verbose > 1: print " Not gathering links from ext URL"
	    safeclose(f)
	    return None
	nurl = f.geturl()
	info = f.info()
	if info.has_key('content-type'):
	    ctype = string.lower(info['content-type'])
	else:
	    ctype = None
	if nurl != url:
	    if verbose > 1:
		print " Redirected to", nurl
	if not ctype:
	    ctype, encoding = mimetypes.guess_type(nurl)
	if ctype != 'text/html':
	    safeclose(f)
	    if verbose > 1:
		print " Not HTML, mime type", ctype
	    return None
	text = f.read()
	f.close()
	return Page(text, nurl)

    def setgood(self, url):
	if self.bad.has_key(url):
	    del self.bad[url]
	    self.changed = 1
	    if verbose > 0:
		print "(Clear previously seen error)"

    def setbad(self, url, msg):
	if self.bad.has_key(url) and self.bad[url] == msg:
	    if verbose > 0:
		print "(Seen this error before)"
	    return
	self.bad[url] = msg
	self.changed = 1
	self.markerror(url)
	
    def markerror(self, url):
	try:
	    origins = self.todo[url]
	except KeyError:
	    origins = self.done[url]
	for source, rawlink in origins:
	    triple = url, rawlink, self.bad[url]
	    self.seterror(source, triple)

    def seterror(self, url, triple):
	try:
	    self.errors[url].append(triple)
	except KeyError:
	    self.errors[url] = [triple]


class Page:

    def __init__(self, text, url):
	self.text = text
	self.url = url

    def getlinkinfos(self):
	size = len(self.text)
	if size > maxpage:
	    if verbose > 0:
		print "Skip huge file", self.url
		print "  (%.0f Kbytes)" % (size*0.001)
	    return []
	if verbose > 2:
	    print "  Parsing", self.url, "(%d bytes)" % size
	parser = MyHTMLParser()
	parser.feed(self.text)
	parser.close()
	rawlinks = parser.getlinks()
	base = urlparse.urljoin(self.url, parser.getbase() or "")
	infos = []
	for rawlink in rawlinks:
	    t = urlparse.urlparse(rawlink)
	    t = t[:-1] + ('',)
	    rawlink = urlparse.urlunparse(t)
	    link = urlparse.urljoin(base, rawlink)
	    infos.append((link, rawlink))
	return infos


class MyStringIO(StringIO.StringIO):

    def __init__(self, url, info):
	self.__url = url
	self.__info = info
	StringIO.StringIO.__init__(self)

    def info(self):
	return self.__info

    def geturl(self):
	return self.__url


class MyURLopener(urllib.FancyURLopener):

    http_error_default = urllib.URLopener.http_error_default

    def __init__(*args):
	self = args[0]
	apply(urllib.FancyURLopener.__init__, args)
	self.addheaders = [('User-agent', 'Python-webchecker/%s' % __version__)]

    def open_file(self, url):
	path = urllib.url2pathname(urllib.unquote(url))
	if path[-1] != os.sep:
	    url = url + '/'
	if os.path.isdir(path):
	    indexpath = os.path.join(path, "index.html")
	    if os.path.exists(indexpath):
		return self.open_file(url + "index.html")
	    try:
		names = os.listdir(path)
	    except os.error, msg:
		raise IOError, msg, sys.exc_traceback
	    names.sort()
	    s = MyStringIO("file:"+url, {'content-type': 'text/html'})
	    s.write('<BASE HREF="file:%s">\n' %
		    urllib.quote(os.path.join(path, "")))
	    for name in names:
		q = urllib.quote(name)
		s.write('<A HREF="%s">%s</A>\n' % (q, q))
	    s.seek(0)
	    return s
	return urllib.FancyURLopener.open_file(self, path)


class MyHTMLParser(sgmllib.SGMLParser):

    def __init__(self):
	self.base = None
	self.links = {}
	sgmllib.SGMLParser.__init__ (self)

    def start_a(self, attributes):
	self.link_attr(attributes, 'href')

    def end_a(self): pass

    def do_img(self, attributes):
	self.link_attr(attributes, 'src', 'lowsrc')

    def do_frame(self, attributes):
	self.link_attr(attributes, 'src')

    def link_attr(self, attributes, *args):
	for name, value in attributes:
	    if name in args:
		if value: value = string.strip(value)
		if value: self.links[value] = None

    def do_base(self, attributes):
	for name, value in attributes:
	    if name == 'href':
		if value: value = string.strip(value)
		if value:
		    if verbose > 1:
			print "  Base", value
		    self.base = value

    def getlinks(self):
	return self.links.keys()

    def getbase(self):
	return self.base


def show(p1, link, p2, origins):
    print p1, link
    i = 0
    for source, rawlink in origins:
	i = i+1
	if i == 2:
	    p2 = ' '*len(p2)
	print p2, source,
	if rawlink != link: print "(%s)" % rawlink,
	print


def sanitize(msg):
    if (type(msg) == TupleType and
	len(msg) >= 4 and
	msg[0] == 'http error' and
	type(msg[3]) == InstanceType):
	# Remove the Message instance -- it may contain
	# a file object which prevents pickling.
	msg = msg[:3] + msg[4:]
    return msg


def safeclose(f):
    url = f.geturl()
    if url[:4] == 'ftp:' or url[:7] == 'file://':
	# Apparently ftp connections don't like to be closed
	# prematurely...
	text = f.read()
    f.close()


if __name__ == '__main__':
    main()
