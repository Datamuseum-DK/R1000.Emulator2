
OBJS += ${OBJDIR}/r1000_thread.o
${OBJDIR}/r1000_thread.o: \
    Chassis/r1000_thread.c \
    Infra/r1000.h \
    Chassis/r1000_arch.h
	${CC} ${CFLAGS} -c Chassis/r1000_thread.c -o ${OBJDIR}/r1000_thread.o

OBJS += ${OBJDIR}/r1000_arch.o
${OBJDIR}/r1000_arch.o: \
    Chassis/r1000_arch.c \
    Chassis/r1000_arch.h \
    Infra/r1000.h \
    Infra/context.h \
    Infra/vend.h \
    Infra/cache_line.h \
    Iop/iop_sc_68k20.hh
	${CC} ${CFLAGS} -c Chassis/r1000_arch.c -o ${OBJDIR}/r1000_arch.o
