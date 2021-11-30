#!/usr/bin/env -S tcsh -fe

###############################################################
#                                                             #
# Copyright (c) 2018-2021 YottaDB LLC and/or its subsidiaries.#
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
	ReleaseNotes/ \
	StyleGuide/ \
	Plugins/ \
)

foreach d ($DIRECTORIES)
	pushd $d > /dev/null

	set filelist = `ls -1 -p | grep -v /`
	# set curr_year = `date +%Y`
	set curr_year = '2022'
	set from = '2021 YottaDB LLC and\/or its'
	set to = $curr_year' YottaDB LLC and\/or its'
	echo $to
	perl -p -i -e "s/$from/$to/g" $filelist

	popd > /dev/null
end
