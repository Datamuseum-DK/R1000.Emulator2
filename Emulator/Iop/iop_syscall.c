/*-
 * Copyright (c) 2021 Poul-Henning Kamp
 * All rights reserved.
 *
 * Author: Poul-Henning Kamp <phk@phk.freebsd.dk>
 *
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 */

#include <stdlib.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Musashi/m68k.h"
#include "Iop/memspace.h"
#include "Iop/iop.h"
#include "Infra/vsb.h"

struct sc_def {
	unsigned		address;
	const char		*name;
	const char		*call_args;
	const char		*ret_args;
};

static int is_tracing = 0;
static int indent = 0;

static const char supress[] = "";
static const char noreturn[] = "";

static struct sc_def sc_kernel[] = {
	{ 0x0362c, "DiagBus_Response",
	    "'D2=' D2 .W",
	    supress
	},
#if 0
	{ 0x0374c, "DiagBus_KC15",
	    "'D0=' D0 .W , 'A0=' A0 .L , A0 16 hexdump",
	    supress
	},
	{ 0x37a8, "DiagBus_KC15_CMDx", "'D0=' D0 .W", "" },
	{ 0x37b2, "DiagBus_KC15_CMD0", supress, supress },
	{ 0x37d0, "DiagBus_KC15_CMD1", supress, supress },
	{ 0x3840, "DiagBus_KC15_CMD5", supress, supress },
#endif

	{ 0x08a7a, "FifoReqRx()", "pace", supress },

#if 0
	{ 0x09d6e, "Timeout_Stop_PIT",
	    "'A1=' A1 .L",
	    supress
	},
	{ 0x09d8e, "Timeout_Start_PIT",
	    supress,
	    supress
	},
	{ 0x09dc4, "Timeout_Arm",
	    "'ticks=' D0 .W , 'func=' A2 .L",
	    supress
	},
	{ 0x09e00, "Timeout_Cancel",
	    "'func=' A2 .L",
	    supress
	},
#endif
#if 0
	{ 0x09e74, "Await_Interrupt",
	    supress,
	    "'Got awaited Interrupt'"
	},
#endif
	{ 1U<<31, NULL, NULL, NULL },
};

static struct sc_def pascal_defs[] = {
#include "Iop/pascal_syscalls.c"
	{ 1U<<31, NULL, NULL, NULL },
};

static struct sc_def sc_defs[] = {
	{ 0x10200, "FSC_10200",
	    "sp+4 @B .B , sp+2 @W .W",
	    "sp+2 @B .B , sp+0 @W .W",
	},
	{ 0x10202, "DumpOn",
	    "sp+2 @W .W , sp+3 @W .W",
	    supress
	},
	{ 0x1020a, "WriteConsole",
	    "sp+2 @L !a "
	    "a @W .W , "
	    "a 2 + a @W ascii",
	    supress
	},
#if 0
	{ 0x1021e, "ReInit",
	    "sp+2 @L 16 hexdump",
	    supress
	},
#endif
	{ 0x10226, "Calendar",
	    "sp+2 @L .L",
	    "sp+0 @L 7 hexdump"
	},
	{ 0x10232, "FSC_10232",
	    "'Src=' sp+5 @L .L , 'Dst=' sp+3 @L .L , 'Len=' sp+2 @B .B "
	    "' ' sp+5 @L sp+2 @B hexdump",
	    supress
	},
	{ 0x10280, "StartProg", ".A7", noreturn },

	{ 0x1028c, "Muls", ".D3 , .D4", ".D3 , .D4" },
	{ 0x10290, "Mulu", ".D3 , .D4", ".D3 , .D4" },
	{ 0x10294, "Divs", ".D3 , .D4", ".D3 , .D4" },
	{ 0x10298, "Divu", ".D3 , .D4", ".D3 , .D4" },

