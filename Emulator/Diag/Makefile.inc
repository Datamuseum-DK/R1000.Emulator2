

OBJS    += ${OBJDIR}/diagbus.o
${OBJDIR}/diagbus.o: \
    Diag/diagbus.c \
    Infra/elastic.h \
    Infra/vend.h \
    Infra/vsb.h \
    Diag/diag.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Diag/diagbus.c -o ${OBJDIR}/diagbus.o

OBJS    += ${OBJDIR}/diagproc.o
${OBJDIR}/diagproc.o: \
    Diag/diagproc.c \
    Chassis/r1000sc.h \
    Diag/diagproc.h \
    Diag/i8052_emul.h \
    Infra/elastic.h \
    Infra/vsb.h \
    Diag/diag.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Diag/diagproc.c -o ${OBJDIR}/diagproc.o

OBJS    += ${OBJDIR}/diproc_turbo_fiu.o
${OBJDIR}/diproc_turbo_fiu.o: \
    Diag/diproc_turbo_fiu.c \
    Chassis/r1000sc.h \
    ${WORKDIR}/Chassis/z_codes.h \
    Diag/diag.h \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_fiu.c -o ${OBJDIR}/diproc_turbo_fiu.o

OBJS    += ${OBJDIR}/diproc_turbo_ioc.o
${OBJDIR}/diproc_turbo_ioc.o: \
    Diag/diproc_turbo_ioc.c \
    Chassis/r1000sc.h \
    ${WORKDIR}/Chassis/z_codes.h \
    Diag/diag.h \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_ioc.c -o ${OBJDIR}/diproc_turbo_ioc.o

OBJS    += ${OBJDIR}/diproc_turbo_mem32.o
${OBJDIR}/diproc_turbo_mem32.o: \
    Diag/diproc_turbo_mem32.c \
    Chassis/r1000sc.h \
    ${WORKDIR}/Chassis/z_codes.h \
    Diag/diag.h \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_mem32.c -o ${OBJDIR}/diproc_turbo_mem32.o

OBJS    += ${OBJDIR}/diproc_turbo_seq.o
${OBJDIR}/diproc_turbo_seq.o: \
    Diag/diproc_turbo_seq.c \
    Chassis/r1000sc.h \
    ${WORKDIR}/Chassis/z_codes.h \
    Diag/diag.h \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_seq.c -o ${OBJDIR}/diproc_turbo_seq.o

OBJS    += ${OBJDIR}/diproc_turbo_tv.o
${OBJDIR}/diproc_turbo_tv.o: \
    Diag/diproc_turbo_tv.c \
    Chassis/r1000sc.h \
    ${WORKDIR}/Chassis/z_codes.h \
    Diag/diag.h \
    Diag/diagproc.h \
    Diag/exp_hash.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -I${WORKDIR} -c Diag/diproc_turbo_tv.c -o ${OBJDIR}/diproc_turbo_tv.o

OBJS    += ${OBJDIR}/diproc_mods.o
${OBJDIR}/diproc_mods.o: \
    Diag/diproc_mods.c \
    Diag/diag.h
	${CC} ${CFLAGS} -c Diag/diproc_mods.c -o ${OBJDIR}/diproc_mods.o

OBJS    += ${OBJDIR}/dummy_diproc.o
${OBJDIR}/dummy_diproc.o: \
    Diag/dummy_diproc.c \
    Infra/vsb.h \
    Infra/elastic.h \
    Chassis/r1000sc.h \
    Diag/diag.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Diag/dummy_diproc.c -o ${OBJDIR}/dummy_diproc.o

OBJS    += ${OBJDIR}/experiment.o
${OBJDIR}/experiment.o: \
    Diag/experiment.c \
    Infra/elastic.h \
    Infra/vqueue.h \
    Diag/diag.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Diag/experiment.c -o ${OBJDIR}/experiment.o

OBJS    += ${OBJDIR}/i8052_emul.o
${OBJDIR}/i8052_emul.o: \
    Diag/i8052_emul.c \
    Diag/i8052_emul.h
	${CC} ${CFLAGS} -c Diag/i8052_emul.c -o ${OBJDIR}/i8052_emul.o
