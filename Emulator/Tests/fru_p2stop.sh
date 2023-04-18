#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc quota add 2000'

# 8 => Initialize processor state
# 3 => Execute diagnostics
# 4 => Run a specific test
# 22 => P2STOP
fru_prompt 8 3 4 22

run

