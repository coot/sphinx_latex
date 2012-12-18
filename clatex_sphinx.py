# -*- coding: utf-8 -*-
"""
Adds environment directives:

.. environment:: Theorem
    :title: Grothendick-Galois Theorem

    Let ...

textcolor directive and a role (roles are not recursive, they ony can  contain
a text, no other nodes, directives are recursive though)

.. textcolor:: #00FF00

        This text is green

:textcolor:`<#FF0000> this text is red`.

.. endpar::

Puts '\n\n' in LaTeX and <br> in html.
(There is no other way to end a paragraph between two environments)
"""
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from docutils import nodes

# environments:

class environment(nodes.Element):
    pass

class EnvironmentDirective(Directive):

    required_arguments = 1
    optional_arguments = 0

    # final_argument_whitespace = True
    # directive arguments are white space separated.

    option_spec = {
                   'class': directives.class_option,
                   'name': directives.unchanged,
                   'title' : directives.unchanged,
                   'html_title' : directives.unchanged,
                   'latex_title' : directives.unchanged,
                   }

    has_content = True

    def run(self):

        self.options['envname'] = self.arguments[0]

        self.assert_has_content()
        environment_node = environment(rawsource='\n'.join(self.content), **self.options)
        self.state.nested_parse(self.content, self.content_offset, environment_node)
        self.add_name(environment_node)
        return [environment_node]

def visit_environment_latex(self, node):
    if 'latex_title' in node:
        # XXX: node['title'] should be parssed (for example there might be math inside)
        self.body.append('\n\\begin{%s}[%s]' % (node['envname'], node['latex_title']))
    elif 'title' in node:
        # XXX: node['title'] should be parssed (for example there might be math inside)
        self.body.append('\n\\begin{%s}[%s]' % (node['envname'], node['title']))
    else:
        self.body.append('\n\\begin{%s}' % (node['envname']))

def depart_environment_latex(self, node):
    self.body.append('\\end{%s}' % node['envname'])

def visit_environment_html(self, node):
    """ This visit method produces the following html:

    The 'theorem' below will be substituted with node['envname'] and title with
    node['title'] (environment node's option),

    <div class='environment theorem'>
        <div class='environment_title theorem_title'>Theorem: title </div>
        <div class='environment_body theorem_body'>
          ...
        </div>
    </div>

    XXX: title doesn't allow for using any math"""
    if 'label' in node:
        ids = [ node['label'] ]
    else:
        ids = []
    self.body.append(self.starttag(node, 'div', CLASS='environment %s' % node['envname'], IDS = ids))
    self.body.append('<div class="environment_title %s_title">' % node['envname'])
    # self.body.append(self.starttag(node, 'div', CLASS=('environment_title %s_title' % node['envname'])))
    if 'html_title' in node:
        self.body.append(node['html_title'])
    if 'title' in node:
        self.body.append(node['title'])
    self.body.append('</div>')
    self.body.append('<div class="environment_body %s_body">' % node['envname'])
    # self.body.append(self.starttag(node, 'div', CLASS=('environment_body %s_body' % node['envname'])))
    self.set_first_last(node)

def depart_environment_html(self, node):
    self.body.append('</div>')
    self.body.append('</div>')

# align:
class align(nodes.Element):
    pass

class AlignDirective(Directive):
    """
    .. align:: center
    .. align:: left
    .. align:: flushleft
    .. align:: right
    .. align:: flushright
    """

    required_arguments = 1
    optional_arguments = 0

    has_content = True

    def run(self):

        if self.arguments[0] in ('left', 'flushleft'):
            align_type = 'fresh-left'
        elif self.arguments[0] in ('right', 'flushright'):
            align_type = 'fresh-right'
        else:
            align_type = 'fresh-center'
        self.options['align_type'] = align_type
        self.options['classes'] = directives.class_option(align_type)


        self.assert_has_content()
        align_node = align(rawsource='\n'.join(self.content), **self.options)
        # print("DEBUG align_node.attributes=%s" % align_node.attributes)
        self.state.nested_parse(self.content, self.content_offset, align_node)
        for node in align_node:
            node['classes'].extend(directives.class_option(align_type))
            print("DEBUG 0: %s" % node['classes'])
            if ('center' not in node['classes'] and
                    'flushleft' not in node['classes'] and
                    'flushright' not in node['classes'] ):
                node['classes'].extend(directives.class_option(align_type))
                print("DEBUG X:%s" % node)
            else:
                print("DEBUG Y:%s" % node)
        return [align_node]

