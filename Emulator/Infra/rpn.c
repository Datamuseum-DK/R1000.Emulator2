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
 * A small RPN interpreter to render state at runtime
 *
 */

#include <ctype.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Infra/vsb.h"

#define VARS \
	VAR(a) VAR(b) VAR(c) VAR(d) VAR(e) \
	VAR(f) VAR(g) VAR(h) VAR(i) VAR(j) \
	VAR(k) VAR(l) VAR(m) VAR(n) VAR(o) \
	VAR(p) VAR(q) VAR(r) VAR(s) VAR(t) \
	VAR(u) VAR(v) VAR(w) VAR(x) VAR(y) \
	VAR(z)

struct rpn_op {
	const char		*name;
	rpn_op_f		*func;
	ssize_t			namelen;
	VTAILQ_ENTRY(rpn_op)	list;
};

#define NSTACK	16
struct rpn {
	uintmax_t		stack[NSTACK];
#define VAR(name) uintmax_t var_##name;
VARS
#undef VAR
	uintmax_t		*sp;
	struct vsb		*vsb;
	const char		*pgm;
	int			error;
	const struct rpn_op	*op;
};

static VTAILQ_HEAD(,rpn_op) rpnops = VTAILQ_HEAD_INITIALIZER(rpnops);

int
Rpn_Failed(const struct rpn *rpn)
{
	return (rpn->error);
}

void
Rpn_AddOp(const char *name, rpn_op_f *func)
{
	struct rpn_op *rpo;

	AN(name);
	AN(func);
	rpo = calloc(sizeof *rpo, 1);
	AN(rpo);
	rpo->name = strdup(name);
	AN(rpo->name);
	rpo->namelen = strlen(rpo->name);
	rpo->func = func;
	VTAILQ_INSERT_TAIL(&rpnops, rpo, list);
}

static int
rpn_need(const struct rpn *rpn, unsigned up, unsigned down)
{
	AN(rpn);
	AN(rpn->op);
	AN(rpn->op->name);
	if (rpn->sp - down < rpn->stack) {
		VSB_printf(rpn->vsb,
		    "\n\n*** RPN error: Stack underrun in %s", rpn->op->name);
	}
	if (rpn->sp + up > rpn->stack + NSTACK) {
		VSB_printf(rpn->vsb,
		    "\n\n*** RPN error: Stack overrun in %s", rpn->op->name);
	}
	return (0);
}

void __printflike(2, 3)
Rpn_Printf(const struct rpn *rpn, const char *fmt, ...)
{
	va_list ap;

	AN(rpn);
	va_start(ap, fmt);
	VSB_vprintf(rpn->vsb, fmt, ap);
	va_end(ap);
}

static int
rpn_error(struct rpn *rpn, const char *fmt, ...)
{
	va_list ap;

	AN(rpn);
	VSB_cat(rpn->vsb, "\n\n*** RPN Error: ");
	va_start(ap, fmt);
	VSB_vprintf(rpn->vsb, fmt, ap);
	va_end(ap);
	rpn->error = -1;
	VSB_printf(rpn->vsb, "\n\nAt: %s\n", rpn->pgm);
	return (-1);
}

int
Rpn_Need(struct rpn *rpn, unsigned up, unsigned down)
{
	AN(rpn);
	if (rpn->sp - down < rpn->stack)
		return(rpn_error(rpn, "Stack underrun, need %u", down));
	if (rpn->sp + up > rpn->stack + NSTACK)
		return(rpn_error(rpn, "Stack overrun, need %u", up));
	return (0);
}

intmax_t
Rpn_Pop(struct rpn *rpn)
{
	intmax_t rv;

	if (rpn_need(rpn, 0, 1))
		return (0);
	rpn->sp--;
	rv = *rpn->sp;
	return (rv);
}

void
Rpn_Push(struct rpn *rpn, intmax_t a)
{

	if (rpn_need(rpn, 1, 0))
		return;
	*rpn->sp++ = a;
}

static void v_matchproto_(rpn_op_f)
rpn_dotB(struct rpn *rpn)
{
	intmax_t a;

	RPN_POP(a);
	VSB_printf(rpn->vsb, "%02jx", a & 0xff);
}


static void v_matchproto_(rpn_op_f)
rpn_dotW(struct rpn *rpn)
{
	intmax_t a;

	RPN_POP(a);
	VSB_printf(rpn->vsb, "%04jx", a & 0xffff);
}


static void v_matchproto_(rpn_op_f)
rpn_dotL(struct rpn *rpn)
{
	intmax_t a;

	RPN_POP(a);
	VSB_printf(rpn->vsb, "%08jx", a & 0xffffffff);
}


static void v_matchproto_(rpn_op_f)
rpn_dotQ(struct rpn *rpn)
{
	intmax_t a;

	RPN_POP(a);
	VSB_printf(rpn->vsb, "%016jx", a);
}

#define TWO_ARGS \
	TWO_ARG(plus, +) \
	TWO_ARG(minus, -) \
	TWO_ARG(multiply, *) \
	TWO_ARG(and, &) \
	TWO_ARG(or, |) \
	TWO_ARG(xor, ^)

