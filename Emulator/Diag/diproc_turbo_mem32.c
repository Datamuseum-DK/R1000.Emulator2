
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

#if !defined(HAS_Z000) || !defined(HAS_Z001)
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	uint8_t *ptr;

	// TAR
	ctx = CTX_Find(COMP_Z000);
	AN(ctx);
	ptr = (uint8_t *)(ctx + 1);
	memset(ptr, 0x00, (1 << 17) + 2 * (1 << 14));

	// TBR
	ctx = CTX_Find(COMP_Z001);
	AN(ctx);
	ptr = (uint8_t *)(ctx + 1);
	memset(ptr, 0x00, (1 << 17) + 2 * (1 << 14));

	sc_tracef(dp->name, "Turbo CLEAR_TAGSTORE.M32");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

static int
fill_memory_m32(const struct diagproc *dp)
{
#if !defined(HAS_Z006) || !defined(HAS_Z007) || !defined(HAS_Z008) || \
    !defined(HAS_Z009) || !defined(HAS_Z010) || !defined(HAS_Z011)
	(void)dp;
	return (0);
#else
	struct ctx *ctx;
	uint64_t *ptr, typ, val, cbit;
	int i;

	typ = vbe64dec(dp->ram + 0x18);		// P18IS8 DATA.TYP
	val = vbe64dec(dp->ram + 0x20);		// P20IS8 DATA.VAL
	cbit = vbe16dec(dp->ram + 0x29);	// P29IS2 DATA.CBITS

	// P28IS1 DATA.VPAR is loaded into DREGVP but not stored anywhere.

	// RAMAT
	ctx = CTX_Find(COMP_Z006);
	AN(ctx);
	ptr = (uint64_t *)(void*)(ctx + 1);
	for (i = 0; i < 1<<20; i++)
		ptr[i] = typ;

	// RAMAV
	ctx = CTX_Find(COMP_Z007);
	AN(ctx);
	ptr = (uint64_t *)(void*)(ctx + 1);
	for (i = 0; i < 1<<20; i++)
		ptr[i] = val;

	// RAMAC
	ctx = CTX_Find(COMP_Z008);
	AN(ctx);
	ptr = (uint64_t *)(void*)(ctx + 1);
	for (i = 0; i < 1<<20; i++)
		ptr[i] = cbit;

	// RAMBT
	ctx = CTX_Find(COMP_Z009);
	AN(ctx);
	ptr = (uint64_t *)(void*)(ctx + 1);
	for (i = 0; i < 1<<20; i++)
		ptr[i] = typ;

	// RAMBV
	ctx = CTX_Find(COMP_Z010);
	AN(ctx);
	ptr = (uint64_t *)(void*)(ctx + 1);
	for (i = 0; i < 1<<20; i++)
		ptr[i] = val;

	// RAMBC
	ctx = CTX_Find(COMP_Z011);
	AN(ctx);
	ptr = (uint64_t *)(void*)(ctx + 1);
	for (i = 0; i < 1<<20; i++)
		ptr[i] = cbit;

	sc_tracef(dp->name, "Turbo FILL_MEMORY.M32");
	return ((int)DIPROC_RESPONSE_DONE);
#endif
}

int v_matchproto_(diagprocturbo_t)
diagproc_turbo_mem32(const struct diagproc *dp)
{
	if (1 && dp->dl_hash == SET_HIT_M32_HASH) {
		sc_tracef(dp->name, "Turbo SET_HIT.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (1 && dp->dl_hash == CLEAR_HITS_M32_HASH) {
		sc_tracef(dp->name, "Turbo CLEAR_HITS.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (dp->dl_hash == CLEAR_PARITY_ERRORS_M32_HASH) {
		sc_tracef(dp->name, "Turbo CLEAR_PARITY_ERRORS.M32");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	
	if (dp->dl_hash == READ_NOVRAM_DATA_M32_HASH) {
		sc_tracef(dp->name, "Turbo READ_NOVRAM_DATA.M32");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_MEM0_NOVRAM", 0, 0x19, 12));
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_M32_HASH) {
		sc_tracef(dp->name, "Turbo READ_NOVRAM_INFO.M32");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_MEM0_NOVRAM", 0, 0x1f, 21));
	}
	if (dp->dl_hash == CLEAR_TAGSTORE_M32_HASH)
		return (clear_tagstore_m32(dp));
	if (dp->dl_hash == FILL_MEMORY_M32_HASH)
		return (fill_memory_m32(dp));
	return (0);
}