	{ 0x10308, "Time2Text",
	    "sp+4 @L .L , "
	    "sp+2 @L .L , stack",
	    "sp+2 String , "
	    "sp+0 @L @L .L"
	},
	{ 0x10364, "MovStringTail",
	    "sp+8 @L .L , sp+8 @L sp+6 @L ascii , "
	    "sp+6 @L .L , "
	    "sp+4 @L .L , "
	    "sp+2 @L .L "
	    ,
	    "sp+6 @L .L , sp+6 @L sp+4 @L ascii , "
	    "sp+4 @L .L , "
	    "sp+2 @L .L , "
	    "sp+0 @L .L"
	},
	{ 0x103b8, "PopProgram",
	    "sp+2 String , sp+4 @B .B",
	    "sp+0 @L 16 hexdump"
	},
	{ 0x10568, "Experiment",
	    "sp+0 @L !a "
	    "'stackdepth=' a @W .W , "
	    "'experiment=' a 3 + a 2 + @B ascii , "
	    "a 3 + a 2 + @B + !b "
	    "'adr=' b @W .W , "
	    "'n_out=' b 2 + @B .B , "
	    "'n_in=' b 3 + @B .B , "
	    "'params=' b 4 + b 2 + @B b 3 + @B + hexdump , ",
	    supress
	},
	{ 1U<<31, NULL, NULL, NULL },
};

struct sc_ctx {
	int			nbr;
	int			indent;
	VTAILQ_ENTRY(sc_ctx)	list;
};

struct sc_call {
	const struct sc_def	*def;
	nanosec			when;
	struct sc_ctx		*ctx;
};

static int ctx_ctr = 0;
static int ctx_level = 0;
static struct vsb *sc_vsb;

static VTAILQ_HEAD(sc_ctxhead, sc_ctx)	sc_ctxs =
    VTAILQ_HEAD_INITIALIZER(sc_ctxs);

/**********************************************************************/

static void
sc_render(int ret, const struct sc_def *def)
{
	int i;
	const char *params;

	AN(def);
	params = ret ? def->ret_args : def->call_args;
	if (params == NULL)
		params = "stack ' ' regs";

	VSB_clear(sc_vsb);

	for (i = 0; i < indent; i++)
		VSB_putc(sc_vsb, ' ');

	if (def->name == NULL)
		VSB_printf(sc_vsb, "FS_CALL_%08x", def->address);
	else
		VSB_printf(sc_vsb, "%s", def->name);

	VSB_printf(sc_vsb, "(");
	i = Rpn_Eval(sc_vsb, params);
	VSB_printf(sc_vsb, ")");
	AZ(VSB_finish(sc_vsb));
	if (i) {
		printf("\nBad RPN in syscall 0x%08x: %s\n",
		    def->address, params);
		printf("%s", VSB_data(sc_vsb));
	}
}

/**********************************************************************/

static int v_matchproto_(ioc_bpt_f)
sc_bpt_ret(void *priv, uint32_t adr)
{
	unsigned a7;
	struct sc_call *scc = priv;

	if (scc->ctx != VTAILQ_FIRST(&sc_ctxs))
		return (0);

	if (indent > 0)
		indent--;

	sc_render(1, scc->def);
	a7 = m68k_get_reg(NULL, M68K_REG_A7);
	Trace(1, "SCEXIT %2d %d SC=0x%08x A7=0x%08x RET=0x%08x %s",
	    VTAILQ_FIRST(&sc_ctxs)->nbr, ctx_level,
	    scc->def->address, a7, adr, VSB_data(sc_vsb));
	return (1);
}

