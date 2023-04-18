OBJS    += ${OBJDIR}/dfs.o
${OBJDIR}/dfs.o: \
    Dfs/dfs.c \
    Infra/vend.h \
    Iop/iop_scsi.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Dfs/dfs.c -o ${OBJDIR}/dfs.o

