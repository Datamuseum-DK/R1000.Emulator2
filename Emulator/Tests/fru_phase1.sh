#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc quota add 2000'
cli 'sc quota exit'

# 3 => Execute diagnostics
# 2 => Run all tests
# 1 => Please enter maximum test phase (1-3)
fru_prompt 3 2 1

run
