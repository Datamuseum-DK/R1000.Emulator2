

OBJS    += ${OBJDIR}/diagbus.o
${OBJDIR}/diagbus.o: \
    Diag/diagbus.c \
    Infra/elastic.h \
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

OBJS    += ${OBJDIR}/diproc_exp.o
${OBJDIR}/diproc_exp.o: \
    Diag/diproc_exp.c \
    Diag/diag.h \
    Diag/diproc_fiu_wcs.h \
    Diag/diproc_seq_dec.h \
    Diag/diproc_seq_wcs.h \
    Diag/diproc_typ_wcs.h \
    Diag/diproc_val_wcs.h \
    Chassis/r1000sc.h \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Diag/diproc_exp.c -o ${OBJDIR}/diproc_exp.o


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
