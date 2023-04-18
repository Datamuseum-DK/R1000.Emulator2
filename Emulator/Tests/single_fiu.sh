#!/bin/sh

. Tests/subr_test.rc

sc_boards fiu

single fiu $*
