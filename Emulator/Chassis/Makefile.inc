
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
    Chassis/r1000sc_priv.h
	${SC_CC} \
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


OBJS += ${OBJDIR}/r1000_arch.o
${OBJDIR}/r1000_arch.o: \
    Chassis/r1000_arch.cc \
    Chassis/r1000_arch.hh \
    Chassis/r1000sc.h \
    Infra/r1000.h \
    Infra/context.h \
    Infra/vend.h \
    Infra/cache_line.h \
    Iop/iop_sc_68k20.hh \
    Diag/diagproc.h \
    Chassis/r1000sc_priv.h
	${SC_CC} -c Chassis/r1000_arch.cc -o ${OBJDIR}/r1000_arch.o

