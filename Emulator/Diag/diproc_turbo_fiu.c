
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

static uint64_t *fiu_wcs;
static unsigned fiu_ptr;

static int
load_control_store_200_fiu(struct diagproc *dp)
{
#if !defined(HAS_Z022)
        (void)dp;
        return (0);
#else
        struct ctx *ctx;
        int n;
        uint64_t wcs, inp, inv;

        if (fiu_wcs == NULL) {
                ctx = CTX_Find(COMP_Z022);
                AN(ctx);
                fiu_wcs = (uint64_t *)(ctx + 1);
        }
        for (n = 0; n < 16; n++) {
                inp = vbe64dec(dp->ram + 0x18 + n * 8);
                inv = inp ^ ~0;
                wcs = 0;

		wcs <<= 1; wcs |= (inp >>  7) & 1; // 38
		wcs <<= 1; wcs |= (inp >> 15) & 1; // 37
		wcs <<= 1; wcs |= (inp >> 23) & 1; // 36
		wcs <<= 1; wcs |= (inp >> 31) & 1; // 35
		wcs <<= 1; wcs |= (inp >> 39) & 1; // 34
		wcs <<= 1; wcs |= (inp >> 47) & 1; // 33
		wcs <<= 1; wcs |= (inp >> 55) & 1; // 32
		wcs <<= 1; wcs |= (inp >> 45) & 1; // 31
		wcs <<= 1; wcs |= (inp >> 63) & 1; // 30
		wcs <<= 1; wcs |= (inp >>  6) & 1; // 29
		wcs <<= 1; wcs |= (inp >> 14) & 1; // 28
		wcs <<= 1; wcs |= (inp >> 22) & 1; // 27
		wcs <<= 1; wcs |= (inp >> 30) & 1; // 26
		wcs <<= 1; wcs |= (inp >> 38) & 1; // 25
		wcs <<= 1; wcs |= (inp >> 46) & 1; // 24
		wcs <<= 1; wcs |= (inp >>  2) & 1; // 23
		wcs <<= 1; wcs |= (inp >> 54) & 1; // 22
		wcs <<= 1; wcs |= (inp >> 62) & 1; // 21
		wcs <<= 1; wcs |= (inp >> 37) & 1; // 20
		wcs <<= 1; wcs |= (inp >> 10) & 1; // 19
		wcs <<= 1; wcs |= (inp >> 36) & 1; // 18
		wcs <<= 1; wcs |= (inp >> 52) & 1; // 17
		wcs <<= 1; wcs |= (inp >> 44) & 1; // 16
		wcs <<= 1; wcs |= (inp >> 60) & 1; // 15
		wcs <<= 1; wcs |= (inp >>  5) & 1; // 14
		wcs <<= 1; wcs |= (inp >> 13) & 1; // 13
		wcs <<= 1; wcs |= (inp >> 21) & 1; // 12
		wcs <<= 1; wcs |= (inp >> 29) & 1; // 11
		wcs <<= 1; wcs |= (inp >>  4) & 1; // 10
		wcs <<= 1; wcs |= (inp >> 12) & 1; // 9
		wcs <<= 1; wcs |= (inp >> 20) & 1; // 8
		wcs <<= 1; wcs |= (inp >> 28) & 1; // 7
		wcs <<= 1; wcs |= (inp >>  3) & 1; // 6
		wcs <<= 1; wcs |= (inp >> 11) & 1; // 5
		wcs <<= 1; wcs |= (inp >> 19) & 1; // 4
		wcs <<= 1; wcs |= (inp >> 27) & 1; // 3
		wcs <<= 1; wcs |= (inp >> 35) & 1; // 2
		wcs <<= 1; wcs |= (inp >> 43) & 1; // 1
		wcs <<= 1; wcs |= (inp >> 59) & 1; // 0
		fiu_wcs[fiu_ptr++] = wcs;
	}
	sc_tracef(dp->name, "Turbo LOAD_CONTROL_STORE_200.FIU");
	return (DIPROC_RESPONSE_DONE);
#endif
}

int
diagproc_turbo_fiu(struct diagproc *dp)
{
	if (dp->dl_hash == LOAD_COUNTER_FIU_HASH) {
		fiu_ptr = 0x100;
		return (0);
	}
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_FIU_HASH ||
            dp->dl_hash == 0x00001045) {
		return (load_control_store_200_fiu(dp));
	}

	return (0);
}
