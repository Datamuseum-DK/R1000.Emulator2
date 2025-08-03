#!/bin/sh

set -e 

. Tests/subr_test.rc

# cli "trace +ioc_instructions"

sc_boards ioc fiu mem0 seq typ val

cli iop memtrace add resha_misc
cli iop memtrace add scsi_d
cli trace +scsi_cmd
cli trace +scsi_data
cli trace +disk_data
cli trace +ioc_dma

cli console serial /dev/nmdm0B
cli r1000 quota add 100

cli_prompt

run_with_cli
