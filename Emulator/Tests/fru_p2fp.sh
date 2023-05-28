#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc quota add 5'
cli 'sc quota exit'

# 8 => Initialize processor state
# 3 => Execute diagnostics
# 4 => Run a specific test
# 15 => P2FP
fru_prompt 3 4 15

run
