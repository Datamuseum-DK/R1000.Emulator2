#!/bin/sh
#
# Run FRU phase 3 for SEQ

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc trace DI*PROC 4'
cli 'sc quota add 35'
cli 'sc quota exit'

# 3 => Execute diagnostics
# 3 => Run all tests applicable to a given FRU (board)
# 4 => SEQuencer
# 3 => Please enter maximum test phase (1-3)
fru_prompt 3 3 4 3

run
