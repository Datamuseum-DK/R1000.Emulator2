#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x--quick" ] ; then
	cli 'dfs neuter POUND_WCS_ASCENDING.TYP'
	cli 'dfs neuter POUND_WCS_DESCENDING.TYP'
	shift
fi

if [ "x$1" = "x" ] ; then
	set test_typ
fi

sc_boards typ

cli 'sc trace DI*PROC 4'
cli 'sc quota add 23'

expmon_prompt

expmon_cmd "$1"

run
