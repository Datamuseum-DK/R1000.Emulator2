
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Chassis/r1000sc.h"
#include "Diag/diag.h"
#include "Diag/diagproc.h"
#include "Diag/exp_hash.h"
#include "Infra/context.h"
#include "Infra/vend.h"

static uint64_t *typ_rf;
static unsigned typ_ptr;

static uint64_t
get_wdr(const struct diagproc *dp, uint8_t offset)
{
	uint64_t wdr, m;
	unsigned v;
	int i;

	wdr = 0;
	m = 1ULL << 63;
	for (v = 0x80; v > 0x02; v >>= 1) {
		for (i = 11; i >= 0; i--) {
			if ((v == 0x20 && i < 4) || (v == 0x10 && i >= 8)) {
				// parity bits, always zero
			} else {
				if (dp->ram[offset + i] & v) {
					wdr |= m;
				}
				m >>= 1;
			}
		}
	}
	return (wdr);
}

static int
load_register_file_typ(const struct diagproc *dp)
{
	uint64_t wdr;
	int i;

	if (typ_rf == NULL) {
		typ_rf = (uint64_t*)CTX_GetRaw("TYP_RF", sizeof(uint64_t) << 10);
		memset(typ_rf, 0xff, sizeof(uint64_t) << 10);
	}

	for (i = 0; i < 16; i++, typ_ptr++) {
		wdr = get_wdr(dp, 0x18 + i * 12);
		typ_rf[typ_ptr] = ~wdr;

	}

	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_REGISTER_FILE_200.TYP");
	return ((int)DIPROC_RESPONSE_DONE);
}

static uint64_t *val_rf;
static unsigned val_ptr;

static int
load_register_file_val(const struct diagproc *dp)
{
	uint64_t wdr;
	int i;

	if (val_rf == NULL) {
		val_rf= (uint64_t*)CTX_GetRaw("VAL_RF", sizeof(uint64_t) << 10);
		memset(val_rf, 0xff, sizeof(uint64_t) << 10);
	}
	
	for (i = 0; i < 16; i++, val_ptr++) {
		wdr = get_wdr(dp, 0x18 + i * 12);
		val_rf[val_ptr] = ~wdr;
	}

	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_REGISTER_FILE_200.VAL");
	return ((int)DIPROC_RESPONSE_DONE);
}

static uint64_t *typ_wcs;

