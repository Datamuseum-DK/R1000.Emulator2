#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc quota add 2000'
cli 'sc quota exit'

# 8 => Initialize processor state
# 3 => Execute diagnostics
# 4 => Run a specific test
# 1 => P1DCOMM
fru_prompt 8 3 4 1 1

run

