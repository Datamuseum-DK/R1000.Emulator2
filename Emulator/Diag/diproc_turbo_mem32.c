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

static void
clear_tagstore_m32(const struct diagproc *dp)
{

	uint64_t *ptr;

	ptr = CTX_GetRaw("MEM.ram", sizeof(*ptr) << 15);
	memset(ptr, 0x00, sizeof(*ptr) << 15);

	Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_TAGSTORE.M32");
}

static void
fill_memory_m32(const struct diagproc *dp)
{
	uint64_t typ, val, *ptrt;
	int i;

	typ = vbe64dec(dp->ram + 0x18);		// P18IS8 DATA.TYP
	val = vbe64dec(dp->ram + 0x20);		// P20IS8 DATA.VAL

	ptrt = CTX_GetRaw("MEM.bitt", sizeof(*ptrt) << 22);
	for (i = 0; i < 1<<21; i++) {
		ptrt[i+i] = typ;
		ptrt[i+i+1] = val;
	}

	Trace(trace_diproc, "%s %s", dp->name, "Turbo FILL_MEMORY.M32");
}

void v_matchproto_(diagprocturbo_t)
diagproc_turbo_mem32(const struct diagproc *dp)
{
	if (dp->dl_hash == RUN_CHECK_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo RUN_CHECK.M32");
		return;
	}

	if (dp->dl_hash == SET_HIT_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo SET_HIT.M32");
		return;
	}

	if (dp->dl_hash == LOAD_CONFIG_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_CONFIG.M32");
		return;
	}

	if (dp->dl_hash == CLEAR_HITS_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_HITS.M32");
		return;
	}

	if (dp->dl_hash == CLEAR_PARITY_ERRORS_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_PARITY_ERRORS.M32");
		return;
	}

	if (dp->dl_hash == READ_NOVRAM_DATA_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_DATA.M32");
		*dp->ip = 0x3;
		diag_load_novram(dp, "R1000_MEM0_NOVRAM", 0, 0x19, 12);
		return;
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_INFO.M32");
		*dp->ip = 0x3;
		diag_load_novram(dp, "R1000_MEM0_NOVRAM", 0, 0x1f, 21);
		return;
	}
	if (dp->dl_hash == CLEAR_TAGSTORE_M32_HASH) {
		clear_tagstore_m32(dp);
		return;
	}
	if (dp->dl_hash == FILL_MEMORY_M32_HASH) {
		fill_memory_m32(dp);
		return;
	}
}
