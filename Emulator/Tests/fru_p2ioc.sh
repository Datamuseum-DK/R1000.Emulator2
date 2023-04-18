#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x-quick" ] ; then
	cli 'dfs neuter TEST_WCS_BITS.IOC'
	cli 'dfs neuter TEST_WCS_ADDRESSING.IOC'
	cli 'dfs neuter TEST_TRACE_DATA.IOC'
	cli 'dfs neuter TEST_TRACE_ADDRESSING.IOC'
	cli 'dfs neuter TEST_TRACE_BITS.IOC'
fi

sc_boards ioc fiu mem0 seq typ val

cli 'sc trace DI*PROC 4'
cli 'sc quota add 5'
cli 'sc quota exit'

# 8 => Initialize processor state
# 3 => Execute diagnostics
# 4 => Run a specific test
# 17 => P2IOC
fru_prompt 8 3 4 17

run