static int
load_control_store_200_typ(const struct diagproc *dp)
{
	int n;
	uint64_t wcs, inp, inv;

	if (typ_wcs == NULL) {
		typ_wcs = (uint64_t*)CTX_GetRaw("TYP_WCS", sizeof(uint64_t) << 14);
	}
	for (n = 0; n < 16; n++) {
		inp = vbe64dec(dp->ram + 0x18 + n * 8);
		inv = inp ^ ~0;

		// The pattern is:
		// WCS-    ------- Bit numbers ---------
		// byte0   7  15  23  31  39  47  55  63
		// byte1   6  14  22  30  38  46  54  62
		// byte2   5  13  21  **  37  45  53  61
		// byte3   4  12  20  28  36  44  52  60
		// byte4   3  11  19  27  35  43  51  59
		// byte5   2  10  18  26  34  42  50  29
		// bit#29 is the parity bit.

		wcs = 0;   wcs |= (inv >>  7) & 1; // 46
		wcs <<= 1; wcs |= (inv >> 15) & 1; // 45
		wcs <<= 1; wcs |= (inv >> 23) & 1; // 44
		wcs <<= 1; wcs |= (inv >> 31) & 1; // 43
		wcs <<= 1; wcs |= (inv >> 39) & 1; // 42
		wcs <<= 1; wcs |= (inv >> 47) & 1; // 41
		wcs <<= 1; wcs |= (inv >> 55) & 1; // 40
		wcs <<= 1; wcs |= (inv >> 63) & 1; // 39

		wcs <<= 1; wcs |= (inv >>  6) & 1; // 38
		wcs <<= 1; wcs |= (inv >> 14) & 1; // 37
		wcs <<= 1; wcs |= (inv >> 22) & 1; // 36
		wcs <<= 1; wcs |= (inv >> 30) & 1; // 35
		wcs <<= 1; wcs |= (inv >> 38) & 1; // 34
		wcs <<= 1; wcs |= (inv >> 46) & 1; // 33
		wcs <<= 1; wcs |= (inv >> 54) & 1; // 32
		wcs <<= 1; wcs |= (inv >> 62) & 1; // 31

		wcs <<= 1; wcs |= (inv >>  5) & 1; // 30
		wcs <<= 1; wcs |= (inv >> 13) & 1; // 29
		wcs <<= 1; wcs |= (inv >> 21) & 1; // 28
		wcs <<= 1; wcs |= (inv >> 37) & 1; // 27
		wcs <<= 1; wcs |= (inv >> 45) & 1; // 26
		wcs <<= 1; wcs |= (inv >> 53) & 1; // 25
		wcs <<= 1; wcs |= (inv >> 61) & 1; // 24

		wcs <<= 1; wcs |= (inp >>  4) & 1; // 23
		wcs <<= 1; wcs |= (inp >> 12) & 1; // 22
		wcs <<= 1; wcs |= (inp >> 20) & 1; // 21
		wcs <<= 1; wcs |= (inp >> 28) & 1; // 20
		wcs <<= 1; wcs |= (inp >> 36) & 1; // 19
		wcs <<= 1; wcs |= (inp >> 44) & 1; // 18
		wcs <<= 1; wcs |= (inp >> 52) & 1; // uncertain (=1)
		wcs <<= 1; wcs |= (inp >> 60) & 1; // uncertain (=1)

		wcs <<= 1; wcs |= (inp >>  3) & 1; // uncertain (=1)
		wcs <<= 1; wcs |= (inp >> 11) & 1; // 14
		wcs <<= 1; wcs |= (inp >> 19) & 1; // 13
		wcs <<= 1; wcs |= (inp >> 27) & 1; // 12
		wcs <<= 1; wcs |= (inp >> 35) & 1; // 11
		wcs <<= 1; wcs |= (inp >> 43) & 1; // 10
		wcs <<= 1; wcs |= (inp >> 51) & 1; // 9
		wcs <<= 1; wcs |= (inp >> 59) & 1; // 8

		wcs <<= 1; wcs |= (inp >>  2) & 1; // 7
		wcs <<= 1; wcs |= (inp >> 10) & 1; // 6
		wcs <<= 1; wcs |= (inp >> 18) & 1; // 5
		wcs <<= 1; wcs |= (inp >> 26) & 1; // 4
		wcs <<= 1; wcs |= (inp >> 34) & 1; // 3
		wcs <<= 1; wcs |= (inp >> 42) & 1; // 2
		wcs <<= 1; wcs |= (inp >> 50) & 1; // 1
		wcs <<= 1; wcs |= (inv >> 29) & 1; // 0
		typ_wcs[typ_ptr++] = wcs;
	}
	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_CONTROL_STORE_200.TYP");
	return ((int)DIPROC_RESPONSE_DONE);
}

static uint64_t *val_wcs;

