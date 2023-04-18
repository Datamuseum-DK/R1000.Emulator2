#!/bin/sh

. Tests/subr_test.rc

sc_boards seq

cli 'sc trace seq_56 1'

single seq $*