static int v_matchproto_(ioc_bpt_f)
sc_bpt(void *priv, uint32_t adr)
{
	unsigned a7, u;
	struct sc_def *scd = priv;
	struct sc_call *scc;
	struct sc_ctx *sctx;

	AN(scd);
	(void)adr;
	sc_render(0, scd);
	a7 = m68k_get_reg(NULL, M68K_REG_A7);
	u = m68k_debug_read_memory_32(a7);
	if (scd->address == 0x10568) {
		/* Experiment() return to previous frame */
		u = m68k_debug_read_memory_32(a7 + 4);
	}
	Trace(1, "SCCALL %2d %d SC=0x%08x A7=0x%08x RET=0x%08x %s",
	    VTAILQ_FIRST(&sc_ctxs)->nbr, ctx_level,
	    scd->address, a7, u, VSB_data(sc_vsb));
	if (scd->address == 0x103b8) {	// PopProgram
		ctx_level--;
		sctx = VTAILQ_FIRST(&sc_ctxs);
		VTAILQ_REMOVE(&sc_ctxs, sctx, list);
		indent = sctx->indent;
		// Must leak, pointers to it still exist.
		return (0);
	}
	if (scd->address == 0x10280)
		return (0);
	if (scd->ret_args == noreturn)
		return (0);
	if (indent < 40)
		indent++;
	scc = calloc(sizeof *scc, 1);
	AN(scc);
	scc->def = scd;
	scc->when = simclock;
	scc->ctx = VTAILQ_FIRST(&sc_ctxs);
	ioc_breakpoint(u, sc_bpt_ret, scc);
	if (scd->address == 0x103b0) {	// PushProgram
		sctx = calloc(sizeof *sctx, 1);
		AN(sctx);
		VTAILQ_INSERT_HEAD(&sc_ctxs, sctx, list);
		sctx->nbr = ++ctx_ctr;
		sctx->indent = indent;
		ctx_level++;
	}
	return (0);
}

static void
start_syscall_tracing(int intern)
{
	unsigned a, b;
	struct sc_def *scp, *scp2, *scp3;
	struct sc_ctx *sctx;

	if (intern) {
		scp = sc_kernel;
		while (scp->address < 0x10000) {
			ioc_breakpoint(scp->address, sc_bpt, scp);
			scp++;
		}
	}

	scp = sc_defs;
	scp3 = pascal_defs;
	a = 0x10200;
	while (a < 0x1061c) {
		if (scp3->address == a && scp->address == a) {
			printf("DUP BREAKPOINT 0x%x\n", a);
			scp2 = scp3++;
			assert(scp3->address > a);
			scp++;
			assert(scp->address > a);
		} else if (scp3->address == a) {
			scp2 = scp3++;
			assert(scp3->address > a);
		} else if (scp->address == a) {
			scp2 = scp++;
			assert(scp->address > a);
		} else {
			scp2 = calloc(sizeof *scp2, 1);
			AN(scp2);
			scp2->address = a;
		}
		b = a;
		if (a < 0x10280) {
			a += 2;
		} else if (a < 0x10460) {
			if (intern)
				b = a + 2 + m68k_debug_read_memory_16(a + 2);
			a += 4;
		} else {
			if (intern)
				b = m68k_debug_read_memory_32(a + 2);
			a += 6;
		}
		ioc_breakpoint(b, sc_bpt, scp2);
	}
	sctx = calloc(sizeof *sctx, 1);
	AN(sctx);
	VTAILQ_INSERT_HEAD(&sc_ctxs, sctx, list);
	sc_vsb = VSB_new_auto();
	AN(sc_vsb);
}

/*
 * Internal tracing cannot start until FS is loaded, so we trigger that
 * from ioc_hotfix.c
 */

void
cli_start_internal_syscall_tracing(void)
{
	if (is_tracing == 2)
		start_syscall_tracing(1);
}

void v_matchproto_(cli_func_f)
cli_ioc_syscall(struct cli *cli)
{
	if (cli->help) {
		Cli_Usage(cli, "[internal]", "Trace DFS system calls.");
		return;
	}
	if (is_tracing)
		return;

	cli->ac--;
	cli->av++;
	if (cli->ac > 0 && !strcmp(*cli->av, "internal")) {
		is_tracing = 2;
	} else if (cli->ac != 0) {
		Cli_Error(cli, "Wrong argument.\n");
		// Cli_Usage(cli, " [internal]\n");
	} else {
		is_tracing = 1;
		start_syscall_tracing(0);
	}
}

