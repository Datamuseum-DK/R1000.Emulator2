
OBJS += ${OBJDIR}/tables.o
${OBJDIR}/tables.o: Components/tables.c 
	${CC} ${CFLAGS} -c Components/tables.c -o ${OBJDIR}/tables.o