static int
load_control_store_200_val(const struct diagproc *dp)
{
	int n;
	uint64_t wcs, inp, inv;

	if (val_wcs == NULL) {
		val_wcs = (uint64_t*)CTX_GetRaw("VAL_WCS", sizeof(uint64_t) << 14);
	}
	for (n = 0; n < 16; n++) {
		inp = vbe64dec(dp->ram + 0x18 + n * 8);
		inv = inp ^ ~0;

		// The pattern is:  (29 = parity)
		// WCS-    ------- Bit numbers ---------
		// byte0   7  15  23  31  39  47  55  63
		// byte1   6  14  22  30  38  46  54  62
		// byte2   5  13  21  **  37  45  53  61
		// byte3   4  12  20  28  36  44  52  60
		// byte4   3  11  19  27  35  43  51  59

		wcs = 0;   wcs |= (inv >>  7) & 1; // 39
		wcs <<= 1; wcs |= (inv >> 15) & 1; // 38
		wcs <<= 1; wcs |= (inv >> 23) & 1; // 37
		wcs <<= 1; wcs |= (inv >> 31) & 1; // 36
		wcs <<= 1; wcs |= (inv >> 39) & 1; // 35
		wcs <<= 1; wcs |= (inv >> 47) & 1; // 34
		wcs <<= 1; wcs |= (inv >> 55) & 1; // 33
		wcs <<= 1; wcs |= (inv >> 63) & 1; // 32

		wcs <<= 1; wcs |= (inv >>  6) & 1; // 31
		wcs <<= 1; wcs |= (inv >> 14) & 1; // 30
		wcs <<= 1; wcs |= (inv >> 22) & 1; // 29
		wcs <<= 1; wcs |= (inv >> 30) & 1; // 28
		wcs <<= 1; wcs |= (inv >> 38) & 1; // 27
		wcs <<= 1; wcs |= (inv >> 46) & 1; // 26
		wcs <<= 1; wcs |= (inv >> 54) & 1; // 25
		wcs <<= 1; wcs |= (inv >> 62) & 1; // 24

		wcs <<= 1; wcs |= (inv >>  5) & 1; // 23
		wcs <<= 1; wcs |= (inv >> 13) & 1; // 22
		wcs <<= 1; wcs |= (inv >> 21) & 1; // 21
		wcs <<= 1; wcs |= (inv >> 37) & 1; // 20
		wcs <<= 1; wcs |= (inv >> 45) & 1; // 19
		wcs <<= 1; wcs |= (inv >> 53) & 1; // 18
		wcs <<= 1; wcs |= (inv >> 61) & 1; // 17
		wcs <<= 1; wcs |= (inp >>  4) & 1; // 16

		wcs <<= 1; wcs |= (inp >> 12) & 1; // 15
		wcs <<= 1; wcs |= (inp >> 20) & 1; // 14
		wcs <<= 1; wcs |= (inp >> 28) & 1; // 13
		wcs <<= 1; wcs |= (inp >> 36) & 1; // 12
		wcs <<= 1; wcs |= (inp >> 44) & 1; // 11
		wcs <<= 1; wcs |= (inp >> 52) & 1; // 10
		wcs <<= 1; wcs |= (inp >> 60) & 1; // 9
		wcs <<= 1; wcs |= (inp >>  3) & 1; // 8

		wcs <<= 1; wcs |= (inp >> 11) & 1; // 7
		wcs <<= 1; wcs |= (inp >> 19) & 1; // 6
		wcs <<= 1; wcs |= (inp >> 27) & 1; // 5
		wcs <<= 1; wcs |= (inp >> 35) & 1; // 4
		wcs <<= 1; wcs |= (inp >> 43) & 1; // 3
		wcs <<= 1; wcs |= (inp >> 51) & 1; // 2
		wcs <<= 1; wcs |= (inp >> 59) & 1; // 1
		wcs <<= 1; wcs |= (inv >> 29) & 1; // 0

		val_wcs[val_ptr++] = wcs;
	}
	Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_CONTROL_STORE_200.VAL");
	return ((int)DIPROC_RESPONSE_DONE);
}