/*************************************************************************/
/*************************************************************************/
/*************************************************************************/
/*************************************************************************/
/*************************************************************************/
/*************************************************************************/

#if 0

#include "XXX/memspace.h"
#include "XXX/vend.h"

static struct vsb *syscall_vsb;

void
ioc_dump_registers(unsigned lvl)
{

	if (trace_fd < 0 || !(do_trace & lvl))
		return;
	if (syscall_vsb == NULL)
		syscall_vsb = VSB_new_auto();
	AN(syscall_vsb);
	VSB_clear(syscall_vsb);
	VSB_printf(syscall_vsb, "%12jd Registers\n", simclock);
	ioc_dump_cpu_regs(syscall_vsb);
	AZ(VSB_finish(syscall_vsb));
	VSB_tofile(syscall_vsb, trace_fd);
}

static void
dump_text(struct vsb *vsb, unsigned adr, unsigned len)
{
	unsigned u, c;

	VSB_cat(vsb, "'");
	for (u = adr; u < adr + len; u++) {
		c = m68k_debug_read_memory_8(u);
		if (0x20 <= c && c <= 0x7e)
			VSB_putc(vsb, c);
		else if (c == 0x0a)
			VSB_cat(vsb, "␊");
		else if (c == 0x0d)
			VSB_cat(vsb, "␍");
		else if (c == 0x1b)
			VSB_cat(vsb, "␛");
		else
			VSB_cat(vsb, "␥");
	}
	VSB_cat(vsb, "'");
}

static void
dump_string(struct vsb *vsb, unsigned adr)
{
	unsigned u;

	u = vbe32dec(ram_space + adr - 4);
	VSB_printf(vsb, "-4={0x%x} ", u);
	u = vbe16dec(ram_space + adr);
	VSB_printf(vsb, "len=0x%x ", u);
	dump_text(vsb, adr + 2, u);
}

static void
dump_10204(struct vsb *vsb, unsigned a7)
{
	unsigned u;

	VSB_printf(vsb, " 0x%x", vbe16dec(ram_space + a7 + 4));
	VSB_printf(vsb, " dst=0x%08x", vbe32dec(ram_space + a7 + 6));
	u = vbe32dec(ram_space + a7 + 10);
	VSB_printf(vsb, " ptr=0x%08x {", u);
	VSB_printf(vsb, " 0x%04x", vbe16dec(ram_space + u));
	VSB_printf(vsb, " 0x%x", vbe16dec(ram_space + u + 2));
	VSB_printf(vsb, " 0x%x", vbe16dec(ram_space + u + 4));
	VSB_printf(vsb, " 0x%x", vbe16dec(ram_space + u + 6));
	VSB_printf(vsb, " 0x%x", vbe16dec(ram_space + u + 8));
	VSB_printf(vsb, " 0x%x", vbe16dec(ram_space + u + 10));
	VSB_printf(vsb, " c=0x%04x", vbe16dec(ram_space + u + 12));
	VSB_printf(vsb, " h=0x%02x", ram_space[ u + 14]);
	VSB_printf(vsb, " s=0x%02x", ram_space[u + 15]);
	VSB_printf(vsb, "}\n");
	ioc_dump_cpu_regs(syscall_vsb);
}

