
# You can override the defaults by creating a Makefile.local
-include Makefile.local

# Where all files will be written
WORKDIR ?= _work

# Which branch of the KiCad schematics to use
BRANCH ?= main

# Where the KiCad netlist files are to be found
NETLISTS ?= ${WORKDIR}/${BRANCH}/*.net

# Copies of https://datamuseum.dk/bits/30000551 and ...552, 1GB each
DISK0_IMAGE ?= ${WORKDIR}/R1K_PAM_Disk_0_Image.BIN
DISK1_IMAGE ?= ${WORKDIR}/R1K_PAM_Disk_1_Image.BIN

# Compiler optimization and debug flags [-O#] [-g]
OPTIMIZE ?= -O2

# You should not need to touch anything below this line
all:	r1000sim

.PHONY: r1000sim

r1000sim:
	@echo "WORKDIR ${WORKDIR}"
	@echo "BRANCH ${BRANCH}"
	-mkdir -p ${WORKDIR} ${WORKDIR}/_obj
	sh cflags.sh ${CC} > ${WORKDIR}/_obj/Makefile.flags
	python3 -u NetList/process_kicad_netlists.py \
		${WORKDIR} \
		${BRANCH} \
		${NETLISTS}
	${MAKE} -f Makefile.sub \
		WORKDIR=${WORKDIR} \
		BRANCH=${BRANCH} \
		OPTIMIZE=${OPTIMIZE} \
		r1000sim

flint:
	${MAKE} -f Makefile.sub \
		WORKDIR=${WORKDIR} \
		BRANCH=${BRANCH} \
		OPTIMIZE=${OPTIMIZE} \
		flint

clean:
	rm -rf ${WORKDIR}/_obj

branch:
	@echo ${BRANCH}

workdir:
	@echo ${WORKDIR}

diskcli:
	@echo "disk mount 0 ${DISK0_IMAGE}"
	@echo "disk mount 1 ${DISK1_IMAGE}"

setup:
	git clone https://github.com/Datamuseum-DK/Musashi
