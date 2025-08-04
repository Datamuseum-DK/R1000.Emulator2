#!/bin/sh

set -e

. Tests/subr_test.rc

if [ "x$1" == "x--background" ] ; then
	BACKGROUND=true
	shift
else
	BACKGROUND=false
fi

if [ "x$1" == "x" ] ; then
	runname=boot
	rundir=${R1K_WORKDIR}/boot
	rm -rf ${rundir}
elif [ -d ${R1K_WORKDIR}/$1 ] ; then
	echo "Run-name (${R1K_WORKDIR}/$1) directory already exists" 1>&2
	exit 1
else
	runname=$1
	rundir=${R1K_WORKDIR}/$1
fi

mkdir -p ${rundir}

sc_boards ioc fiu mem0 seq typ val

cli 'r1000 quota add 10000'
cli 'r1000 quota exit'

cli "console > ${rundir}/_.console"
cli "modem > ${rundir}/_.modem"

cli 'r1000 wait 1e-6'
cli iop reset

cli 'console match expect "Enter option [enter CLI] : "'
cli 'console << "6"'

if $BACKGROUND ; then
	cli 'console match expect "notevermatching"'
	nohup ./r1000sim \
		-T ${rundir}/_ \
		"include ${R1K_CLIFILE}" 2>&1 | tee ${rundir}/_.log \
		2>&1 > _.${runname} &
else
	./r1000sim \
		-T ${rundir}/_ \
		"include ${R1K_CLIFILE}" 2>&1 | tee ${rundir}/_.log
fi
