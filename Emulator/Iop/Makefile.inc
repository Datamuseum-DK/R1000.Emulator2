
OBJS += ${OBJDIR}/iop_cli.o
${OBJDIR}/iop_cli.o: \
    Iop/iop_cli.c \
    Iop/iop.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_cli.c -o ${OBJDIR}/iop_cli.o

OBJS += ${OBJDIR}/iop_debug.o
${OBJDIR}/iop_debug.o: \
    Iop/iop_debug.c \
    Musashi/m68k.h \
    Iop/iop.h \
    Infra/vsb.h \
    Iop/memspace.h \
    Iop/_memcfg.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_debug.c -o ${OBJDIR}/iop_debug.o

OBJS += ${OBJDIR}/iop_duart.o
${OBJDIR}/iop_duart.o: \
    Iop/iop_duart.c \
    Iop/iop.h \
    Infra/elastic.h \
    Infra/vsb.h \
    Iop/memspace.h \
    Diag/diag.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_duart.c -o ${OBJDIR}/iop_duart.o

OBJS += ${OBJDIR}/iop_eeproms.o
${OBJDIR}/iop_eeproms.o: \
    Iop/iop_eeproms.c \
    Iop/iop.h \
    Iop/memspace.h \
    Infra/vend.h \
    Chassis/r1000sc.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_eeproms.c -o ${OBJDIR}/iop_eeproms.o

OBJS += ${OBJDIR}/iop_pnlreg.o
${OBJDIR}/iop_pnlreg.o: \
    Iop/iop_pnlreg.c \
    Iop/memspace.h \
    Infra/vend.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_pnlreg.c -o ${OBJDIR}/iop_pnlreg.o

OBJS += ${OBJDIR}/iop_hotfix.o
${OBJDIR}/iop_hotfix.o: \
    Iop/iop_hotfix.c \
    Iop/iop.h \
    Iop/memspace.h \
    Infra/vend.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_hotfix.c -o ${OBJDIR}/iop_hotfix.o

OBJS += ${OBJDIR}/iop_interrupt.o
${OBJDIR}/iop_interrupt.o: \
    Iop/iop_interrupt.c \
    Iop/iop.h \
    Infra/vend.h \
    Iop/memspace.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_interrupt.c -o ${OBJDIR}/iop_interrupt.o

OBJS += ${OBJDIR}/iop_main.o
${OBJDIR}/iop_main.o: \
    Iop/iop_main.c \
    Infra/vsb.h \
    Infra/vend.h \
    Iop/memspace.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_main.c -o ${OBJDIR}/iop_main.o

OBJS += ${OBJDIR}/iop_memory.o
${OBJDIR}/iop_memory.o: \
    Iop/iop_memory.c \
    Infra/vend.h \
    Iop/memspace.h \
    Iop/iop.h \
    Iop/iop_sc_68k20.hh \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_memory.c -o ${OBJDIR}/iop_memory.o

OBJS += ${OBJDIR}/iop_memtrace.o
${OBJDIR}/iop_memtrace.o: \
    Iop/iop_memtrace.c \
    Iop/iop.h \
    Iop/memspace.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_memtrace.c -o ${OBJDIR}/iop_memtrace.o

OBJS += ${OBJDIR}/iop_mosart.o
${OBJDIR}/iop_mosart.o: \
    Iop/iop_mosart.c \
    Iop/iop.h \
    Iop/memspace.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_mosart.c -o ${OBJDIR}/iop_mosart.o

OBJS += ${OBJDIR}/iop_rtc.o
${OBJDIR}/iop_rtc.o: \
    Iop/iop_rtc.c \
    Iop/iop.h \
    Iop/memspace.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_rtc.c -o ${OBJDIR}/iop_rtc.o

OBJS += ${OBJDIR}/iop_sc.o
${OBJDIR}/iop_sc.o: \
    Iop/iop_sc.c \
    Iop/iop_sc_68k20.hh \
    Iop/iop.h \
    Chassis/r1000sc_priv.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_sc.c -o ${OBJDIR}/iop_sc.o

OBJS += ${OBJDIR}/iop_scsi_ctl.o
${OBJDIR}/iop_scsi_ctl.o: \
    Iop/iop_scsi_ctl.c \
    Iop/iop_scsi.h \
    Iop/iop.h \
    Iop/memspace.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_scsi_ctl.c -o ${OBJDIR}/iop_scsi_ctl.o

OBJS += ${OBJDIR}/iop_scsi_dev.o
${OBJDIR}/iop_scsi_dev.o: \
    Iop/iop_scsi_dev.c \
    Iop/iop_scsi.h \
    Iop/iop.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_scsi_dev.c -o ${OBJDIR}/iop_scsi_dev.o

OBJS += ${OBJDIR}/iop_syscall.o
${OBJDIR}/iop_syscall.o: \
    Iop/iop_syscall.c \
    Iop/pascal_syscalls.c \
    Iop/iop.h \
    Iop/memspace.h \
    Infra/vsb.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_syscall.c -o ${OBJDIR}/iop_syscall.o

OBJS += ${OBJDIR}/iop_vme.o
${OBJDIR}/iop_vme.o: \
    Iop/iop_vme.c \
    Iop/iop.h \
    Infra/context.h \
    Infra/vend.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_vme.c -o ${OBJDIR}/iop_vme.o

OBJS += ${OBJDIR}/iop_uart.o
${OBJDIR}/iop_uart.o: \
    Iop/iop_uart.c \
    Iop/iop.h \
    Infra/elastic.h \
    ${R1000DEP}
	${CC} ${CFLAGS} -c Iop/iop_uart.c -o ${OBJDIR}/iop_uart.o

OBJS += ${OBJDIR}/_memcfg.o
${OBJDIR}/_memcfg.o: \
    Iop/_memcfg.c \
    Iop/_memcfg.h \
    Infra/context.h \
    Infra/vend.h \
    Infra/vqueue.h \
    Iop/memspace.h
	${CC} ${CFLAGS} -c Iop/_memcfg.c -o ${OBJDIR}/_memcfg.o

CLEANFILES += Iop/_memcfg.c Iop/_memcfg.h

Iop/_memcfg.c Iop/_memcfg.h: \
    Iop/makemem.py \
    Iop/makemem_class.py
	python3 Iop/makemem.py
