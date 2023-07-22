#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x--quick" ] ; then
	shift
fi

if [ "x$1" = "x" ] ; then
        set test_seq
fi

sc_boards seq fiu

# cli sc trace S79TRACE 1

cli 'sc quota add 20'
# cli 'dfs sed TEST_SEQ.EM /seq_wcs_tests/d'

expmon_prompt

expmon_cmd "$1"

run
