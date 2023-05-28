#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x--quick" ] ; then
	cli 'dfs neuter TEST_WCS_BITS.IOC'
	cli 'dfs neuter TEST_WCS_ADDRESSING.IOC'
	shift
fi

if [ "x$1" = "x" ] ; then
        set test_ioc
fi

sc_boards ioc

cli 'sc quota add 13'

expmon_prompt

expmon_cmd "$1"

run
