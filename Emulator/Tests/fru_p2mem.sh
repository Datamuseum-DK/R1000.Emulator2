#!/bin/sh

. Tests/subr_test.rc

if [ "x$1" = "x--quick" ] ; then
	true
fi

sc_boards ioc fiu mem0 seq typ val

cli 'sc quota add 5'
cli 'sc quota exit'

# 8 => Initialize processor state
# 3 => Execute diagnostics
# 4 => Run a specific test
# 18 => P2MEM
# 7 => Memory 0
fru_prompt 8 3 4 18 7

run