int v_matchproto_(diagprocturbo_t)
diagproc_turbo_typ(const struct diagproc *dp)
{
	if (dp->dl_hash == MF_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo MF.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_WCS_UIR_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_WCS_UIR.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == REG_TO_LOOP_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo REG_TO_LOOP.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == READ_B_REG_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_B_REG.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == PREP_READ_REG_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_READ_REG.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == RUN_NORMAL_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo RUN_NORMAL.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == PREP_RUN_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_RUN.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == PREP_WRITE_REG_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_WRITE_REG.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == WRITE_REG_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo WRITE_REG.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_BENIGN_UWORD_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_BENIGN_UWORD.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_WDR_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_WDR.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == ALIGN_CSA_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo ALIGN_CSA.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == CLEAR_PARITY_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_PARITY.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == READ_NOVRAM_DATA_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_DATA.TYP");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_TYP_NOVRAM", 1, 0x19, 7));
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_TYP_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_INFO.TYP");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_TYP_NOVRAM", 0, 0x20, 21));
	}
	if (dp->dl_hash == PREP_LOAD_REGISTER_FILE_TYP_HASH) {
		typ_ptr = 0;
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_LOAD_REGISTER_FILE.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_DIAG_COUNTER_TYP_HASH) {
		typ_ptr = 0x100;
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_DIAG_COUNTER.TYP");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_REGISTER_FILE_200_TYP_HASH ||
	    dp->dl_hash == 0x000017c5)
		return (load_register_file_typ(dp));
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_TYP_HASH ||
	    dp->dl_hash == 0x00001045) {
		return (load_control_store_200_typ(dp));
	}
	return (0);
}

int v_matchproto_(diagprocturbo_t)
diagproc_turbo_val(const struct diagproc *dp)
{
	if (dp->dl_hash == LOAD_WDR_VAL_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo LOAD_WDR.VAL");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == ALIGN_CSA_VAL_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo ALIGN_CSA.VAL");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == CLEAR_PARITY_VAL_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo CLEAR_PARITY.VAL");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == READ_NOVRAM_DATA_VAL_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_DATA.VAL");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_VAL_NOVRAM", 1, 0x19, 7));
	}
	if (dp->dl_hash == READ_NOVRAM_INFO_VAL_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo READ_NOVRAM_INFO.VAL");
		*dp->ip = 0x3;
		return(diag_load_novram(dp, "R1000_VAL_NOVRAM", 0, 0x20, 21));
	}
	if (dp->dl_hash == PREP_RUN_VAL_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_RUN.VAL");
		unsigned uad = vbe16dec(dp->ram + 0x18);
		if (uad == 0x100) {
			val_rf[0x1f] = 0;
		}
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == PREP_LOAD_REGISTER_FILE_VAL_HASH) {
		val_ptr = 0;
		Trace(trace_diproc, "%s %s", dp->name, "Turbo PREP_LOAD_REGISTER_FILE.VAL");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == LOAD_DIAG_COUNTER_VAL_HASH) {
		val_ptr = 0x100;
		return ((int)DIPROC_RESPONSE_DONE);
		return (0);
	}
	if (dp->dl_hash == LOAD_REGISTER_FILE_200_VAL_HASH ||
	    dp->dl_hash == 0x000017c5)
		return (load_register_file_val(dp));
	if (dp->dl_hash == LOAD_CONTROL_STORE_200_VAL_HASH ||
	    dp->dl_hash == 0x00001045) {
		return (load_control_store_200_val(dp));
	}
	if (dp->dl_hash == RUN_NORMAL_VAL_HASH) {
		Trace(trace_diproc, "%s %s", dp->name, "Turbo RUN_NORMAL.VAL");
		return ((int)DIPROC_RESPONSE_DONE);
	}
	if (dp->dl_hash == READ_RF_B_VAL_HASH) {
		unsigned ptr = ~vbe16dec(dp->ram + 0x31) & 0x3ff;
		Trace(trace_diproc, "%s %s [0x%x]", dp->name, "Turbo READ_RF_B.TYP", ptr);
		if (ptr < 1024)
			vbe64enc(dp->ram + 0x33, val_rf[ptr]);
		return ((int)DIPROC_RESPONSE_DONE);
	}
	return (0);
}
