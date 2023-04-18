
all:
	(cd Symbols && python3 build_symbols.py)
	find . -name '[A-Z]*.kicad_sch' -print | \
	    while read fn ; do \
		( \
		    set -e ; \
		    cd `dirname $$fn` ; \
		    pwd ; \
		    kicad-cli sch export netlist `basename $$fn` \
		) ; \
	    done
