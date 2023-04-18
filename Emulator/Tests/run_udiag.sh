#!/bin/sh

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

cli 'sc trace DI*PROC 4'
cli 'sc quota add 50'
cli 'sc quota exit'

cli_prompt

cli 'console << "x run_udiag"'
cli 'console match expect "long version [N] ? "'
cli 'console << "n"'
cli 'console match expect "CLI>"'

run
