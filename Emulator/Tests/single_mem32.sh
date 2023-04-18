#!/bin/sh

. Tests/subr_test.rc

sc_boards mem0

cli 'sc trace mem32_33.DFSM 1'
#cli 'dfs patch LOAD_CONFIG.M32 0x3c 0x30 0x32'

single mem0 $*
