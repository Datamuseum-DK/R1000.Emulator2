
OBJS += ${OBJDIR}/sc.o
${OBJDIR}/sc.o: \
    Chassis/sc.c \
    Infra/r1000.h \
    Infra/vqueue.h \
    Chassis/r1000sc.h \
    Chassis/r1000sc_priv.h
	${CC} ${CFLAGS} -c Chassis/sc.c -o ${OBJDIR}/sc.o

OBJS += ${OBJDIR}/sc_main_thread.o
${OBJDIR}/sc_main_thread.o: \
    Chassis/sc_main_thread.cc \
    Chassis/r1000sc.h \
    Chassis/r1000sc_priv.h \
    ${WORKDIR}/Chassis/planes.hh \
    ${WORKDIR}/Emu/emu_pub.hh \
    ${WORKDIR}/Fiu/fiu_pub.hh \
    ${WORKDIR}/Ioc/ioc_pub.hh \
    ${WORKDIR}/Mem32/mem32_pub.hh \
    ${WORKDIR}/Seq/seq_pub.hh \
    ${WORKDIR}/Typ/typ_pub.hh \
    ${WORKDIR}/Val/val_pub.hh 
	${SC_CC} \
		-I${WORKDIR}/Emu/ \
		-I${WORKDIR}/Fiu/ \
		-I${WORKDIR}/Ioc/ \
		-I${WORKDIR}/Mem32/ \
		-I${WORKDIR}/Seq/ \
		-I${WORKDIR}/Typ/ \
		-I${WORKDIR}/Val/ \
		-I${WORKDIR}/Chassis/ \
		-o ${OBJDIR}/sc_main_thread.o \
		Chassis/sc_main_thread.cc

OBJS += ${OBJDIR}/sc_watchdog.o
${OBJDIR}/sc_watchdog.o: \
    Chassis/sc_watchdog.c \
    Infra/r1000.h \
    Infra/context.h \
    Diag/diagproc.h \
    Chassis/r1000sc_priv.h
	${CC} ${CFLAGS} -c Chassis/sc_watchdog.c -o ${OBJDIR}/sc_watchdog.o