void
ioc_trace_syscall(unsigned pc)
{
	unsigned a7, u;

	if (trace_fd < 0 || !(do_trace & TRACE_SYSCALL))
		return;
	if (syscall_vsb == NULL)
		syscall_vsb = VSB_new_auto();
	AN(syscall_vsb);
	VSB_clear(syscall_vsb);
	VSB_printf(syscall_vsb, "%12jd Syscall 0x%x ", simclock, pc);

	a7 =  m68k_get_reg(NULL, M68K_REG_A7);
	if (0x10460 <= pc && pc <= 0x104c0)
		return;
	switch (pc) {
	case 0x1020a: return;
	case 0x102c4: return;
	case 0x10310: return;
	case 0x10380: return;
	case 0x103e4: return;
	case 0x10466: return;
	case 0x1046c: return;
	case 0x10da4: return;
	default:
		VSB_cat(syscall_vsb, "\n");
		ioc_dump_cpu_regs(syscall_vsb);
		hexdump(syscall_vsb, ram_space + a7, 0x80, a7);
		u = vbe32dec(ram_space + a7 + 4);
		if (0x10000 < u && u < 0x80000)
			hexdump(syscall_vsb, ram_space + u, 0x80, u);
		u = vbe32dec(ram_space + a7 + 8);
		if (0x10000 < u && u < 0x80000)
			hexdump(syscall_vsb, ram_space + u, 0x80, u);
		u = vbe32dec(ram_space + a7 + 12);
		if (0x10000 < u && u < 0x80000)
			hexdump(syscall_vsb, ram_space + u, 0x80, u);
		break;
	}
	AZ(VSB_finish(syscall_vsb));
	VSB_tofile(syscall_vsb, trace_fd);
}

struct syscall {
	const char	*name;
	unsigned	lo;
	unsigned	hi;
	unsigned	no_trace;
	unsigned	dump;
	const char	*call;
	const char	*ret;
};

