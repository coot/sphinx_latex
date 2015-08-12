# -*- coding: utf-8 -*-
"""
LaTeX writer for Sphinx which allows to use arbitrary LaTeX class.

Also includes clatex_sphinx.py Sphinx extension.
"""

import sys
from os import path
from docutils import nodes
from sphinx import highlighting
import sphinx.writers.latex
from sphinx.util.osutil import ustrftime
from sphinx.ext.mathbase import latex_visit_math, latex_visit_displaymath, latex_visit_eqref

import clatex_sphinx

HEADER = r'''%%%% File generated by Sphinx clatex builder
%(documentclass)s

%%%% Added by Sphinx:
\usepackage[%(hyperref_args)s]{hyperref}
%(longtable)s
%(tabulary)s
%(multirow)s
%(makeidx)s
%%%% Sphinx: addition's end.

%(preamble)s
'''

BEGIN_DOC = \
r'''
\begin{document}
%(begin_doc)s
'''

FOOTER = \
r'''
%(end_doc)s
\end{document}
'''

class CustomLaTeXWriter(sphinx.writers.latex.LaTeXWriter):

    def translate(self):
        visitor = CustomLaTeXTranslator(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.astext()

class CustomLaTeXTranslator(sphinx.writers.latex.LaTeXTranslator, nodes.NodeVisitor, object):

    default_elements = {
        'preamble': '',
        'begin_doc': '',
        'end_doc': '',
        'longtable': '',
        'tabulary': '\\usepackage{tabulary}',
        'multirow': '\\usepackage{multirow}',
        'hyperref_args': '',
        'makeidx': '',
        'documentclass': '\documentclass{book}',
        'shorthandoff': '',
        'transition': '\n\n\\bigskip\\hrule{}\\bigskip\n\n',
        'figure_align': 'htbp',
        }

    def visit_document(self, node):
        self.footnotestack.append(self.collect_footnotes(node))
        self.curfilestack.append(node.get('docname', ''))
        if self.first_document == 1:
            # the first document is all the regular content ...
            self.body.append(BEGIN_DOC % self.elements)
            self.first_document = 0
        elif self.first_document == 0:
            # ... and all others are the appendices
            self.body.append(u'\n\\appendix\n')
            self.first_document = -1
        if 'docname' in node:
            self.body.append(self.hypertarget(':doc'))
        # "- 1" because the level is increased before the title is visited
        self.sectionlevel = self.top_sectionlevel - 1

    # todo: I should find a real solution
    def visit_transition(self, node):
        try:
            self.body.append(self.elements['transition'])
        except Exception, e:
            print('ERROR: %s' % e)

    def __init__(self, document, builder):

        # super(type(self), self).__init__(document, builder)
        nodes.NodeVisitor.__init__(self, document)
        self.builder = builder
        self.body = []
        self.elements = self.default_elements.copy()
        if type(builder.config.clatex_makeidx) == bool:
            if builder.config.clatex_makeidx:
                makeidx = '\\usepackage{makeidx}\n\\makeindex'
            else:
                makeidx = ''
        else:
            makeidx = builder.config.clatex_makeidx
        self.elements.update({
            'author':       document.settings.author,
            'title':        document.settings.title,
            'documentclass': builder.config.clatex_documentclass,
            'preamble':     builder.config.clatex_preamble,
            'begin_doc':    builder.config.clatex_begin_doc,
            'end_doc':      builder.config.clatex_end_doc,
            'hyperref_args': builder.config.clatex_hyperref_args,
            'makeidx':      makeidx,
            })
        self.highlighter = highlighting.PygmentsBridge('latex',
            builder.config.pygments_style, builder.config.trim_doctest_flags)
        self.context = []
        self.descstack = []
        self.bibitems = []
        self.table = None
        self.next_table_colspec = None
        # stack of [language, linenothreshold] settings per file
        # the first item here is the default and must not be changed
        # the second item is the default for the master file and can be changed
        # by .. highlight:: directive in the master file
        self.hlsettingstack = 2 * [[builder.config.highlight_language,
                                    sys.maxint]]
        self.footnotestack = []
        self.curfilestack = []
        self.handled_abbrs = set()
        if builder.config.latex_use_parts:
            self.top_sectionlevel = 0
        else:
            if builder.config.clatex_use_chapters:
                self.top_sectionlevel = 1
            else:
                self.top_sectionlevel = 2
        self.next_section_ids = set()
        self.next_figure_ids = set()
        self.next_table_ids = set()
        # flags
        self.verbatim = None
        self.in_title = 0
        self.in_production_list = 0
        self.in_footnote = 0
        self.in_caption = 0
        self.first_document = 1
        self.this_is_the_title = 1
        self.literal_whitespace = 0
        self.no_contractions = 0
        self.compact_list = 0
        self.first_param = 0
        self.previous_spanning_row = 0
        self.previous_spanning_column = 0
        self.remember_multirow = {}

    def astext(self):
        HEADER = self.builder.app.config.clatex_header
        if self.builder.config.clatex_highlighter:
            return (HEADER % self.elements +
                    self.highlighter.get_stylesheet() +
                    u''.join(self.body) +
                    FOOTER % self.elements)
        else:
            return (HEADER % self.elements +
                    u''.join(self.body) +
                    FOOTER % self.elements)

    def visit_environment(self, node):
        clatex_sphinx.visit_environment_latex(self, node)
    def depart_environment(self, node):
        clatex_sphinx.depart_environment_latex(self, node)

    def visit_textcolor(self, node):
        clatex_sphinx.visit_textcolor_latex(self, node)
    def depart_textcolor(self, node):
        clatex_sphinx.depart_textcolor_latex(self, node)

    def visit_endpar(self, node):
        clatex_sphinx.visit_endpar_latex(self, node)
    def depart_endpar(self, node):
        clatex_sphinx.depart_endpar_latex(self, node)

    def visit_math(self, node):
        latex_visit_math(self, node)
    def depart_math(self, node):
        pass

    def visit_displaymath(self, node):
        latex_visit_displaymath(self, node)
    def depart_displaymath(self, node):
        pass

    def visit_eqref(self, node):
        latex_visit_eqref(self, node)
    def depart_eqref(self, node):
        pass

    def visit_align(self, node):
        clatex_sphinx.visit_align_latex(self, node)
    def depart_align(self, node):
        clatex_sphinx.depart_align_latex(self, node)

    def visit_ifhtml(self, node):
        pass
    def depart_ifhtml(self, node):
        pass

    def visit_iflatex(self, node):
        pass
    def depart_iflatex(self, node):
        pass
