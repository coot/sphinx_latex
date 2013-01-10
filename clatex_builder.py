# -*- coding: utf-8 -*-
"""
    clatex_builder (CustomLaTeXBuilder)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The difference from LaTeXBuilder are:
        not many except:
        - CustomLaTeXWriter is imported from clatex_writer,
        - clatex_sphinx extension is build in.

    LaTeX builder.

    :copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import os
from os import path

from docutils import nodes
from docutils.io import FileOutput
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.parsers.rst import Directive

from sphinx import package_dir
from sphinx import addnodes
from sphinx.util import texescape
from sphinx.locale import _
from sphinx.builders import Builder
from sphinx.environment import NoUri
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.osutil import SEP, copyfile
from sphinx.util.console import bold, darkgreen
from clatex_writer import CustomLaTeXWriter as LaTeXWriter
from sphinx.ext.mathbase import math_role
from sphinx.ext.mathbase import eq_role
from sphinx.ext.mathbase import MathDirective
from sphinx.ext.mathbase import number_equations

import clatex_sphinx

class LaTeXBuilder(Builder):
    """
    Builds LaTeX output to create PDF.
    """
    name = 'clatex' # c from custom
    format = 'latex'
    supported_image_types = ['application/pdf', 'image/png',
                             'image/gif', 'image/jpeg']

    def init(self):
        self.docnames = []
        self.document_data = []
        texescape.init()

    def get_outdated_docs(self):
        return 'all documents' # for now

    def get_target_uri(self, docname, typ=None):
        if docname not in self.docnames:
            raise NoUri
        else:
            return '%' + docname

    def get_relative_uri(self, from_, to, typ=None):
        # ignore source path
        return self.get_target_uri(to, typ)

    def init_document_data(self):
        preliminary_document_data = map(list, self.config.latex_documents)
        if not preliminary_document_data:
            self.warn('no "latex_documents" config value found; no documents '
                      'will be written')
            return
        # assign subdirs to titles
        self.titles = []
        for entry in preliminary_document_data:
            docname = entry[0]
            if docname not in self.env.all_docs:
                self.warn('"latex_documents" config value references unknown '
                          'document %s' % docname)
                continue
            self.document_data.append(entry)
            if docname.endswith(SEP+'index'):
                docname = docname[:-5]
            self.titles.append((docname, entry[2]))

    def write(self, *ignored):
        docwriter = LaTeXWriter(self)
        docsettings = OptionParser(
            defaults=self.env.settings,
            components=(docwriter,)).get_default_values()

        self.init_document_data()

        for entry in self.document_data:
            docname, targetname, title, author, docclass = entry[:5]
            toctree_only = False
            if len(entry) > 5:
                toctree_only = entry[5]
            destination = FileOutput(
                destination_path=path.join(self.outdir, targetname),
                encoding='utf-8')
            self.info("processing " + targetname + "... ", nonl=1)
            doctree = self.assemble_doctree(docname, toctree_only,
                appendices=((docclass != 'howto') and
                            self.config.latex_appendices or []))
            self.post_process_images(doctree)
            self.info("writing... ", nonl=1)
            doctree.settings = docsettings
            doctree.settings.author = author
            doctree.settings.title = title
            doctree.settings.docname = docname
            doctree.settings.docclass = docclass
            docwriter.write(doctree, destination)
            self.info("done")

    def assemble_doctree(self, indexfile, toctree_only, appendices):
        self.docnames = set([indexfile] + appendices)
        self.info(darkgreen(indexfile) + " ", nonl=1)
        tree = self.env.get_doctree(indexfile)
        tree['docname'] = indexfile
        if toctree_only:
            # extract toctree nodes from the tree and put them in a
            # fresh document
            new_tree = new_document('<latex output>')
            new_sect = nodes.section()
            new_sect += nodes.title(u'<Set title in conf.py>',
                                    u'<Set title in conf.py>')
            new_tree += new_sect
            for node in tree.traverse(addnodes.toctree):
                new_sect += node
            tree = new_tree
        largetree = inline_all_toctrees(self, self.docnames, indexfile, tree,
                                        darkgreen)
        largetree['docname'] = indexfile
        for docname in appendices:
            appendix = self.env.get_doctree(docname)
            appendix['docname'] = docname
            largetree.append(appendix)
        self.info()
        self.info("resolving references...")
        self.env.resolve_references(largetree, indexfile, self)
        # resolve :ref:s to distant tex files -- we can't add a cross-reference,
        # but append the document name
        for pendingnode in largetree.traverse(addnodes.pending_xref):
            docname = pendingnode['refdocname']
            sectname = pendingnode['refsectname']
            newnodes = [nodes.emphasis(sectname, sectname)]
            for subdir, title in self.titles:
                if docname.startswith(subdir):
                    newnodes.append(nodes.Text(_(' (in '), _(' (in ')))
                    newnodes.append(nodes.emphasis(title, title))
                    newnodes.append(nodes.Text(')', ')'))
                    break
            else:
                pass
            pendingnode.replace_self(newnodes)
        return largetree

    def finish(self):
        # copy image files
        if self.images:
            self.info(bold('copying images...'), nonl=1)
            for src, dest in self.images.iteritems():
                self.info(' '+src, nonl=1)
                copyfile(path.join(self.srcdir, src),
                         path.join(self.outdir, dest))
            self.info()

        # copy additional files
        if self.config.latex_additional_files:
            self.info(bold('copying additional files...'), nonl=1)
            for filename in self.config.latex_additional_files:
                self.info(' '+filename, nonl=1)
                copyfile(path.join(self.confdir, filename),
                         path.join(self.outdir, path.basename(filename)))
            self.info()

        # the logo is handled differently
        if self.config.latex_logo:
            logobase = path.basename(self.config.latex_logo)
            copyfile(path.join(self.confdir, self.config.latex_logo),
                     path.join(self.outdir, logobase))

        self.info(bold('copying TeX support files... '), nonl=True)
        staticdirname = path.join(package_dir, 'texinputs')
        for filename in os.listdir(staticdirname):
            if not filename.startswith('.'):
                copyfile(path.join(staticdirname, filename),
                         path.join(self.outdir, filename))
        self.info('done')

def setup(app):
    app.add_config_value('clatex_documentclass', '\\documentclass{book}\n', 'env')
    app.add_config_value('clatex_preamble', '', 'env')
    app.add_config_value('clatex_use_chapters', True, 'env')
    app.add_config_value('clatex_begin_doc', '', 'env')
    app.add_config_value('clatex_end_doc', '', 'env')
    app.add_config_value('clatex_highlighter', True, 'env')
    app.add_config_value('clatex_hyperref_args', '', 'env')
    app.add_config_value('clatex_makeidx', False, 'env')
    # clatex_makeidx can be a boolean or a string ('\usepackage{makeidx}\n\makeindex')

    app.add_builder(LaTeXBuilder)

    app.add_role('math', math_role)
    app.add_role('eq', eq_role)
    app.add_directive('math', MathDirective)
    app.connect('doctree-resolved', number_equations)

    clatex_sphinx.setup(app)
