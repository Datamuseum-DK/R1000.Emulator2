#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x--quick" ] ; then
	shift
fi

if [ "x$1" = "x" ] ; then
        set test_fiu
fi

sc_boards fiu seq

cli 'sc trace DI*PROC 4'
cli 'sc quota add 27'

expmon_prompt

expmon_cmd "$1"

run
