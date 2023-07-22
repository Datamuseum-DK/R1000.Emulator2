#!/bin/sh

. Tests/subr_test.rc

sc_boards seq

cli sc trace S79TRACE 1

single seq $*
