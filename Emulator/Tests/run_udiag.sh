#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'r1000 quota add 50'
cli 'r1000 quota exit'

cli_prompt

cli 'console << "x run_udiag"'
cli 'console match expect "long version [N] ? "'
cli 'console << "n"'
cli 'console match expect "CLI>"'

run

if ! fgrep -a 'the Confidence test (uDIAG) passed' ${R1K_PFX}/_.console ; then
	exit 2
fi
