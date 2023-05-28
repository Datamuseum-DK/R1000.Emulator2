#!/bin/sh

. Tests/subr_test.rc

sc_boards fiu ioc mem0 seq typ val

cli 'sc quota add 1'

expmon_prompt

expmon_cmd reset_all

run
