#!/bin/sh

. Tests/subr_test.rc

sc_boards val

cli 'sc trace WDR 1'
cli 'sc trace [.][AB]RAM 1'

single val $*
