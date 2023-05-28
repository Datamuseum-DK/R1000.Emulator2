#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x--quick" ] ; then
	cli 'dfs neuter POUND_WCS_ASCENDING.VAL'
	cli 'dfs neuter POUND_WCS_DESCENDING.VAL'
	shift
fi

if [ "x$1" = "x" ] ; then
	set test_val
fi

sc_boards val

cli 'sc quota add 12'

expmon_prompt

expmon_cmd "$1"

run
