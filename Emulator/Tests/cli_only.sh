#!/bin/sh

set -e 

. Tests/subr_test.rc

# cli "trace +ioc_instructions"

sc_boards ioc fiu mem0 seq typ val

#cli iop memtrace add io_sreg8
#cli iop memtrace add scsi_d
cli trace +scsi_cmd
#cli trace +scsi_data
cli trace +tape_data
#cli trace +ioc_dma

cli r1000 quota add 100


start_r1000

# cli_prompt

run_with_cli
