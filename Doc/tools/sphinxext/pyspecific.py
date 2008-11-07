# -*- coding: utf-8 -*-
"""
    pyspecific.py
    ~~~~~~~~~~~~~

    Sphinx extension with Python doc-specific markup.

    :copyright: 2008 by Georg Brandl.
    :license: Python license.
"""

ISSUE_URI = 'http://bugs.python.org/issue%s'

from docutils import nodes, utils

def issue_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    issue = utils.unescape(text)
    text = 'issue ' + issue
    refnode = nodes.reference(text, text, refuri=ISSUE_URI % issue)
    return [refnode], []


# Support for building "topic help" for pydoc

pydoc_topic_labels = [
    'assert', 'assignment', 'atom-identifiers', 'atom-literals',
    'attribute-access', 'attribute-references', 'augassign', 'binary',
    'bitwise', 'bltin-code-objects', 'bltin-ellipsis-object',
    'bltin-file-objects', 'bltin-null-object', 'bltin-type-objects', 'booleans',
    'break', 'callable-types', 'calls', 'class', 'comparisons', 'compound',
    'context-managers', 'continue', 'conversions', 'customization', 'debugger',
    'del', 'dict', 'dynamic-features', 'else', 'exceptions', 'execmodel',
    'exprlists', 'floating', 'for', 'formatstrings', 'function', 'global',
    'id-classes', 'identifiers', 'if', 'imaginary', 'import', 'in', 'integers',
    'lambda', 'lists', 'naming', 'numbers', 'numeric-types', 'objects',
    'operator-summary', 'pass', 'power', 'raise', 'return', 'sequence-types',
    'shifting', 'slicings', 'specialattrs', 'specialnames', 'string-methods',
    'strings', 'subscriptions', 'truth', 'try', 'types', 'typesfunctions',
    'typesmapping', 'typesmethods', 'typesmodules', 'typesseq',
    'typesseq-mutable', 'unary', 'while', 'with', 'yield'
]

from os import path
from time import asctime
from pprint import pformat
from docutils.io import StringOutput
from docutils.utils import new_document
from sphinx.builder import Builder
from sphinx.textwriter import TextWriter

class PydocTopicsBuilder(Builder):
    name = 'pydoc-topics'

    def init(self):
        self.topics = {}

    def get_outdated_docs(self):
        return 'all pydoc topics'

    def get_target_uri(self, docname, typ=None):
        return ''  # no URIs

    def write(self, *ignored):
        writer = TextWriter(self)
        for label in self.status_iterator(pydoc_topic_labels, 'building topics... '):
            if label not in self.env.labels:
                self.warn('label %r not in documentation' % label)
                continue
            docname, labelid, sectname = self.env.labels[label]
            doctree = self.env.get_and_resolve_doctree(docname, self)
            document = new_document('<section node>')
            document.append(doctree.ids[labelid])
            destination = StringOutput(encoding='utf-8')
            writer.write(document, destination)
            self.topics[label] = str(writer.output)

    def finish(self):
        f = open(path.join(self.outdir, 'pydoc_topics.py'), 'w')
        try:
            f.write('# Autogenerated by Sphinx on %s\n' % asctime())
            f.write('topics = ' + pformat(self.topics) + '\n')
        finally:
            f.close()


# Support for documenting Opcodes

import re
from sphinx import addnodes

opcode_sig_re = re.compile(r'(\w+(?:\+\d)?)\s*\((.*)\)')

def parse_opcode_signature(env, sig, signode):
    """Transform an opcode signature into RST nodes."""
    m = opcode_sig_re.match(sig)
    if m is None:
        raise ValueError
    opname, arglist = m.groups()
    signode += addnodes.desc_name(opname, opname)
    paramlist = addnodes.desc_parameterlist()
    signode += paramlist
    paramlist += addnodes.desc_parameter(arglist, arglist)
    return opname.strip()


def setup(app):
    app.add_role('issue', issue_role)
    app.add_builder(PydocTopicsBuilder)
    app.add_description_unit('opcode', 'opcode', '%s (opcode)',
                             parse_opcode_signature)
