#!/bin/sh

. Tests/subr_test.rc

sc_boards fiu

cli sc trace fiu_57 1

single fiu $*