static int v_matchproto_(mem_event_f)
sc_peg(void *priv, const struct memdesc *md, const char *what, unsigned adr, unsigned val,
    unsigned width, unsigned peg)
{
	struct syscall *sc = priv;
	const char *which;
	unsigned a7, sp, u, v, w;

	(void)md;
	(void)val;
	(void)what;
	(void)width;
	(void)peg;

	if (ioc_fc != 2 && ioc_fc != 6)
		return (0);

	if (syscall_vsb == NULL)
		syscall_vsb = VSB_new_auto();
	AN(syscall_vsb);
	VSB_clear(syscall_vsb);
	VSB_printf(syscall_vsb, "%12jd ", simclock);

	a7 =  m68k_get_reg(NULL, M68K_REG_A7);
	if (adr == sc->lo) {
		VSB_printf(syscall_vsb, "CALL %s(%s)\n", sc->name, sc->call);
		which = sc->call;
	} else if (adr == sc->hi) {
		VSB_printf(syscall_vsb, "RETURN %s(%s)\n", sc->name, sc->ret);
		which = sc->ret;
	} else {
		WRONG();
	}
	sp = a7 + 4;
	for(; *which != '\0'; which += 2) {
		if (which[0] == 'D' && which[1] == '0') {
			VSB_printf(syscall_vsb, "\t\tD0: 0x%x\n", m68k_get_reg(NULL, M68K_REG_D0));
			continue;
		}
		if (which[0] == 'D' && which[1] == '2') {
			VSB_printf(syscall_vsb, "\t\tD2: 0x%x\n", m68k_get_reg(NULL, M68K_REG_D2));
			continue;
		}
		if (which[0] == 'A' && which[1] == '0') {
			u = m68k_get_reg(NULL, M68K_REG_A0);
			VSB_printf(syscall_vsb, "\t\tA0: ");
			if (u < 0x80000)
				hexdump(syscall_vsb, ram_space + u, 0x10, u);
			else
				VSB_printf(syscall_vsb, " 0x%x\n", u);
			continue;
		}
		if (which[0] == 'A' && which[1] == '1') {
			u = m68k_get_reg(NULL, M68K_REG_A1);
			VSB_printf(syscall_vsb, "\t\tA1: ");
			if (u < 0x80000)
				hexdump(syscall_vsb, ram_space + u, 0x10, u);
			else
				VSB_printf(syscall_vsb, " 0x%x\n", u);
			continue;
		}
		if (which[0] == 'A' && which[1] == '2') {
			u = m68k_get_reg(NULL, M68K_REG_A2);
			VSB_printf(syscall_vsb, "\t\tA2: ");
			if (u < 0x80000)
				hexdump(syscall_vsb, ram_space + u, 0x10, u);
			else
				VSB_printf(syscall_vsb, " 0x%x\n", u);
			continue;
		}
		if (which[0] == 'i' && which[1] == 'l') {
			// Ignore 32 bits on stack
			sp += 4;
			continue;
		}
		if (which[0] == 'i' && which[1] == 'w') {
			// Ignore 16 bits on stack
			sp += 2;
			continue;
		}
		if (which[0] == 's' && which[1] == 'L') {
			// 32 bit long word on stack
			u = m68k_debug_read_memory_32(sp);
			VSB_printf(syscall_vsb, "\t\tLong: 0x%x\n", u);
			sp += 4;
			continue;
		}
		if (which[0] == 's' && which[1] == 'W') {
			// 16 bit word on stack
			u = m68k_debug_read_memory_16(sp);
			VSB_printf(syscall_vsb, "\t\tWord: 0x%x\n", u);
			sp += 2;
			continue;
		}
		if (which[0] == 's' && which[1] == 'B') {
			// 8 bit byte on stack
			u = m68k_debug_read_memory_8(sp);
			VSB_printf(syscall_vsb, "\t\tByte: 0x%x\n", u);
			sp += 2;
			continue;
		}
		if (which[0] == 's' && which[1] == 'E') {
			// 32 bit experiment pointer on stack
			u = m68k_debug_read_memory_32(sp);
			if (u && u < 0x80000) {
				VSB_printf(syscall_vsb, "\t\tExperiment:\n");
				hexdump(syscall_vsb, ram_space + u, 0x40, u);
			} else {
				VSB_printf(syscall_vsb, "\t\tExperiment: 0x%x\n", u);
			}
			sp += 4;
			continue;
		}
		if (which[0] == 's' && which[1] == 'P') {
			// 32 bit pointer on stack
			u = m68k_debug_read_memory_32(sp);
			VSB_printf(syscall_vsb, "\t\tPointer: ");
			if (u && u < 0x80000)
				hexdump(syscall_vsb, ram_space + u, 0x10, u);
			else
				VSB_printf(syscall_vsb, "0x%x\n", u);
			sp += 4;
			continue;
		}
		if (which[0] == 's' && which[1] == 'q') {
			// 32 bit pointer to pointer on stack
			u = m68k_debug_read_memory_32(sp);
			VSB_printf(syscall_vsb, "\t\tPointer: 0x%x", u);
			u = m68k_debug_read_memory_32(u);
			VSB_printf(syscall_vsb, " *-> 0x%x\n", u);
			sp += 4;
			continue;
		}
		if (which[0] == 's' && which[1] == 'Q') {
			// 32 bit pointer to pointer on stack
			u = m68k_debug_read_memory_32(sp);
			VSB_printf(syscall_vsb, "\t\tPointer: 0x%x", u);
			u = m68k_debug_read_memory_32(u);
			VSB_printf(syscall_vsb, " *-> 0x%x ", u);
			if (u)
				hexdump(syscall_vsb, ram_space + u, 0x40, u);
			else
				VSB_cat(syscall_vsb, "\n");
			sp += 4;
			continue;
		}
		if (which[0] == 's' && which[1] == 'S') {
			// 32 bit pointer to string on stack
			u = m68k_debug_read_memory_32(sp);
			VSB_printf(syscall_vsb, "\t\tString: 0x%x ", u);
			if (u)
				dump_string(syscall_vsb, u);
			VSB_cat(syscall_vsb, "\n");
			sp += 4;
			continue;
		}
		if (which[0] == 'x' && which[1] == '0') {
			// 32 bit pointer to string on stack
			// Length is second previous arg on stack
			v = m68k_debug_read_memory_16(sp - 4);
			u = m68k_debug_read_memory_32(sp);
			VSB_printf(syscall_vsb, "\t\tText[0x%x]: 0x%x ", v, u);
			dump_text(syscall_vsb, u, v);
			VSB_cat(syscall_vsb, "\n");
			sp += 4;
			continue;
		}
		if (which[0] == 'x' && which[1] == '1') {
			// A2 -> string, lengtn in D1
			// Length is second previous arg on stack
			u = m68k_get_reg(NULL, M68K_REG_A2);
			v = m68k_get_reg(NULL, M68K_REG_D1);
			VSB_printf(syscall_vsb, "\t\tText[0x%x]: 0x%x ", v, u);
			dump_text(syscall_vsb, u, v);
			VSB_cat(syscall_vsb, "\n");
			continue;
		}
		if (which[0] == 'x' && which[1] == '3') {
			hexdump(syscall_vsb, ram_space + 0x150c, 0x100, 0x150c);
			continue;
		}
		WRONG();
	}
	if (sc->dump) {
		VSB_printf(syscall_vsb, "PC = 0x%x\n", adr);
		ioc_dump_cpu_regs(syscall_vsb);
		hexdump(syscall_vsb, ram_space + a7, 0x80, a7);
	}
	AZ(VSB_finish(syscall_vsb));
	VSB_tofile(syscall_vsb, trace_fd);
	return (0);
}

