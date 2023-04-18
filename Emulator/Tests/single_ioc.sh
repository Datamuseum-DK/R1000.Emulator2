#!/bin/sh

. Tests/subr_test.rc

cli 'sc force_reset'

sc_boards ioc

cli 'sc trace ioc_51 1'
cli 'sc trace ioc_52 1'

single ioc $*