#define TWO_ARG(name, oper)					\
	static void v_matchproto_(rpn_op_f)			\
	rpn_##name(struct rpn *rpn)				\
	{							\
		intmax_t a, b;					\
		RPN_POP(a);					\
		RPN_POP(b);					\
		RPN_PUSH(b oper a);				\
	}

TWO_ARGS
#undef TWO_ARG

static void v_matchproto_(rpn_op_f)
rpn_min(struct rpn *rpn)
{
	intmax_t a, b;

	RPN_POP(a);
	RPN_POP(b);
	if (a > b)
		RPN_PUSH(b);
	else
		RPN_PUSH(a);
}

static void v_matchproto_(rpn_op_f)
rpn_max(struct rpn *rpn)
{
	intmax_t a, b;

	RPN_POP(a);
	RPN_POP(b);
	if (a > b)
		RPN_PUSH(a);
	else
		RPN_PUSH(b);
}

static void v_matchproto_(rpn_op_f)
rpn_modulus(struct rpn *rpn)
{
	intmax_t a, b;

	RPN_POP(a);
	RPN_POP(b);
	if (a)
		RPN_PUSH(b % a);
	else
		RPN_PUSH(0);
}

static void v_matchproto_(rpn_op_f)
rpn_divide(struct rpn *rpn)
{
	intmax_t a, b;

	RPN_POP(a);
	RPN_POP(b);
	if (a)
		RPN_PUSH(b / a);
	else
		RPN_PUSH(0);
}

#define VAR(name)						\
	static void v_matchproto_(rpn_op_f)			\
	rpn_bang_##name(struct rpn *rpn)			\
	{							\
		RPN_POP(rpn->var_##name);			\
	}							\
	static void v_matchproto_(rpn_op_f)			\
	rpn_at_##name(struct rpn *rpn)				\
	{							\
		RPN_PUSH(rpn->var_##name);			\
	}

VARS
#undef VAR

/*lint -save -e785 */
static struct rpn_op rpn_builtin[] = {
#define TWO_ARG(name, oper) { #oper, rpn_##name },
TWO_ARGS
#undef TWO_ARG

#define VAR(name)			\
	{ "!" #name, rpn_bang_##name },	\
	{ #name, rpn_at_##name },
VARS
#undef VAR

	{ "min", rpn_min },
	{ "max", rpn_max },
	{ "/", rpn_divide },
	{ "%", rpn_modulus },
	{ ".B", rpn_dotB },
	{ ".W", rpn_dotW },
	{ ".L", rpn_dotL },
	{ ".Q", rpn_dotQ },
	{ NULL, NULL }
};
/*lint -restore */

static const struct rpn_op pseudo_number = { "<number>", NULL };

int
Rpn_Eval(struct vsb *vsb, const char *pgm)
{
	struct rpn rpn[1];
	struct rpn_op *rpno;
	intmax_t a;
	ssize_t z;

	AN(vsb);
	AN(pgm);
	memset(rpn, 0, sizeof *rpn);
	rpn->vsb = vsb;
	rpn->sp = rpn->stack;

	for(rpno = rpn_builtin; rpno->name != NULL; rpno++)
		rpno->namelen = strlen(rpno->name);

	while (*pgm != '\0') {
		if (isspace(*pgm)) {
			pgm++;
			continue;
		}

		rpn->pgm = pgm;

		if (*pgm == '\'') {
			pgm++;
			while (*pgm != '\0' && *pgm != '\'')
				VSB_putc(rpn->vsb, *pgm++);
			if (*pgm++ != '\'') {
				rpn_error(rpn, "Unterminated string");
				return (-1);
			}
			continue;
		}
		z = strcspn(pgm, "\t\n\v\f\r ");
		assert(z > 0);
		if (isdigit(*pgm)) {
			a = strtoumax(pgm, NULL, 0);
			rpn->op = &pseudo_number;
			Rpn_Push(rpn, a);
			rpn->op = NULL;
			if (Rpn_Failed(rpn))
				return (-1);
			pgm += z;
			continue;
		}
		VTAILQ_FOREACH(rpno, &rpnops, list) {
			if (rpno->namelen == z && !memcmp(rpno->name, pgm, z))
				break;
		}
		if (rpno == NULL) {
			for(rpno = rpn_builtin; rpno->name != NULL; rpno++) {
				if (rpno->namelen == z && !memcmp(rpno->name, pgm, z))
					break;
			}
			if (rpno->name == NULL)
				rpno = NULL;
		}
		if (rpno == NULL) {
			rpn_error(rpn, "Unknown operator: '%.*s'",
			    (int)z, pgm);
			return (-1);
		}
		rpn->op = rpno;
		AN(rpn->op);
		AN(rpno->name);
		AN(rpno->func);
		rpno->func(rpn);
		rpn->op = NULL;
		if (rpn->error)
			return(rpn->error);
		pgm += z;
	}
	return (0);
}
