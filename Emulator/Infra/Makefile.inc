CFLAGS += -g

OBJS += ${OBJDIR}/cache_line.o
${OBJDIR}/cache_line.o: \
    Infra/cache_line.c \
    Infra/cache_line.h
	${CC} ${CFLAGS} -c Infra/cache_line.c -o ${OBJDIR}/cache_line.o

OBJS += ${OBJDIR}/callout.o
${OBJDIR}/callout.o: \
    Infra/callout.c \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/callout.c -o ${OBJDIR}/callout.o

OBJS += ${OBJDIR}/cli.o
${OBJDIR}/cli.o: \
    Infra/cli.c \
    Infra/vav.h \
    Iop/iop.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/cli.c -o ${OBJDIR}/cli.o

OBJS += ${OBJDIR}/context.o
${OBJDIR}/context.o: \
    Infra/context.c \
    Infra/context.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/context.c -o ${OBJDIR}/context.o

OBJS += ${OBJDIR}/elastic.o
${OBJDIR}/elastic.o: \
    Infra/elastic.c \
    Infra/elastic.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/elastic.c -o ${OBJDIR}/elastic.o

OBJS += ${OBJDIR}/elastic_fd.o
${OBJDIR}/elastic_fd.o: \
    Infra/elastic_fd.c \
    Infra/elastic.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/elastic_fd.c -o ${OBJDIR}/elastic_fd.o

OBJS += ${OBJDIR}/elastic_match.o
${OBJDIR}/elastic_match.o: \
    Infra/elastic_match.c \
    Infra/elastic.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/elastic_match.c -o ${OBJDIR}/elastic_match.o

OBJS += ${OBJDIR}/elastic_tcp.o
${OBJDIR}/elastic_tcp.o: \
    Infra/elastic_tcp.c \
    Infra/elastic.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/elastic_tcp.c -o ${OBJDIR}/elastic_tcp.o

OBJS += ${OBJDIR}/firmware.o
${OBJDIR}/firmware.o: \
    Infra/firmware.c \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/firmware.c -o ${OBJDIR}/firmware.o

OBJS += ${OBJDIR}/firmware_cli.o
${OBJDIR}/firmware_cli.o: \
    Infra/firmware_cli.c \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/firmware_cli.c -o ${OBJDIR}/firmware_cli.o

OBJS += ${OBJDIR}/main.o
${OBJDIR}/main.o: \
    Infra/main.c \
    Infra/vsb.h \
    Iop/iop.h \
    Chassis/r1000_arch.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/main.c -o ${OBJDIR}/main.o

OBJS += ${OBJDIR}/rpn.o
${OBJDIR}/rpn.o: \
    Infra/rpn.c \
    Infra/vsb.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/rpn.c -o ${OBJDIR}/rpn.o

OBJS += ${OBJDIR}/trace.o
${OBJDIR}/trace.o: \
    Infra/trace.c \
    Infra/trace.h \
    Infra/vsb.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Infra/trace.c -o ${OBJDIR}/trace.o

OBJS += ${OBJDIR}/vav.o
${OBJDIR}/vav.o: \
    Infra/vav.c \
    Infra/vav.h
	${CC} ${CFLAGS} -c Infra/vav.c -o ${OBJDIR}/vav.o

OBJS += ${OBJDIR}/vsb.o
${OBJDIR}/vsb.o: \
    Infra/vsb.c \
    Infra/vsb.h
	${CC} ${CFLAGS} -c Infra/vsb.c -o ${OBJDIR}/vsb.o
