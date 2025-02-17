#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc quota add 11'
cli 'sc quota exit'

# 3 => Execute diagnostics
# 4 => Run a specific test
# 29 => P3UCODE
# 1 => All
fru_prompt 3 4 29 1

run

if ! fgrep -a 'P3UCODE passed' ${R1K_PFX}/_.console ; then
	exit 2
fi
