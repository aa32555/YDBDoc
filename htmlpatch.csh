#!/usr/bin/env -S tcsh -fe

###############################################################
#                                                             #
# Copyright (c) 2018-2023 YottaDB LLC and/or its subsidiaries.#
# All rights reserved.                                        #
#                                                             #
#     This source code contains the intellectual property     #
#     of its copyright holder(s), and is made available       #
#     under a license.  If you do not know the terms of       #
#     the license, please stop and do not read further.       #
#                                                             #
###############################################################

set DIRECTORIES=( \
	AcculturationGuide/ \
	AdminOpsGuide/ \
	MessageRecovery/ \
	MultiLangProgGuide/ \
	ProgGuide/ \
	StyleGuide/ \
	Plugins/ \
)

echo '# Step 1 : Do the following change'
echo '# In files docs.yottadb.com/*/_static/css/theme.css, make the following replacements:'
echo '#'
echo '# monospace,serif -> Inconsolata,Consolas,monospace'
echo '# Lato,proxima-nova,Helvetica Neue,Arial,sans-serif -> FiraGO,Tahoma,sans-serif'
echo '# Roboto Slab,ff-tisa-web-pro,Georgia,Arial,sans-serif -> Lora,Georgia,serif'
echo '# SFMono-Regular,Menlo,Monaco,Consolas,Liberation Mono,Courier New,Courier,monospace -> Inconsolata,Consolas,monospace'
echo ''
echo '# Step 2 : Make the following changes to the theme.css file:'
echo '#'
echo '# Change the colors on the admonition and fonts '
echo ''
echo '# Step 3 : Make the following change in the index.html files under docs.yottadb.com:'
echo '# After the line that contains: <script src="_static/js/theme.js"></script>'
echo '# Add the lines:'
echo '# <script type="text/javascript" src="_static/searchtools.js"></script>'
echo '# <script type="text/javascript" src="searchindex.js"></script>'
echo ''
echo '# Step 4 : Make the following change in the search.html files under docs.yottadb.com:'
echo '# After the line that contains: <script src="_static/js/theme.js"></script>'
echo '# Add the line:'
echo '# <script type="text/javascript" src="_static/language_data.js"></script>'
echo ''
echo '# Step 5 : Make the following change in the all .html files under docs.yottadb.com:'
echo '# After the line that contains: <div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="Navigation menu">'
echo '# Add the line:'
echo '# <img referrerpolicy="no-referrer-when-downgrade" src="https://download.yottadb.com/yottadb-pixel.png" />'

foreach d ($DIRECTORIES)
	pushd $d > /dev/null

	# Step 1
	set filelist = `ls -1 _build/html/_static/css/theme.css`
	set from = 'monospace,serif'
	set to   = 'Inconsolata,Consolas,monospace'
	perl -p -i -e "s/$from/$to/g" $filelist
	set from = 'Lato,proxima-nova,Helvetica Neue,Arial,sans-serif'
	set to   = 'FiraGO,Tahoma,sans-serif'
	perl -p -i -e "s/$from/$to/g" $filelist
	set from = 'Roboto Slab,ff-tisa-web-pro,Georgia,Arial,sans-serif'
	set to   = 'Lora,Georgia,serif'
	perl -p -i -e "s/$from/$to/g" $filelist
	set from = 'SFMono-Regular,Menlo,Monaco,Consolas,Liberation Mono,Courier New,Courier,monospace'
	set to   = 'Inconsolata,Consolas,monospace'
	perl -p -i -e "s/$from/$to/g" $filelist

	# Step 2
	set filelist = `ls -1 _build/html/_static/css/theme.css`
	set from1 = 'background:#6ab0de'
	set to1 = 'background:#3b1a68'
	perl -p -i -e "s/$from1/$to1/g" $filelist
	set from2 = 'e7f2fa'
	set to2 = 'e0d1f3'
	perl -p -i -e "s/$from2/$to2/g" $filelist

	# Step 3
	set filelist = `ls -1 _build/html/index.html`
	set from = '<script src="_static/js/theme.js"></script>'
	set to1 = '<script type="text/javascript" src="_static/searchtools.js"></script>'
	set to2 = '<script type="text/javascript" src="searchindex.js"></script>'
	set to = "$from${to1}${to2}"
	perl -p -i -e "s|$from|$to|g" $filelist

	# Step 4
	set filelist = `ls -1 _build/html/search.html`
	set from = '<script src="_static/js/theme.js"></script>'
	set to1 = '<script type="text/javascript" src="_static/language_data.js"></script>'
	set to = "$from${to1}"
	perl -p -i -e "s|$from|$to|g" $filelist

	# Step 5
	set filelist = `find _build/html/ -name '*.html'`
	set from = '<div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="Navigation menu">'
	set to1 = '<img referrerpolicy="no-referrer-when-downgrade" src="https://download.yottadb.com/yottadb-pixel.png" />'
	set to = "$from${to1}"
	perl -p -i -e "s|$from|$to|g" $filelist

	popd > /dev/null
end