def visit_align_latex(self, node):
    self.body.append('\n\\begin{%s}' % node['align_type'])

def depart_align_latex(self, node):
    self.body.append('\\end{%s}' % node['align_type'])

def visit_align_html(self, node):
    # XXX: to be implemented.
    pass

def depart_align_html(self, node):
    # XXX: to be implemented.
    pass

# textcolor:

class TextColorDirective(Directive):

    required_arguments = 1
    optional_arguments = 0

    has_content = True

    def run(self):

        self.assert_has_content()
        textcolor_node = textcolor(rawsource='\n'.join(self.content), **self.options)
        textcolor_node['color_spec'] = self.arguments[0]
        self.state.nested_parse(self.content, self.content_offset, textcolor_node)
        self.add_name(textcolor_node)
        return [textcolor_node]

class textcolor(nodes.Element):
    pass

def textcolor_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """ This role is interpreted in the following way:
        :color:`<color_spec> text `
        where color spec is in HTML model, e.g. #FFFFFF, ...
        in latex:
        \\textcolor[HTML]{color_spec}{text}
        (the leading # is removed from color_spec)
        in html
        <font color="color_spec">text</font>
    """
    color_spec = text[1:text.index('>')]
    text = (text[text.index('>')+1:]).strip()
    textcolor_node = textcolor()
    textcolor_node.children.append(nodes.Text(text))
    textcolor_node['color_spec'] = color_spec

    return [textcolor_node], []

def visit_textcolor_html(self, node):
    self.body.append('<font color="%s">' % node['color_spec'])

def depart_textcolor_html(self, node):
    self.body.append('</font>')

def visit_textcolor_latex(self, node):
    color_spec = node['color_spec'][1:]
    self.body.append('\n\\textcolor[HTML]{%s}{' % color_spec)

def depart_textcolor_latex(self, node):
    self.body.append('}')

# endpar:

class endpar(nodes.Element):
    pass

class EndParDirective(Directive):

    required_arguments = 0
    optional_arguments = 0

    has_content = False

    def run(self):
        return [endpar()]

def visit_endpar_latex(self, node):
    self.body.append('\n\n')

def depart_endpar_latex(self, node):
    pass

def visit_endpar_html(self, node):
    self.body.append('\n<br>\n')

def depart_endpar_html(self, node):
    pass

# setup:

def setup(app):

    # app.add_directive('begin', EnvironmentDirective)
    # app.add_node(environment,
                # html = (visit_environment_html, depart_environment_html),
                # latex = (visit_environment_latex, depart_environment_latex),
            # )

    app.add_directive('environment', EnvironmentDirective)
    app.add_node(environment,
                html = (visit_environment_html, depart_environment_html),
                latex = (visit_environment_latex, depart_environment_latex),
            )

    app.add_directive('align', AlignDirective)
    app.add_node(align,
                html =  (visit_align_html, depart_align_html),
                latex = (visit_align_latex, depart_align_latex),
            )

    app.add_directive('textcolor', TextColorDirective)
    app.add_role('textcolor', textcolor_role)
    app.add_node(textcolor,
            html = (visit_textcolor_html, depart_textcolor_html),
            latex = (visit_textcolor_latex, depart_textcolor_latex)
            )

    app.add_directive('endpar', EndParDirective)
    app.add_node(endpar,
            html = (visit_endpar_html, depart_endpar_html),
            latex = (visit_endpar_latex, depart_endpar_latex)
            )
