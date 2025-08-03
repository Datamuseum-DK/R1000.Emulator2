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

#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Diag/diagproc.h"
#include "Diag/exp_hash.h"
#include "Infra/context.h"
#include "Infra/vend.h"
#include "Chassis/r1000_arch.h"

static uint64_t *ioc_wcs;
static unsigned ioc_ptr;

static void
read_last_pc(const struct diagproc *dp)
{
	struct ctx *ctx;
	uint16_t *tram;
	unsigned ctr1;

	(void)dp;
	ctx = CTX_Find("IOC_TRAM");
	AN(ctx);
	tram = (uint16_t *)(void*)(ctx + 1);
	ctr1 = tram[2048] + 2046;
	ctr1 &= 0x7ff;
	vbe16enc(dp->ram + 0x18, tram[ctr1] & 0x3fff);
	Trace(trace_diproc, "%s %s (0x%x 0x%x 0x%x)", dp->name, "Turbo READ_LAST_PC.IOC", tram[2048], ctr1, tram[ctr1]);
}


static void
load_control_store_200_ioc(const struct diagproc *dp)
{
	struct ctx *ctx;
	int n;
	uint64_t inp;

	if (ioc_wcs == NULL) {
		ctx = CTX_Find("IOC_WCS");
		AN(ctx);
		ioc_wcs = (uint64_t *)(void*)(ctx + 1);
	}
	for (n = 0; n < 16; n++) {
		inp = vbe16dec(dp->ram + 0x18 + n * 2);
		ioc_wcs[ioc_ptr++] = inp & 0xffff;
	}
	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_CONTROL_STORE_200.IOC");
}

void v_matchproto_(diagprocturbo_t)
diagproc_turbo_ioc(const struct diagproc *dp)
{

	if (dp->dl_hash == LOAD_PAREG_IOC_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_PAREG.IOC");
		return;
	}
	if (dp->dl_hash == PREP_RUN_IOC_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_RUN.IOC");
		return;
	}
	if (dp->dl_hash == LOAD_UIR_IOC_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_UIR.IOC");
		return;
	}
	if (dp->dl_hash == DISABLE_TIMERS_IOC_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo DISABLE_TIMERS.IOC");
		return;
	}
	if (dp->dl_hash == LOAD_WCS_ADDRESS_IOC_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_WCS_ADDRESS.IOC");
		ioc_ptr = vbe16dec(dp->ram + 0x2e);
		return;
	}
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_IOC_HASH ||
	    dp->dl_hash == 0x00000500) {
		load_control_store_200_ioc(dp);
		return;
	}
	if (dp->dl_hash == RUN_CHECK_IOC_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "START TRACING");
		mp_ioc_trace = 1;
		return;
	}
	if (dp->dl_hash == READ_LAST_PC_IOC_HASH) {
		read_last_pc(dp);
		return;
	}
	if (dp->dl_hash == RESET_IOC_HASH) {
		return;
	}
}
