
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


static unsigned seq_ptr;
#if defined(HAS_Z020)
static uint64_t *seq_wcs;
static uint32_t *decode;
#endif

static int
load_dispatch_rams_200_seq(const struct diagproc *dp)
{
#if !defined(HAS_Z020)
	fprintf(stderr, "NO Z020\n");
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	unsigned offset, n;
	uint64_t src;
	uint32_t dst;

	if (decode == NULL) {
		ctx = CTX_Find(COMP_Z020);
		AN(ctx);
		decode = (uint32_t *)(void*)(ctx + 1);
	}
	offset = vbe16dec(dp->ram + 0x18);
	if (dp->ram[0x11]) {
		// Low
		offset += 1024;
	} else {
		// High
		offset >>= 6;
	}
	for (n = 0; n < 16; n++) {
		src = vbe64dec(dp->ram + 0x1a + 8 * n);
		// This translation found by correlation
		// Last three entries are ambigious (always zero)
		dst = 0;   dst |= (src >>  7) & 1;	// 31
		dst <<= 1; dst |= (src >> 15) & 1;
		dst <<= 1; dst |= (src >>  6) & 1;
		dst <<= 1; dst |= (src >> 14) & 1;
		dst <<= 1; dst |= (src >> 23) & 1;
		dst <<= 1; dst |= (src >> 31) & 1;
		dst <<= 1; dst |= (src >> 22) & 1;	// 25
		dst <<= 1; dst |= (src >> 39) & 1;
		dst <<= 1; dst |= (src >> 47) & 1;
		dst <<= 1; dst |= (src >> 30) & 1;
		dst <<= 1; dst |= (src >> 55) & 1;
		dst <<= 1; dst |= (src >> 63) & 1;	// 20
		dst <<= 1; dst |= (src >> 38) & 1;
		dst <<= 1; dst |= (src >> 54) & 1;
		dst <<= 1; dst |= (src >> 62) & 1;
		dst <<= 1; dst |= (src >> 46) & 1;
		dst <<= 1; dst |= (src >> 53) & 1;	// 15
		dst <<= 1; dst |= (src >> 61) & 1;
		dst <<= 1; dst |= (src >> 29) & 1;
		dst <<= 1; dst |= (src >> 37) & 1;
		dst <<= 1; dst |= (src >> 45) & 1;
		dst <<= 1; dst |= (src >> 12) & 1;	// 10
		dst <<= 1; dst |= (src >> 20) & 1;
		dst <<= 1; dst |= (src >> 28) & 1;
		dst <<= 1; dst |= (src >> 36) & 1;
		dst <<= 1; dst |= (src >> 60) & 1;
		dst <<= 1; dst |= (src >> 52) & 1;	// 5
		dst <<= 1; dst |= (src >> 44) & 1;
		dst <<= 1; dst |= (src >>  5) & 1;
		dst <<= 1; dst |= (src >> 21) & 1; // =0
		dst <<= 1; dst |= (src >> 13) & 1; // =0
		dst <<= 1; dst |= (src >>  4) & 1; // =0

		decode[offset + n] = dst;
	}

	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_DISPATCH_RAMS_200.SEQ");

	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

static int
load_control_store_200_seq(const struct diagproc *dp)
{
	struct ctx *ctx;
	int n;
	uint64_t wcs, inp;

	if (seq_wcs == NULL) {
		ctx = CTX_Find("SEQ_WCS");
		AN(ctx);
		seq_wcs = (uint64_t *)(void*)(ctx + 1);
	}
	for (n = 0; n < 16; n++) {
		inp = vbe64dec(dp->ram + 0x18 + n * 8);

		wcs = 0;   wcs |= (inp >> 46) & 1; // 41
		wcs <<= 1; wcs |= (inp >> 38) & 1; // 40
		wcs <<= 1; wcs |= (inp >> 30) & 1; // 39
		wcs <<= 1; wcs |= (inp >> 22) & 1; // 38
		wcs <<= 1; wcs |= (inp >> 14) & 1; // 37
		wcs <<= 1; wcs |= (inp >>  6) & 1; // 36
		wcs <<= 1; wcs |= (inp >> 63) & 1; // 35
		wcs <<= 1; wcs |= (inp >> 55) & 1; // 34
		wcs <<= 1; wcs |= (inp >> 47) & 1; // 33
		wcs <<= 1; wcs |= (inp >> 39) & 1; // 32
		wcs <<= 1; wcs |= (inp >> 31) & 1; // 31
		wcs <<= 1; wcs |= (inp >> 23) & 1; // 30
		wcs <<= 1; wcs |= (inp >> 15) & 1; // 29
		wcs <<= 1; wcs |= (inp >>  7) & 1; // 28
		wcs <<= 1; wcs |= (inp >> 18) & 1; // 27
		wcs <<= 1; wcs |= (inp >> 61) & 1; // 26
		wcs <<= 1; wcs |= (inp >> 45) & 1; // 25
		wcs <<= 1; wcs |= (inp >> 53) & 1; // 24
		wcs <<= 1; wcs |= (inp >> 36) & 1; // 23
		wcs <<= 1; wcs |= (inp >> 44) & 1; // 22
		wcs <<= 1; wcs |= (inp >> 12) & 1; // 21
		wcs <<= 1; wcs |= (inp >> 20) & 1; // 20
		wcs <<= 1; wcs |= (inp >> 37) & 1; // 19
		wcs <<= 1; wcs |= (inp >> 29) & 1; // 18
		wcs <<= 1; wcs |= (inp >>  5) & 1; // 17
		wcs <<= 1; wcs |= (inp >> 13) & 1; // 16
		wcs <<= 1; wcs |= (inp >> 21) & 1; // 15
		wcs <<= 1; wcs |= (inp >> 62) & 1; // 14
		wcs <<= 1; wcs |= (inp >> 54) & 1; // 13
		wcs <<= 1; wcs |= (inp >>  2) & 1; // 12
		wcs <<= 1; wcs |= (inp >> 10) & 1; // 11
		wcs <<= 1; wcs |= (inp >> 28) & 1; // 10
		wcs <<= 1; wcs |= (inp >>  4) & 1; // 9
		wcs <<= 1; wcs |= (inp >> 52) & 1; // 8
		wcs <<= 1; wcs |= (inp >> 60) & 1; // 7
		wcs <<= 1; wcs |= (inp >>  1) & 1; // 6
		wcs <<= 1; wcs |= (inp >>  9) & 1; // 5
		wcs <<= 1; wcs |= (inp >> 50) & 1; // 4
		wcs <<= 1; wcs |= (inp >> 58) & 1; // 3
		wcs <<= 1; wcs |= (inp >> 34) & 1; // 2
		wcs <<= 1; wcs |= (inp >> 42) & 1; // 1
		wcs <<= 1; wcs |= (inp >> 26) & 1; // 0
		seq_wcs[seq_ptr++] = wcs;
	}
	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_CONTROL_STORE_200.SEQ");
	return ((int)DIPROC_RESPONSE_DONE);
}

static void
prep_run_seq(const struct diagproc *dp)
{
	struct ctx *ctx;
	uint16_t *nxtuadr;

	ctx = CTX_Find(COMP_Z020);
	AN(ctx);
	uint8_t *ptr = (void*)(ctx + 1);
	ptr += 4 << 10;	// uint32_t top[1<<10]
	ptr += 4 << 10; // uint32_t bot[1<<10]
	nxtuadr = (uint16_t *)(void*)ptr;

	nxtuadr[0] = vbe16dec(dp->ram + 0x18);
	nxtuadr[1] = vbe16dec(dp->ram + 0x18);
	mp_nua_bus = vbe16dec(dp->ram + 0x18);
	Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_RUN.SEQ");
}

int v_matchproto_(diagprocturbo_t)
diagproc_turbo_seq(const struct diagproc *dp)
{
	if (dp->dl_hash == CLEAR_PARITY_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_PARITY.SEQ");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == READ_NOVRAM_DATA_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_DATA.SEQ");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_SEQ_NOVRAM", 1, 0x1a, 8));
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_INFO.SEQ");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_SEQ_NOVRAM", 0, 0x20, 21));
	}

	if (dp->dl_hash == LOAD_DISPATCH_RAMS_200_SEQ_HASH ||
	    dp->dl_hash == 0x00001081) {
		return (load_dispatch_rams_200_seq(dp));
	}
	if (dp->dl_hash == LOAD_COUNTER_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_COUNTER.SEQ");
		seq_ptr = vbe16dec(dp->ram + 0x18);
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_SEQ_HASH ||
	    dp->dl_hash == 0x00001045) {
		return (load_control_store_200_seq(dp));
	}
	if (dp->dl_hash == PREP_RUN_SEQ_HASH) {
		prep_run_seq(dp);
	        return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == RESET_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "THAW 0");
		mp_seq_prepped = 0;
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == RUN_CHECK_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "THAW 1");
		mp_seq_prepped = 1;
		return ((int)DIPROC_RESPONSE_DONE);
	}

	if (dp->dl_hash == PREP_LOAD_DISPATCH_RAMS_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_LOAD_DISPATCH_RAMS.SEQ");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == CLR_BREAK_MASK_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLR_BREAK_MASK.SEQ");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == GET_MISC_ERRORS_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo GET_MISC_ERRORS.SEQ");
		dp->ram[0x18] = 0x1f;
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == HALT_SEQ_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo HALT.SEQ");
		*dp->ip = 0x6;
		return ((int)DIPROC_RESPONSE_DONE);
	}

	Trace(trace_diproc, "%s %s", dp->name, "Turbo *.SEQ");
	return ((int)DIPROC_RESPONSE_DONE);
	return (0);
}
