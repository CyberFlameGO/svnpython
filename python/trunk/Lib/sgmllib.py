# A parser for SGML, using the derived class as static DTD.

# XXX This only supports those SGML features used by HTML.

# XXX There should be a way to distinguish between PCDATA (parsed
# character data -- the normal case), RCDATA (replaceable character
# data -- only char and entity references and end tags are special)
# and CDATA (character data -- only end tags are special).


import regex
import string


# Regular expressions used for parsing

interesting = regex.compile('[&<]')
incomplete = regex.compile('&\([a-zA-Z][a-zA-Z0-9]*\|#[0-9]*\)?\|'
			   '<\([a-zA-Z][^<>]*\|'
			      '/\([a-zA-Z][^<>]*\)?\|'
			      '![^<>]*\)?')

entityref = regex.compile('&\([a-zA-Z][a-zA-Z0-9]*\)[^a-zA-Z0-9]')
charref = regex.compile('&#\([0-9]+\)[^0-9]')

starttagopen = regex.compile('<[>a-zA-Z]')
shorttagopen = regex.compile('<[a-zA-Z][a-zA-Z0-9]*/')
shorttag = regex.compile('<\([a-zA-Z][a-zA-Z0-9]*\)/\([^/]*\)/')
endtagopen = regex.compile('</[<>a-zA-Z]')
endbracket = regex.compile('[<>]')
special = regex.compile('<![^<>]*>')
commentopen = regex.compile('<!--')
commentclose = regex.compile('--[ \t\n]*>')
tagfind = regex.compile('[a-zA-Z][a-zA-Z0-9]*')
attrfind = regex.compile(
    '[ \t\n]+\([a-zA-Z_][a-zA-Z_0-9]*\)'
    '\([ \t\n]*=[ \t\n]*'
    '\(\'[^\']*\'\|"[^"]*"\|[-a-zA-Z0-9./:+*%?!()_#=~]*\)\)?')


# SGML parser base class -- find tags and call handler functions.
# Usage: p = SGMLParser(); p.feed(data); ...; p.close().
# The dtd is defined by deriving a class which defines methods
# with special names to handle tags: start_foo and end_foo to handle
# <foo> and </foo>, respectively, or do_foo to handle <foo> by itself.
# (Tags are converted to lower case for this purpose.)  The data
# between tags is passed to the parser by calling self.handle_data()
# with some data as argument (the data may be split up in arbutrary
# chunks).  Entity references are passed by calling
# self.handle_entityref() with the entity reference as argument.

