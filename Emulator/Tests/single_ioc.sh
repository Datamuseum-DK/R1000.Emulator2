#!/bin/sh

. Tests/subr_test.rc

cli 'sc force_reset'

sc_boards ioc

single ioc $*
