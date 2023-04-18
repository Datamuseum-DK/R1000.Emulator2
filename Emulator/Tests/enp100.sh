#!/bin/sh

set -e 

. Tests/subr_test.rc

cli console serial /dev/nmdm0B

#cli iop memtrace add resha_misc
#cli iop memtrace add 0x9303e008 0x9303e00e
#cli iop memtrace add 0x9303e102 0x9303e104

echo "10.1.2.3" > /tmp/_enp100_ip
cli dfs write /tmp/_enp100_ip TCP_IP_HOST_ID
# cli dfs cat TCP_IP_HOST_ID

cli_prompt

cli 'console << "x enp100"'
cli 'console match expect "ENP100>"'

cli 'console << "help"'
cli 'console match expect "RAM_BASE=H, SA=H, TDB_COUNT, V, VID=D, WORD"'
cli 'console match expect "ENP100>"'

cli 'console << "show_addrs"'
cli 'console match expect "ENP100>"'

cli 'console << "test_ram"'
cli 'console match expect "ENP100>"'

# If IP# >= 128.0.0.0 you will need this:
# See: https://datamuseum.dk/wiki/Rational/R1000s400/Logbook#2022-09-08_A_really_obscure_bug
#cli 'trace +ioc_instructions'
#cli iop breakpoint 0x2947a regs

cli 'console << "download"'
cli 'console match expect "ENP100>"'
cli 'exit'


./r1000sim \
		-T ${R1K_WORKDIR}/_r1000 \
		"include ${R1K_CLIFILE}" 2>&1 | tee ${R1K_PFX}.log