class SGMLParser:

    # Interface -- initialize and reset this instance
    def __init__(self, verbose=0):
	self.verbose = verbose
	self.reset()

    # Interface -- reset this instance.  Loses all unprocessed data
    def reset(self):
	self.rawdata = ''
	self.stack = []
	self.lasttag = '???'
	self.nomoretags = 0
	self.literal = 0

    # For derived classes only -- enter literal mode (CDATA) till EOF
    def setnomoretags(self):
	self.nomoretags = self.literal = 1

    # For derived classes only -- enter literal mode (CDATA)
    def setliteral(self, *args):
	self.literal = 1

    # Interface -- feed some data to the parser.  Call this as
    # often as you want, with as little or as much text as you
    # want (may include '\n').  (This just saves the text, all the
    # processing is done by goahead().)
    def feed(self, data):
	self.rawdata = self.rawdata + data
	self.goahead(0)

    # Interface -- handle the remaining data
    def close(self):
	self.goahead(1)

    # Internal -- handle data as far as reasonable.  May leave state
    # and data to be processed by a subsequent call.  If 'end' is
    # true, force handling all data as if followed by EOF marker.
    def goahead(self, end):
	rawdata = self.rawdata
	i = 0
	n = len(rawdata)
	while i < n:
	    if self.nomoretags:
		self.handle_data(rawdata[i:n])
		i = n
		break
	    j = interesting.search(rawdata, i)
	    if j < 0: j = n
	    if i < j: self.handle_data(rawdata[i:j])
	    i = j
	    if i == n: break
	    if rawdata[i] == '<':
		if starttagopen.match(rawdata, i) >= 0:
		    if self.literal:
			self.handle_data(rawdata[i])
			i = i+1
			continue
		    k = self.parse_starttag(i)
		    if k < 0: break
		    i = k
		    continue
		if endtagopen.match(rawdata, i) >= 0:
		    k = self.parse_endtag(i)
		    if k < 0: break
		    i =  k
		    self.literal = 0
		    continue
		if commentopen.match(rawdata, i) >= 0:
		    if self.literal:
			self.handle_data(rawdata[i])
			i = i+1
			continue
		    k = self.parse_comment(i)
		    if k < 0: break
		    i = i+k
		    continue
		k = special.match(rawdata, i)
		if k >= 0:
		    if self.literal:
			self.handle_data(rawdata[i])
			i = i+1
			continue
		    i = i+k
		    continue
	    elif rawdata[i] == '&':
		k = charref.match(rawdata, i)
		if k >= 0:
		    k = i+k
		    if rawdata[k-1] != ';': k = k-1
		    name = charref.group(1)
		    self.handle_charref(name)
		    i = k
		    continue
		k = entityref.match(rawdata, i)
		if k >= 0:
		    k = i+k
		    if rawdata[k-1] != ';': k = k-1
		    name = entityref.group(1)
		    self.handle_entityref(name)
		    i = k
		    continue
	    else:
		raise RuntimeError, 'neither < nor & ??'
	    # We get here only if incomplete matches but
	    # nothing else
	    k = incomplete.match(rawdata, i)
	    if k < 0:
		self.handle_data(rawdata[i])
		i = i+1
		continue
	    j = i+k
	    if j == n:
		break # Really incomplete
	    self.handle_data(rawdata[i:j])
	    i = j
	# end while
	if end and i < n:
	    self.handle_data(rawdata[i:n])
	    i = n
	self.rawdata = rawdata[i:]
	# XXX if end: check for empty stack

    # Internal -- parse comment, return length or -1 if not terminated
    def parse_comment(self, i):
	rawdata = self.rawdata
	if rawdata[i:i+4] <> '<!--':
	    raise RuntimeError, 'unexpected call to handle_comment'
	j = commentclose.search(rawdata, i+4)
	if j < 0:
	    return -1
	self.handle_comment(rawdata[i+4: j])
	j = j+commentclose.match(rawdata, j)
	return j-i

    # Internal -- handle starttag, return length or -1 if not terminated
    def parse_starttag(self, i):
	rawdata = self.rawdata
	if shorttagopen.match(rawdata, i) >= 0:
	    # SGML shorthand: <tag/data/ == <tag>data</tag>
	    # XXX Can data contain &... (entity or char refs)?
	    # XXX Can data contain < or > (tag characters)?
	    # XXX Can there be whitespace before the first /?
	    j = shorttag.match(rawdata, i)
	    if j < 0:
		return -1
	    tag, data = shorttag.group(1, 2)
	    tag = string.lower(tag)
	    self.finish_shorttag(tag, data)
	    k = i+j
	    if rawdata[k-1] == '<':
		k = k-1
	    return k
	# XXX The following should skip matching quotes (' or ")
	j = endbracket.search(rawdata, i+1)
	if j < 0:
	    return -1
	# Now parse the data between i+1 and j into a tag and attrs
	attrs = []
	if rawdata[i:i+2] == '<>':
	    # SGML shorthand: <> == <last open tag seen>
	    k = j
	    tag = self.lasttag
	else:
	    k = tagfind.match(rawdata, i+1)
	    if k < 0:
		raise RuntimeError, 'unexpected call to parse_starttag'
	    k = i+1+k
	    tag = string.lower(rawdata[i+1:k])
	    self.lasttag = tag
	while k < j:
	    l = attrfind.match(rawdata, k)
	    if l < 0: break
	    attrname, rest, attrvalue = attrfind.group(1, 2, 3)
	    if not rest:
		attrvalue = attrname
	    elif attrvalue[:1] == '\'' == attrvalue[-1:] or \
		 attrvalue[:1] == '"' == attrvalue[-1:]:
		attrvalue = attrvalue[1:-1]
	    attrs.append((string.lower(attrname), attrvalue))
	    k = k + l
	if rawdata[j] == '>':
	    j = j+1
	self.finish_starttag(tag, attrs)
	return j

    # Internal -- parse endtag
    def parse_endtag(self, i):
	rawdata = self.rawdata
	j = endbracket.search(rawdata, i+1)
	if j < 0:
	    return -1
	tag = string.lower(string.strip(rawdata[i+2:j]))
	if rawdata[j] == '>':
	    j = j+1
	self.finish_endtag(tag)
	return j

    # Internal -- finish parsing of <tag/data/ (same as <tag>data</tag>)
    def finish_shorttag(self, tag, data):
	self.finish_starttag(tag, [])
	self.handle_data(data)
	self.finish_endtag(tag)

    # Internal -- finish processing of start tag
    # Return -1 for unknown tag, 0 for open-only tag, 1 for balanced tag
    def finish_starttag(self, tag, attrs):
	try:
	    method = getattr(self, 'start_' + tag)
	except AttributeError:
	    try:
		method = getattr(self, 'do_' + tag)
	    except AttributeError:
		self.unknown_starttag(tag, attrs)
		return -1
	    else:
		self.handle_starttag(tag, method, attrs)
		return 0
	else:
	    self.stack.append(tag)
	    self.handle_starttag(tag, method, attrs)
	    return 1

    # Internal -- finish processing of end tag
    def finish_endtag(self, tag):
	if not tag:
	    found = len(self.stack) - 1
	    if found < 0:
		self.unknown_endtag(tag)
		return
	else:
	    if tag not in self.stack:
		try:
		    method = getattr(self, 'end_' + tag)
		except AttributeError:
		    self.unknown_endtag(tag)
		return
	    found = len(self.stack)
	    for i in range(found):
		if self.stack[i] == tag: found = i
	while len(self.stack) > found:
	    tag = self.stack[-1]
	    try:
		method = getattr(self, 'end_' + tag)
	    except AttributeError:
		method = None
	    if method:
		self.handle_endtag(tag, method)
	    else:
		self.unknown_endtag(tag)
	    del self.stack[-1]

    # Overridable -- handle start tag
    def handle_starttag(self, tag, method, attrs):
	method(attrs)

    # Overridable -- handle end tag
    def handle_endtag(self, tag, method):
	method()

    # Example -- report an unbalanced </...> tag.
    def report_unbalanced(self, tag):
	if self.verbose:
	    print '*** Unbalanced </' + tag + '>'
	    print '*** Stack:', self.stack

    # Example -- handle character reference, no need to override
    def handle_charref(self, name):
	try:
	    n = string.atoi(name)
	except string.atoi_error:
	    self.unknown_charref(name)
	    return
	if not 0 <= n <= 255:
	    self.unknown_charref(name)
	    return
	self.handle_data(chr(n))

    # Definition of entities -- derived classes may override
    entitydefs = \
	    {'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': '\''}

    # Example -- handle entity reference, no need to override
    def handle_entityref(self, name):
	table = self.entitydefs
	if table.has_key(name):
	    self.handle_data(table[name])
	else:
	    self.unknown_entityref(name)
	    return

    # Example -- handle data, should be overridden
    def handle_data(self, data):
	pass

    # Example -- handle comment, could be overridden
    def handle_comment(self, data):
	pass

    # To be overridden -- handlers for unknown objects
    def unknown_starttag(self, tag, attrs): pass
    def unknown_endtag(self, tag): pass
    def unknown_charref(self, ref): pass
    def unknown_entityref(self, ref): pass


