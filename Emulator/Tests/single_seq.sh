#!/bin/sh

. Tests/subr_test.rc

sc_boards seq

single seq $*
