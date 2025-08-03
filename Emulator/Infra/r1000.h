/*-
 * Copyright (c) 2005-2020 Poul-Henning Kamp
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

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <pthread.h>
#include <sys/types.h>

#include "vqueue.h"

#define AZ(x) do { assert((x) == 0); } while(0)
#define AN(x) do { assert((x) != 0); } while(0)
#define WRONG() assert(__LINE__ == 0);

#ifndef __printflike
#    define __printflike(fmtarg, firstvararg) \
     __attribute__((__format__ (__printf__, fmtarg, firstvararg)))
#endif

#define TRUST_ME(ptr)  ((void*)(uintptr_t)(ptr))

struct vsb;

/**********************************************************************/
/*
 * In OO-light situations, functions have to match their prototype
 * even if that means not const'ing a const'able argument.
 * The typedef should be specified as argument to the macro.
 */
#define v_matchproto_(xxx)              /*lint --e{818} */

struct cli;
struct callout;

typedef int64_t			nanosec;
extern volatile nanosec		simclock;
extern volatile nanosec		systemc_t_zero;
extern volatile int		systemc_clock;
extern int			trace_fd;
extern volatile int		iop_running;

/* CONTEXT  ***************************************************************/

void CTX_init(const char *path);

/* MAIN ***************************************************************/

void finish(int status, const char *why)  __attribute__((__noreturn__));

/* CLI ****************************************************************/

struct cli {
	int			status;
	int			help;
	int			ac;
	char			**av;
	const char		*cmd;
	struct elastic		*elastic;
	struct vsb		*path;
};

typedef void cli_func_f(struct cli *);

struct cli_cmds {
	const char		*cmd;
	cli_func_f		*func;
};

void Cli_Usage(struct cli *, const char *args, const char *fmt, ...) __printflike(3,4);
void Cli_Dispatch(struct cli *, const struct cli_cmds *cmds);
int Cli_Exec(const char *);
int Cli_From_File(FILE *, int fatal);
void Cli_Printf(struct cli *, const char *fmt, ...) __printflike(2, 3);
void Cli_Error(struct cli *, const char *fmt, ...) __printflike(2, 3);
void Cli_Unknown(struct cli *);

/* RPN evaluator ******************************************************/

struct rpn;

typedef void rpn_op_f(struct rpn *);

int Rpn_Eval(struct vsb *vsb, const char *pgm);
void Rpn_AddOp(const char *name, rpn_op_f *func);
int Rpn_Need(struct rpn *rpn, unsigned up, unsigned down);
intmax_t Rpn_Pop(struct rpn *rpn);
void Rpn_Push(struct rpn *rpn, intmax_t a);
int Rpn_Failed(const struct rpn *rpn);
void Rpn_Printf(const struct rpn *rpn, const char *fmt, ...);

#define RPN_POP(var)						\
	do {							\
		var = Rpn_Pop(rpn);				\
		if (Rpn_Failed(rpn))				\
			return;					\
	} while (0)

#define RPN_PUSH(val)						\
	do {							\
		Rpn_Push(rpn, val);				\
		if (Rpn_Failed(rpn))				\
			return;					\
	} while (0)

/* R1000 **************************************************************/

cli_func_f cli_r1000;

/* Tracing & Debugging ************************************************/

void Trace(int flag, const char *fmt, ...) __printflike(2, 3);
void Tracev(int flag, const char *pfx, const char *fmt, va_list);
void TraceDump(int flag, const void *ptr, size_t len,
    const char *fmt, ...) __printflike(4, 5);

#include "trace.h"
#define TRACER(name, unused) extern int trace_##name;
TRACERS
#undef TRACER

cli_func_f cli_trace;

#include "Infra/microtrace.h"

/* CALLOUTS ***********************************************************/

void callout_signal_cond(pthread_cond_t *cond,
    pthread_mutex_t *mtx, nanosec when, nanosec repeat);

typedef void callout_callback_f(void *);
void callout_callback(callout_callback_f *func,
    void *priv, nanosec when, nanosec repeat);
void callout_sleep(nanosec duration);

nanosec callout_poll(void);

/* DIAG *************************************************************/

cli_func_f Cli_dfs;
cli_func_f cli_diagbus;
cli_func_f cli_diproc;
cli_func_f cli_firmware;
void diagbus_init(void);

/* FIRMWARE *********************************************************/

uint8_t *Firmware_Get(const char *name, size_t *size);
int Firmware_Copy(const char *name, size_t size, void *dst);

/* MEMORY *************************************************************/

void mem_init(void);

/* UTILITIES **********************************************************/

void hexdump(struct vsb *vsb, const void *ptr, size_t len, unsigned offset);

/* Safe printf into a fixed-size buffer */
#define bprintf(buf, fmt, ...)						\
	do {								\
		int ibprintf;						\
		ibprintf = snprintf(buf, sizeof buf, fmt, __VA_ARGS__);	\
		assert(ibprintf >= 0 && ibprintf < (int)sizeof buf);	\
	} while (0)
