
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

static uint64_t *fiu_wcs;
static unsigned fiu_ptr;

static void
load_control_store_200_fiu(const struct diagproc *dp)
{
	struct ctx *ctx;
	int n;
	uint64_t wcs, inp;

	if (fiu_wcs == NULL) {
		ctx = CTX_Find("FIU_WCS");
		AN(ctx);
		fiu_wcs = (uint64_t *)(void*)(ctx + 1);
	}
	for (n = 0; n < 16; n++) {
		inp = vbe64dec(dp->ram + 0x18 + n * 8);

		wcs = 0;   wcs |= (inp >>  7) & 1; // 46
		wcs <<= 1; wcs |= (inp >> 15) & 1; // 45
		wcs <<= 1; wcs |= (inp >> 23) & 1; // 44
		wcs <<= 1; wcs |= (inp >> 31) & 1; // 43
		wcs <<= 1; wcs |= (inp >> 39) & 1; // 42
		wcs <<= 1; wcs |= (inp >> 47) & 1; // 41
		wcs <<= 1; wcs |= (inp >> 55) & 1; // 40
		wcs <<= 1; // wcs |= (inp >>  0) & 0; // 39
		wcs <<= 1; wcs |= (inp >> 63) & 1; // 38
		wcs <<= 1; wcs |= (inp >>  6) & 1; // 37
		wcs <<= 1; wcs |= (inp >> 14) & 1; // 36
		wcs <<= 1; wcs |= (inp >> 22) & 1; // 35
		wcs <<= 1; wcs |= (inp >> 30) & 1; // 34
		wcs <<= 1; wcs |= (inp >> 38) & 1; // 33
		wcs <<= 1; wcs |= (inp >> 46) & 1; // 32
		wcs <<= 1; wcs |= (inp >> 54) & 1; // 31
		wcs <<= 1; wcs |= (inp >> 62) & 1; // 30
		wcs <<= 1; wcs |= (inp >>  5) & 1; // 29
		wcs <<= 1; wcs |= (inp >> 13) & 1; // 28
		wcs <<= 1; wcs |= (inp >> 21) & 1; // 27
		wcs <<= 1; wcs |= (inp >> 29) & 1; // 26
		wcs <<= 1; wcs |= (inp >> 37) & 1; // 25
		wcs <<= 1; wcs |= (inp >> 45) & 1; // 24
		wcs <<= 1; wcs |= (inp >>  4) & 1; // 23
		wcs <<= 1; wcs |= (inp >> 12) & 1; // 22
		wcs <<= 1; wcs |= (inp >> 20) & 1; // 21
		wcs <<= 1; wcs |= (inp >> 28) & 1; // 20
		wcs <<= 1; wcs |= (inp >> 36) & 1; // 19
		wcs <<= 1; wcs |= (inp >> 44) & 1; // 18
		wcs <<= 1; wcs |= (inp >> 52) & 1; // 17
		wcs <<= 1; wcs |= (inp >> 60) & 1; // 16
		wcs <<= 1; // wcs |= (inp >>  0) & 0; // 15
		wcs <<= 1; wcs |= (inp >>  3) & 1; // 14
		wcs <<= 1; wcs |= (inp >> 11) & 1; // 13
		wcs <<= 1; wcs |= (inp >> 19) & 1; // 12
		wcs <<= 1; wcs |= (inp >> 27) & 1; // 11
		wcs <<= 1; wcs |= (inp >> 35) & 1; // 10
		wcs <<= 1; wcs |= (inp >> 43) & 1; //  9
		wcs <<= 1; wcs |= (inp >> 59) & 1; //  8
		wcs <<= 1; // wcs |= (inp >>  0) & 0; //  7
		wcs <<= 1; // wcs |= (inp >>  0) & 0; //  6
		wcs <<= 1; // wcs |= (inp >>  0) & 0; //  5
		wcs <<= 1; // wcs |= (inp >>  0) & 0; //  4
		wcs <<= 1; // wcs |= (inp >>  0) & 0; //  3
		wcs <<= 1; // wcs |= (inp >>  0) & 0; //  2
		wcs <<= 1; wcs |= (inp >>  2) & 1; //  1
		wcs <<= 1; wcs |= (inp >> 10) & 1; //  0


		fiu_wcs[fiu_ptr++] = wcs;
	}
	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_CONTROL_STORE_200.FIU");
}

static void
load_counter(const struct diagproc *dp)
{
	fiu_ptr = vbe16dec(dp->ram + 0x28);

	mp_refresh_count = vbe16dec(dp->ram + 0x26);

	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_COUNTER.FIU");
}

void v_matchproto_(diagprocturbo_t)
diagproc_turbo_fiu(const struct diagproc *dp)
{
	if (dp->dl_hash == LOAD_COUNTER_FIU_HASH) {
		load_counter(dp);
		return;
	}
	if (dp->dl_hash == INIT_MRU_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo INIT_MRU.FIU");
		return;
	}
	if (dp->dl_hash == CLEAR_PARITY_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_PARITY.FIU");
		return;
	}
	if (dp->dl_hash == LOAD_HRAM_32_0_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_HRAM_32_0.FIU");
		return;
	}
	if (dp->dl_hash == LOAD_HRAM_1_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_HRAM_1.FIU");
		return;
	}
	if (dp->dl_hash == READ_NOVRAM_DATA_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_DATA.FIU");
		*dp->ip = 0x3;
		diag_load_novram(dp, "R1000_FIU_NOVRAM", 1, 0x22, 8);
		return;
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_INFO.FIU");
		*dp->ip = 0x3;
		diag_load_novram(dp, "R1000_FIU_NOVRAM", 0, 0x27, 21);
		return;
	}
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_FIU_HASH ||
	    dp->dl_hash == 0x00001045) {
		load_control_store_200_fiu(dp);
		return;
	}
	if (dp->dl_hash == LOAD_REFRESH_REGS_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_REFRESH_REGS.FIU");
		return;
	}

	if (dp->dl_hash == CLEAR_EXCEPTIONS_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_EXCEPTIONS.FIU");
		return;
	}

	if (dp->dl_hash == LOAD_UIR_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_UIR.FIU");
		return;
	}

	if (dp->dl_hash == PREP_RUN_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_RUN.FIU");
		return;
	}

	if (dp->dl_hash == RESET_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo RESET.FIU");
		return;
	}

	if (dp->dl_hash == MF_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo MF.FIU");
		return;
	}

	if (dp->dl_hash == RUN_NORMAL_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "THAW 0");
		mp_fiu_freeze = 0;
		mp_fiu_unfreeze = 5;
	}
	if (dp->dl_hash == FREEZE_WORLD_FIU_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "THAW 1");
		mp_fiu_freeze = 1;
		mp_fiu_unfreeze = 0;
	}
}
