#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x--quick" ] ; then
	shift
fi

if [ "x$1" = "x" ] ; then
        set "test_mem32 0 0"
fi

sc_boards mem0

cli 'sc quota add 280'

expmon_prompt

expmon_cmd "[set BOARD_NUM 0]$1"

run
