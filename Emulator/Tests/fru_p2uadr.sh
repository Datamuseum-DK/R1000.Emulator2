#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc quota add 5'
cli 'sc quota exit'

cli 'dfs neuter TEST_WCS_LOCATIONS.TYP'

# 8 => Initialize processor state
# 3 => Execute diagnostics
# 4 => Run a specific test
# 25 => P2UADR
fru_prompt 8 3 4 25

run
