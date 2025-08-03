

OBJS    += ${OBJDIR}/diagbus.o
${OBJDIR}/diagbus.o: \
    Diag/diagbus.c \
    Infra/elastic.h \
    Infra/vend.h \
    Infra/vsb.h \
    Diag/diag.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Diag/diagbus.c -o ${OBJDIR}/diagbus.o

OBJS    += ${OBJDIR}/diproc_turbo_fiu.o
${OBJDIR}/diproc_turbo_fiu.o: \
    Diag/diproc_turbo_fiu.c \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    Chassis/r1000_arch.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_fiu.c -o ${OBJDIR}/diproc_turbo_fiu.o

OBJS    += ${OBJDIR}/diproc_turbo_ioc.o
${OBJDIR}/diproc_turbo_ioc.o: \
    Diag/diproc_turbo_ioc.c \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    Chassis/r1000_arch.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_ioc.c -o ${OBJDIR}/diproc_turbo_ioc.o

OBJS    += ${OBJDIR}/diproc_turbo_mem32.o
${OBJDIR}/diproc_turbo_mem32.o: \
    Diag/diproc_turbo_mem32.c \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_mem32.c -o ${OBJDIR}/diproc_turbo_mem32.o

OBJS    += ${OBJDIR}/diproc_turbo_seq.o
${OBJDIR}/diproc_turbo_seq.o: \
    Diag/diproc_turbo_seq.c \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    Chassis/r1000_arch.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_seq.c -o ${OBJDIR}/diproc_turbo_seq.o

OBJS    += ${OBJDIR}/diproc_turbo_tv.o
${OBJDIR}/diproc_turbo_tv.o: \
    Diag/diproc_turbo_tv.c \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_tv.c -o ${OBJDIR}/diproc_turbo_tv.o

OBJS    += ${OBJDIR}/dummy_diproc.o
${OBJDIR}/dummy_diproc.o: \
    Diag/dummy_diproc.c \
    Infra/vsb.h \
    Infra/elastic.h \
    Diag/diagproc.h \
    Diag/diag.h \
    Chassis/r1000_arch.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Diag/dummy_diproc.c -o ${OBJDIR}/dummy_diproc.o
