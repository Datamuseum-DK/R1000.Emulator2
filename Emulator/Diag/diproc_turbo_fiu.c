
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

#if defined(HAS_Z022)
static uint64_t *fiu_wcs;
#endif
static unsigned fiu_ptr;

static int
load_control_store_200_fiu(const struct diagproc *dp)
{
#if !defined(HAS_Z022)
	fprintf(stderr, "NO Z022\n");
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	int n;
	uint64_t wcs, inp;

	if (fiu_wcs == NULL) {
		ctx = CTX_Find(COMP_Z022);
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
	sc_tracef(dp->name, "Turbo LOAD_CONTROL_STORE_200.FIU");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

static int
load_hram_0_32(const struct diagproc *dp)
{
#if !defined(HAS_Z024)
	fprintf(stderr, "NO Z024\n");
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	uint8_t *ptr;
	unsigned n;
	uint8_t b0;
	uint8_t b1;
	uint8_t b2;
	uint8_t b3;
	uint8_t b4;
	uint8_t b5;
	uint8_t b6;
	uint8_t b7;

	ctx = CTX_Find(COMP_Z024);
	AN(ctx);
	ptr = (uint8_t *)(void*)(ctx + 1);
	for (n = 0; n < 1024; n++) {
		b0 = (n >> 9) & 1;
		b1 = (n >> 8) & 1;
		b2 = (n >> 7) & 1;
		b3 = (n >> 6) & 1;
		b4 = (n >> 5) & 1;
		b5 = (n >> 4) & 1;
		b6 = (n >> 3) & 1;
		b7 = (n >> 2) & 1;
		ptr[n] = 0x0f;
		ptr[n] ^= (b0^b4) << 3;
		ptr[n] ^= (b1^b5) << 2;
		ptr[n] ^= (b2^b7) << 1;
		ptr[n] ^= (b3^b6) << 0;
	}
	sc_tracef(dp->name, "Turbo LOAD_HRAM_32_0._FIU");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

static int
load_hram_1(const struct diagproc *dp)
{
#if !defined(HAS_Z024)
	fprintf(stderr, "NO Z024\n");
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	uint8_t *ptr;
	unsigned n;
	uint8_t b0;
	uint8_t b1;
	uint8_t b2;
	uint8_t b3;
	uint8_t b6;
	uint8_t b7;
	uint8_t b8;
	uint8_t b9;

	ctx = CTX_Find(COMP_Z024);
	AN(ctx);
	ptr = (uint8_t *)(void*)(ctx + 1);
	ptr += 1<<10;
	for (n = 0; n < 1024; n++) {
		b0 = (n >> 9) & 1;
		b1 = (n >> 8) & 1;
		b2 = (n >> 7) & 1;
		b3 = (n >> 6) & 1;
		b6 = (n >> 3) & 1;
		b7 = (n >> 2) & 1;
		b8 = (n >> 1) & 1;
		b9 = (n >> 0) & 1;
		ptr[n] = 0x0f;
		ptr[n] ^= (b0 ^ b9) << 3;
		ptr[n] ^= (b1 ^ b8) << 2;
		ptr[n] ^= (b2 ^ b7) << 1;
		ptr[n] ^= (b3 ^ b6) << 0;
	}
	sc_tracef(dp->name, "Turbo LOAD_HRAM_1.FIU");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

static int
load_counter(const struct diagproc *dp)
{
	fiu_ptr = vbe16dec(dp->ram + 0x28);
#if !defined(HAS_Z025) || !defined(HAS_Z026)
	fprintf(stderr, "NO Z025 Z026\n");
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	uint32_t *ptr;

	ctx = CTX_Find(COMP_Z025);
	AN(ctx);
	ptr = (unsigned *)(void*)(ctx + 1);
	*ptr = vbe16dec(dp->ram + 0x26);

	ctx = CTX_Find(COMP_Z026);
	AN(ctx);
	ptr = (unsigned *)(void*)(ctx + 1);
	*ptr = vbe16dec(dp->ram + 0x28);

	sc_tracef(dp->name, "Turbo LOAD_COUNTER.FIU");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

int v_matchproto_(diagprocturbo_t)
diagproc_turbo_fiu(const struct diagproc *dp)
{
	if (dp->dl_hash == LOAD_COUNTER_FIU_HASH) {
		return (load_counter(dp));
	}
	if (0 && dp->dl_hash == INIT_MRU_FIU_HASH) {
		sc_tracef(dp->name, "Turbo INIT_MRU.FIU");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == CLEAR_PARITY_FIU_HASH) {
		sc_tracef(dp->name, "Turbo CLEAR_PARITY.FIU");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_HRAM_32_0_FIU_HASH) {
		sc_tracef(dp->name, "Turbo LOAD_HRAM_32_0.FIU");
		return ((int)DIPROC_RESPONSE_DONE);
		return(load_hram_0_32(dp));
	}
	if (dp->dl_hash == LOAD_HRAM_1_FIU_HASH) {
		sc_tracef(dp->name, "Turbo LOAD_HRAM_1.FIU");
		return ((int)DIPROC_RESPONSE_DONE);
		return(load_hram_1(dp));
	}
	if (dp->dl_hash == READ_NOVRAM_DATA_FIU_HASH) {
		sc_tracef(dp->name, "Turbo READ_NOVRAM_DATA.FIU");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_FIU_NOVRAM", 1, 0x22, 8));
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_FIU_HASH) {
		sc_tracef(dp->name, "Turbo READ_NOVRAM_INFO.FIU");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_FIU_NOVRAM", 0, 0x27, 21));
	}
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_FIU_HASH ||
	    dp->dl_hash == 0x00001045) {
		return (load_control_store_200_fiu(dp));
	}

	return (0);
}
