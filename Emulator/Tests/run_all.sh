#!/bin/sh

set -e

make 

rm -f Tests/_*

if [ "x$1" != "x" ] ; then
	TS="${1}"
else
	TS=`date +%Y%m%d%H%M`
fi

for tst in \
	Tests/expmon_reset_all.sh \
	Tests/test_novram.sh \
	Tests/fru_phase3.sh
do
	sh $tst || ( [ $? == 9 ] && sh $tst ) || true
done

mkdir -p Tests/Results/$TS
mv Tests/_* Tests/Results/$TS
cd Tests/Results/$TS && python3 ../../testsumm.py > summary.txt
