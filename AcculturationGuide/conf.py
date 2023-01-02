#################################################################
#                                                               #
# Copyright (c) 2017-2022 YottaDB LLC and/or its subsidiaries.  #
# All rights reserved.                                          #
#                                                               #
#       This source code contains the intellectual property     #
#       of its copyright holder(s), and is made available       #
#       under a license.  If you do not know the terms of       #
#       the license, please stop and do not read further.       #
#                                                               #
#################################################################
# -*- coding: utf-8 -*-
#
# YottaDBDoc documentation build configuration file, created by
# sphinx-quickstart on Fri Nov 17 11:33:19 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sphinx_rtd_theme

# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",
    "sphinxprettysearchresults",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = u"Acculturation"
copyright = u"2017-2022, YottaDB LLC"
author = u"YottaDB Team"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
#version = u"1.34"
# The full version, including alpha/beta/rc tags.
release = u""

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_css_files = ["css/custom.css"]
html_show_sourcelink = False

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {'stickysidebar':'true','sidebarwidth':'330','sidebartextcolor':'#3b1a68','sidebarbgcolor':'#f3f3f3','relbarbgcolor':'#3b1a68','footerbgcolor':'#3b1a68', 'sidebarlinkcolor':'#3b1a68','bodyfont':'Raleway','headfont':'Lora'}
html_theme_options = {
    "sticky_navigation": "true",
    "prev_next_buttons_location": "both",
    "logo_only": True,
}
html_logo = "logo.png"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "**": [
        "relations.html",  # needs 'show_related': True theme option to display
        "globaltoc.html",
        "searchbox.html"
    ]
}

#################################################################################
#                  RELEASE SPECIFIC DOCUMENTATION
#################################################################################

# html_context is used to supply values to templates (under _templates).
# The current release and all the git tags values will be supplied using html_context.

try:
   html_context
except NameError:
   html_context = dict()

from git import Repo
repo = Repo( search_parent_directories=True )

# Creating a list to store all the releases
html_context['releases'] = list()

# Fetching the tags in reverse sorted order (most recent first)
# Only interested in tags from d1.34 onwards
tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)[7:]
latest_tag = tags[-1]

# Setting html_context['curr_rel'] value depending on whether current commit has a tag associated to it or not.
# If the latest commit has a tag associated to it, it means documentation has not yet diverged from latest release.
# In this case the curr_rel is "rn.nn (current)", else it is just "current"
curr_commit_sha = repo.head.object
latest_tag_sha = latest_tag.commit
if curr_commit_sha == latest_tag_sha:
   html_context['curr_rel'] = str(latest_tag).replace("d", "r") + " (current)"
else:
   html_context['curr_rel'] = "current"

# Populate the releases list
html_context['releases'].append((html_context['curr_rel'], "current/AcculturationGuide/"))
for tag in tags:
   current_tag = str(tag).replace("d","r")
   html_context['releases'].append((current_tag, current_tag.replace(".","")+"/AcculturationGuide/"))

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "YottaDBDocdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    "preamble": "",
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
    "extraclassoptions": ",openany,oneside",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "YottaDBDoc.tex",
        u"YottaDB Documentation",
        u"YottaDB Team",
        "manual",
    ),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "yottadbdoc", u"YottaDB Documentation", [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "YottaDBDoc",
        u"YottaDBDoc Documentation",
        author,
        "YottaDBDoc",
        "YottaDB Acculturation Guide",
        "Miscellaneous",
    ),
]


# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]
