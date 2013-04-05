Custom LaTeX and HTML builders for Sphinx - Python documentation tool
=====================================================================

This is code contains LaTeX and HTML buidlers for Sphinx - the Python default
documentation tool which uses the ReStructuredText (RST) file format.  It
allows for custom build LaTeX documents: you can define your own LaTeX
preambule, e.g.  use whatever class you would like to use (for example the
memoir class).  Also adds a few LaTeX type directives (align, theorem, definition,
etc)

Installation
------------

To install the extension follow the standar
[way](http://sphinx-doc.org/extensions.html), i.e. put the python files
somewher in your $PYTHONPATH and add "clatex_builder" to `extensions` list in
your conf.py file.

theorems and newtheorem function
--------------------------------

Furthermore it allows you to define LaTeX like environments and use them in
the rst source files.  There are predefined directives:

```
.. theorem::

.. proposition::

.. definition::

.. lemma::

.. example::

.. exercise::
```

The directives work in a very similar way to the corresponding LaTeX
environment: they all are nummbered.  You can define your own environment.
For that you need to add your own [extension to
Sphinx](http://sphinx-doc.org/extensions.html) and add the following code to
the `setup` function:

```
def setup(app)

    newtheorem(app, 'theorem', 'Theorem', 'theorem')

```

the `newtheorem()` function works in a very similar way to the LaTeX
\newtheorem{}{}{} command.  That means that the above code will define a `..
theorem::` directive, which will use `Theorem` as the environment name and the
directives will be numbered like `theorem` (the third argument).  For example
if you add also

```
    newtheorem(app, 'definition', 'Definition', 'theorem')
```

all the definition directives will be counted together with theorem
directives.  There is currently no way to bind the numbering with the section
numbers (like Definition 1.1, 1.2 in the first chapter; 2.1, 2.2, ... etc in
the second one) - but I have started working on this and I have an idea how to
implement it - though it requires some effort.


The syntax for the directive is very similar to

```
\begin{theorem}[title]
    ...
\end{theorem}
```
the equivalent useage of theorem directive is:

```
.. theorem:: title

    ...
```

environment directive
---------------------

Furthermore, there is an environment directive which allows for more
sofisticated constructions:

```
.. environment::
    :class: ENV_CLASS
    :name: Definition
    :html_title: title used by html builder
    :latex_title: title used by latex builder

	...
```
You can also use `:title:` which if both `:html_title:` and `:latex_title:`
are ought to be the same.  This directive will probably be changed in future
releases.

textcolor role
--------------

You can also change the color with the `:textcolor:` role:

```
:textcolor:`<color_spec> colored text`
```
The color_spec is an HTML color model, e.g. #ffffff for white, #00ff00 for
green, etc.  The LaTeX builder is useing \textcolor[HTML]{color_spec}{colored
text} (with the `#` removed from `color_spec`).  The HTML builder is using

```
<font color="color_spec">colored text</font>
```
to change the font color.

endpar directive
----------------

the ``.. endpar::`` directive will input </br> into HTML and an empty line
into LaTeX source file - which ends a paragraph in LaTeX.


align directive
---------------

There is also align directive which aligns the code:

```
.. align:: center

    Centered text

.. align:: flushleft

    Left aligned text

.. align:: flushright

    Right aligned text
```
You can also use 'left' and 'right' instead of 'flushleft' and 'flushright'.
