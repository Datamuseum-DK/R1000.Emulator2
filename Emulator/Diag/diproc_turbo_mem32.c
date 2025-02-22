
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Chassis/r1000sc.h"
#include "Chassis/z_codes.h"
#include "Diag/diag.h"
#include "Diag/diagproc.h"
#include "Diag/exp_hash.h"
#include "Infra/context.h"
#include "Infra/vend.h"

static int
clear_tagstore_m32(const struct diagproc *dp)
{

	struct ctx *ctx;
	uint8_t *ptr;

	// TAR
	ctx = CTX_Find(COMP_Z000);
	AN(ctx);
	ptr = (uint8_t *)(ctx + 1);
	memset(ptr, 0x00, 9 << 15);

	Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_TAGSTORE.M32");
	return ((int)DIPROC_RESPONSE_DONE);
}

static int
fill_memory_m32(const struct diagproc *dp)
{
	struct ctx *ctx;
	uint64_t typ, val, *ptrt;
	int i;

	typ = vbe64dec(dp->ram + 0x18);		// P18IS8 DATA.TYP
	val = vbe64dec(dp->ram + 0x20);		// P20IS8 DATA.VAL

	// P28IS1 DATA.VPAR is loaded into DREGVP but not stored anywhere.

	// RAMA
	ctx = CTX_Find(COMP_Z000);
	AN(ctx);
	uint8_t *ptr = (void*)(ctx + 1);
	ptrt = (uint64_t *)(void*)(ptr + (9 << 15));
	for (i = 0; i < 1<<21; i++) {
		ptrt[i+i] = typ;
		ptrt[i+i+1] = val;
	}

	Trace(trace_diproc, "%s %s", dp->name, "Turbo FILL_MEMORY.M32");
	return ((int)DIPROC_RESPONSE_DONE);
}

int v_matchproto_(diagprocturbo_t)
diagproc_turbo_mem32(const struct diagproc *dp)
{
	if (dp->dl_hash == RUN_CHECK_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo RUN_CHECK.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (dp->dl_hash == SET_HIT_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo SET_HIT.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (dp->dl_hash == LOAD_CONFIG_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_CONFIG.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (1 && dp->dl_hash == CLEAR_HITS_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_HITS.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (dp->dl_hash == CLEAR_PARITY_ERRORS_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_PARITY_ERRORS.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (dp->dl_hash == READ_NOVRAM_DATA_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_DATA.M32");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_MEM0_NOVRAM", 0, 0x19, 12));
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_M32_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_INFO.M32");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_MEM0_NOVRAM", 0, 0x1f, 21));
	}
	if (dp->dl_hash == CLEAR_TAGSTORE_M32_HASH)
		return (clear_tagstore_m32(dp));
	if (dp->dl_hash == FILL_MEMORY_M32_HASH)
		return (fill_memory_m32(dp));
	return (0);
}
