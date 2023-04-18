#!/bin/sh

if $1 --version | grep -q clang ; then
	echo "PARANOIA += -Qunused-arguments"
	echo "PARANOIA += -Wno-unknown-warning-option"
	echo "PARANOIA += -Wno-format-zero-length"
	echo "PARANOIA += -fstack-protector-strong -Wsystem-headers -Werror -Wall"
	echo "PARANOIA += -Wno-format-y2k -W -Wno-unused-parameter -Wstrict-prototypes"
	echo "PARANOIA += -Wmissing-prototypes -Wpointer-arith -Wreturn-type -Wcast-qual"
	echo "PARANOIA += -Wwrite-strings -Wswitch -Wshadow -Wunused-parameter"
	echo "PARANOIA += -Wcast-align"
	echo "PARANOIA += -Wchar-subscripts -Winline -Wnested-externs -Wredundant-decls"
	echo "PARANOIA += -Wold-style-definition -Wno-pointer-sign"
	echo "PARANOIA += -Wmissing-variable-declarations -Wthread-safety -Wno-empty-body"
	echo "PARANOIA += -Wno-string-plus-int"
	echo "PARANOIA += -Wno-missing-field-initializers"
	echo "PARANOIA += -Wno-unused-but-set-variable"

	echo "PARANOIA += -Wno-format-zero-length"
	echo "PARANOIA += -Wno-unused-const-variable"
	echo "PARANOIA += -Wno-nullability-completeness"
	echo "PARANOIA += -Wno-expansion-to-defined"

	echo "PARANOIAXX += -Wno-cast-qual"
	echo "PARANOIAXX += -Wno-cast-align"
	echo "PARANOIAXX += -Wno-unused-parameter"
fi


exit 0
