
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

static uint64_t *ioc_wcs;
static unsigned ioc_ptr;

static int
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
	sc_tracef(dp->name, "Turbo READ_LAST_PC.IOC (0x%x 0x%x 0x%x)", tram[2048], ctr1, tram[ctr1]);
	return ((int)DIPROC_RESPONSE_DONE);
}


static int
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
	sc_tracef(dp->name, "Turbo LOAD_CONTROL_STORE_200.IOC");
	return ((int)DIPROC_RESPONSE_DONE);
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
	if (dp->dl_hash == RUN_CHECK_IOC_HASH) {
		sc_tracef(dp->name, "START TRACING");
		mp_ioc_trace = 1;
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == READ_LAST_PC_IOC_HASH) {
		return (read_last_pc(dp));
	}
	if (dp->dl_hash == RESET_IOC_HASH) {
		return ((int)DIPROC_RESPONSE_DONE);
	}

	return (0);
}
