
if [ "x$EXPMON_TEST_NAME" = "x" ] ; then
	EXPMON_TEST_NAME=`echo $EXPMON_COMMAND | tr '[A-Z ]' '[a-z_]'`
fi

./r1000sim \
	-T /critter/_r1000 \
	-f Tests/cli_prompt.cli \
	"console > Tests/_expmon_${EXPMON_TEST_NAME}.console" \
	'trace +systemc' \
	"sc launch ${EXPMON_LAUNCH}"\
	"dummy_diproc -TIMEOUT mem1 mem2 mem3" \
	"dummy_diproc ${EXPMON_DUMMY}" \
	'sc trace "DI*PROC" 4' \
	'sc q exit' \
	"sc q ${EXPMON_DURATION}" \
	'console << "x expmon"' \
	'console match expect "EM>"' \
	'console << "[set FIRST_PASS true]"' \
	'console match expect "EM>"' \
	"console << \"${EXPMON_COMMAND}"\" \
	'console match expect "EM>"' \
	'sc rate' \
	'exit' \
	2>&1 | tee Tests/_expmon_${EXPMON_TEST_NAME}.log

(
	cd Context && python3 context.py \
		> ../Tests/_expmon_${EXPMON_TEST_NAME}.context
)

grep 'DI*PROC Exec' /critter/_r1000 | tail -10 \
	> Tests/_expmon_${EXPMON_TEST_NAME}.diproc
