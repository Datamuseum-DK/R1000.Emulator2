
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

#if defined(HAS_Z023)
static uint64_t *ioc_wcs;
#endif
static unsigned ioc_ptr;

static int
read_last_pc(const struct diagproc *dp)
{
#if !defined(HAS_Z023)
	fprintf(stderr, "NO Z023\n");
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	uint8_t *ptr;
	uint16_t *tram;
	unsigned *ctr;
	unsigned ctr1;

	(void)dp;
	ctx = CTX_Find(COMP_Z023);
	AN(ctx);
	ptr = (uint8_t *)(void*)(ctx + 1);
        tram = (uint16_t *)(void*)(ptr + (8 << 14));
        ctr = (unsigned *)(void*)(ptr + (8 << 14) + (2 << 11));
	ctr1 = *ctr;
	ctr1 -= 4;
	ctr1 &= (1<<11) - 1;
	vbe16enc(dp->ram + 0x18, tram[ctr1] & 0x3fff);
	sc_tracef(dp->name, "Turbo READ_LAST_PC.IOC");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}


static int
load_control_store_200_ioc(const struct diagproc *dp)
{
#if !defined(HAS_Z023)
	fprintf(stderr, "NO Z023\n");
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	int n;
	uint64_t inp;

	if (ioc_wcs == NULL) {
		ctx = CTX_Find(COMP_Z023);
		AN(ctx);
		ioc_wcs = (uint64_t *)(void*)(ctx + 1);
	}
	for (n = 0; n < 16; n++) {
		inp = vbe16dec(dp->ram + 0x18 + n * 2);
		ioc_wcs[ioc_ptr++] = inp & 0xffff;
	}
	sc_tracef(dp->name, "Turbo LOAD_CONTROL_STORE_200.IOC");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

int v_matchproto_(diagprocturbo_t)
diagproc_turbo_ioc(const struct diagproc *dp)
{

	if (dp->dl_hash == LOAD_PAREG_IOC_HASH) {
		sc_tracef(dp->name, "Turbo LOAD_PAREG.IOC");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == PREP_RUN_IOC_HASH) {
		sc_tracef(dp->name, "Turbo PREP_RUN.IOC");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_UIR_IOC_HASH) {
		sc_tracef(dp->name, "Turbo LOAD_UIR.IOC");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == DISABLE_TIMERS_IOC_HASH) {
		sc_tracef(dp->name, "Turbo DISABLE_TIMERS.IOC");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_WCS_ADDRESS_IOC_HASH) {
		sc_tracef(dp->name, "Turbo LOAD_WCS_ADDRESS.IOC");
		ioc_ptr = vbe16dec(dp->ram + 0x2e);
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_IOC_HASH ||
	    dp->dl_hash == 0x00000500) {
		return (load_control_store_200_ioc(dp));
	}
	if (dp->dl_hash == READ_LAST_PC_IOC_HASH) {
		return (read_last_pc(dp));
	}

	return (0);
}