class TestSGMLParser(SGMLParser):

    def __init__(self, verbose=0):
	self.testdata = ""
	SGMLParser.__init__(self, verbose)

    def handle_data(self, data):
	self.testdata = self.testdata + data
	if len(`self.testdata`) >= 70:
	    self.flush()

    def flush(self):
	data = self.testdata
	if data:
	    self.testdata = ""
	    print 'data:', `data`

    def handle_comment(self, data):
	self.flush()
	r = `data`
	if len(r) > 68:
	    r = r[:32] + '...' + r[-32:]
	print 'comment:', r

    def unknown_starttag(self, tag, attrs):
	self.flush()
	if not attrs:
	    print 'start tag: <' + tag + '>'
	else:
	    print 'start tag: <' + tag,
	    for name, value in attrs:
		print name + '=' + '"' + value + '"',
	    print '>'

    def unknown_endtag(self, tag):
	self.flush()
	print 'end tag: </' + tag + '>'

    def unknown_entityref(self, ref):
	self.flush()
	print '*** unknown entity ref: &' + ref + ';'

    def unknown_charref(self, ref):
	self.flush()
	print '*** unknown char ref: &#' + ref + ';'

    def close(self):
	SGMLParser.close(self)
	self.flush()


def test(args = None):
    import sys

    if not args:
	args = sys.argv[1:]

    if args and args[0] == '-s':
	args = args[1:]
	klass = SGMLParser
    else:
	klass = TestSGMLParser

    if args:
	file = args[0]
    else:
	file = 'test.html'

    if file == '-':
	f = sys.stdin
    else:
	try:
	    f = open(file, 'r')
	except IOError, msg:
	    print file, ":", msg
	    sys.exit(1)

    data = f.read()
    if f is not sys.stdin:
	f.close()

    x = klass()
    for c in data:
	x.feed(c)
    x.close()


if __name__ == '__main__':
    test()