static struct syscall syscalls[] = {
	{ ">CONSOLE.3",		0x02374, 0x023de, 0x023e0, 0, "x1", ""},
	{ ">CONSOLE.2",		0x028dc, 0,	  0x02978, 0, "", ""},
	{ ">CONSOLE.0",		0x02978, 0,	  0x029a6, 0, "", ""},
	{ ">CONSOLE.1",		0x02992, 0,	  0x02ab0, 0, "", ""},
	{ ">CONSOLE",		0x02ab0, 0,	  0x02ad2, 0, "", ""},
	// { "IS_IDLE?",		0x03638, 0,	  0x0364a, 0, "", ""},
	{ "_CHS9_LBA10",	0x04b20, 0,	  0x04b82, 0, "", ""},
	{ "_SCSID.0",		0x05502, 0,	  0x05556, 0, "", ""},
	{ "_DISPATCH_KERNCALL",	0x08370, 0,	  0x0838c, 0, "", ""},
	{ "KC_03_WAIT_DISK",	0x08536, 0x8562,  0x8564,  0, "", ""},
	{ "KC_1C",		0x089aa, 0,	  0x089ee, 0, "", ""},
	{ "DEFDMAMAP",		0x08e12, 0,	  0x08eb0, 0, "D0", ""},
	{ "DEFXXMAP",		0x09cee, 0x9d30,  0x09d32, 0, "", ""},
	{ ">PIT.0",		0x09d6e, 0x09d8c, 0x09d8e, 0, "", ""},
	{ ">PIT.1",		0x09d8e, 0x09dc2, 0x09dc4, 0, "", ""},
	{ ">PIT",		0x09e30, 0x09e68, 0x09e6a, 0, "", ""},
	{ "$IDLE",		0x09e74, 0x09f04, 0x09f06, 0, "", ""},
	{ "INIT.PROGRAM",	0x10656, 0,	  0x10704, 0, "", "" },
	{ "MALLOC",		0x10856, 0x108b8, 0x108de, 0, "sL", "ilsq" },
	{ "FREE",		0x108fa, 0x109fc, 0x109fc, 0, "sLsq", "" },
	{ "ALLOC_STR",		0x10cfa, 0x10d34, 0x10d34, 0, "", "sq" },
	{ "FILL_STR",		0x10da4, 0x10e60, 0x10e60, 0, "sWsWx0", "iwiwilsS"},
	{ "AppendChar",		0x10d66, 0x10da2, 0x10da4, 0, "sBsS", "sBsS" },
	{ "StringEqual",	0x10e62, 0x10ed8, 0x10eda, 0, "sSsS", "ililsB" },
	{ "StringDup",		0x10eda, 0x10f2a, 0x10f2c, 0, "sSsL", "sSsS" },
	{ "StringCat",		0x10f2c, 0x10fc8, 0x10fc8, 0, "sSsSil", "ililsS"},
	{ "StringCat2",		0x10fca, 0x10ffe, 0x11000, 0, "sSsSsS", "ililsS" },
	{ "LongInt2String",	0x110c0, 0x111cc, 0x111ce, 0, "sL", "ilsS" },
	{ "String2LongInt",	0x1127c, 0x113ae, 0x113b0, 0, "sPsPsS", "sPsPsL"},
	{ "ToUpper",		0x113b0, 0x11424, 0x11426, 0, "sS", "sS"},
	{ "Str2Int",		0x11a36, 0x11ab2, 0,	   0, "sPsLsLsPsS", "sPsLsLsPsS" },
	{ "MONTH",		0x11ab4, 0x11b82, 0,	   0, "sPsPsS", "sPsPsS"},
	{ "ConvertTimestamp",	0x11b84, 0x11d02, 0x11d04, 0, "sPsPsS", "sPsPsS"},
	{ "DiskIO",		0x127c4, 0x12992, 0x12994, 0, "sPsPsLsWsB", "sPsPsLsWsB"},
	{ "NameI",		0x13718, 0x138b2, 0x138b4, 0, "sPsP", "sPsP" },
	{ "OPEN?",		0x138b4, 0x13a6e, 0,	   0, "sPsPsLsBsBsS", "sQsPsLsBsBsS"},
	{ "RW1?",		0x13ae6, 0x13bb6, 0,	   0, "sPsPsBsW", "sPsPsBsW"},
	{ "RW2?",		0x13bb8, 0x13c88, 0,	   0, "sPsPsBsW", "sPsPsBsW"},
	{ "RW3?",		0x13c8a, 0x13e5a, 0,	   1, "sPsPsBsWsB", "sPsPsBsWsB"},
	{ "XXX1",		0x144e6, 0x1473e, 0,	   1, "sPsB", "sPsB" },
	{ "PopProgram",		0x14e18, 0x14f66, 0,	   1, "sLsB", ""},
	{ "WR_CON_C",		0x15210, 0,	  0x15286, 0, "sB", ""},
	{ "ReadChar",		0x15286, 0x15390, 0x15392, 0, "", "sB"},
	{ "WriteConsole",	0x15392, 0x15408, 0x15408, 0, "sS", ""},
	{ "WriteConsoleCRLF",	0x1540a, 0x154ae, 0x154b0, 0, "", ""},
	{ "WriteLnConsole",	0x154b0, 0x154f4, 0x154f4, 0, "sS", ""},
	{ "AskConsoleString",	0x15694, 0x158be, 0x158c0, 0, "sS", "ilsS"},
	{ "ReadDir",		0x17d1a, 0x17e94, 0,	   1, "", ""},
	{ "fs_10466",		0x18b28, 0x18b84, 0,	   1, "", ""},
	{ "fs_1046c",		0x18b86, 0x18bf2, 0,	   1, "", ""},
	{ "fs_10496_exp_close",	0x18eec, 0x18ff0, 0,	   1, "", ""},
	{ "fs_1049c",		0x18ff2, 0x190a2, 0,	   1, "", ""},
	{ "fs_104a2",		0x190a4, 0x190f8, 0,	   1, "", ""},
	{ "fs_104a8",		0x190fa, 0x19168, 0,	   1, "", ""},
	{ "fs_104ae",		0x1916a, 0x191d4, 0,	   1, "", ""},
	{ "fs_104b4",		0x191d6, 0x1927c, 0,	   1, "", ""},
	{ "fs_104c0",		0x194f6, 0x195fc, 0,	   1, "", ""},
	{ "fs_10610",		0x1afd0, 0x1b01e, 0x1b020, 0, "", "sB"},

	{ "novram_0",		0x21cda, 0,	  0,	   1, "sB", ""},
	{ "novram_0",		0x21e48, 0,	  0,	   1, "A1", ""},

	{ NULL, 0, 0, 0, 0, NULL, NULL },
};

#endif
