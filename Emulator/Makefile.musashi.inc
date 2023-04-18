
M68K_INCL = \
	Musashi/m68kcpu.h \
	Musashi/m68kmmu.h \
	Musashi/softfloat/softfloat.h \
	Iop/musashi_conf.h \
	Musashi/m68kops.h

OBJS += ${OBJDIR}/m68kcpu.o
${OBJDIR}/m68kcpu.o: \
    Musashi/m68kcpu.c \
    ${M68K_INCL}
	${CC} ${CFLAGS} -c Musashi/m68kcpu.c -o ${OBJDIR}/m68kcpu.o

OBJS += ${OBJDIR}/m68kdasm.o
${OBJDIR}/m68kdasm.o: \
    Musashi/m68kdasm.c \
    ${M68K_INCL}
	${CC} ${CFLAGS} -c Musashi/m68kdasm.c -o ${OBJDIR}/m68kdasm.o

OBJS += ${OBJDIR}/m68kops.o
${OBJDIR}/m68kops.o: \
    Musashi/m68kops.c \
    Musashi/m68kcpu.h \
    Musashi/m68kops.h
	${CC} ${CFLAGS} -c Musashi/m68kops.c -o ${OBJDIR}/m68kops.o

Musashi/m68kops.h Musashi/m68kops.c: \
    ${OBJDIR}/m68kmake \
    Iop/musashi_conf.h \
    Musashi/m68k_in.c
	${OBJDIR}/m68kmake Musashi Musashi/m68k_in.c

${OBJDIR}/m68kmake: \
    Musashi/m68kmake.c
	${CC} ${CFLAGS} Musashi/m68kmake.c -o ${OBJDIR}/m68kmake

Musashi/m68kcpu.h: \
    Musashi/m68k.h

CLEANFILES += Musashi/m68kops.h Musashi/m68kops.c ${OBJDIR}/m68kmake

OBJS += ${OBJDIR}/m68ksoftfloat.o
${OBJDIR}/m68ksoftfloat.o: \
    Musashi/softfloat/softfloat.c \
    ${M68K_INCL}
	${CC} ${CFLAGS} -c Musashi/softfloat/softfloat.c -o ${OBJDIR}/m68ksoftfloat.o

