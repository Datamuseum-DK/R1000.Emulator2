
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
load_control_store_200_ioc(const struct diagproc *dp)
{
#if !defined(HAS_Z023)
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

	if (dp->dl_hash == PREP_RUN_IOC_HASH) {
		sc_tracef(dp->name, "Turbo PREP_RUN.IOC");
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

	return (0);
}
