#!/bin/sh

set -e 

. Tests/subr_test.rc

# cli "trace +ioc_instructions"
sc_boards ioc

cli console serial /dev/nmdm0B
cli sc quota add 100

cli_prompt

run_with_cli
