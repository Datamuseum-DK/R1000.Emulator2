
#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Chassis/r1000sc.h"
#include "Diag/diag.h"
#include "Infra/context.h"

#include "Diag/diproc_fiu_wcs.h"
#include "Diag/diproc_seq_dec.h"
#include "Diag/diproc_seq_wcs.h"
#include "Diag/diproc_typ_wcs.h"
#include "Diag/diproc_val_wcs.h"

typedef int board_func_t(struct diagproc_exp_priv *dep, uint8_t length);

#define BITPOS(octet, bitno, xor) \
	do { \
		w += w; \
		w += xor ^ ((dep->ram[u + 7 - bitno] >> (7 - octet)) & 1); \
	} while(0)

static board_func_t fiu_board;
static board_func_t ioc_board;
static board_func_t mem0_board;
static board_func_t seq_board;
static board_func_t typ_board;
static board_func_t val_board;

struct diagproc_exp_priv {
	const char	*name;
	unsigned	state;
	unsigned	counter;
	uint8_t		*ram;
	uint8_t		*ip;
	uint8_t		*dst1;
	uint8_t		*dst2;
	uint16_t	*dst3;
	board_func_t	*board;
};

#define SET_PT(dep)	do { *((dep)->ip) |= 2; } while (0)
#define SET_PX(dep)	do { *((dep)->ip) |= 1; } while (0)
#define CLR_PT(dep)	do { *((dep)->ip) &= ~2; } while (0)
#define CLR_PX(dep)	do { *((dep)->ip) &= ~1; } while (0)

void
diagproc_exp_init(struct diagproc_exp_priv **depp, const char *name)
{
	struct diagproc_exp_priv *dep;

	dep = calloc(sizeof *dep, 1);
	AN(dep);
	dep->name = name;
	*depp = dep;
	if (strstr(name, "FIU.fiu") != NULL) {
		dep->board = fiu_board;
	} else if (strstr(name, "IOC.ioc") != NULL) {
		dep->board = ioc_board;
	} else if (strstr(name, "MEM0.mem32")) {
		dep->board = mem0_board;
	} else if (strstr(name, "SEQ.seq") != NULL) {
		dep->board = seq_board;
	} else if (strstr(name, "TYP.typ") != NULL) {
		dep->board = typ_board;
	} else if (strstr(name, "VAL.val") != NULL) {
		dep->board = val_board;
	} else {
		fprintf(stderr, "Unrecognized DIPROC: %s\n", name);
		exit(2);
	}
}

static void
upload(uint8_t *ptr, const char *hexstr)
{
	uint8_t byte;

	while (*hexstr) {
		while (isspace(*hexstr))
			hexstr++;
		byte = digittoint(*hexstr++) << 4;
		byte |= digittoint(*hexstr++);
		*ptr++ = byte;
	}
}

static int
ioc_board(struct diagproc_exp_priv *dep, uint8_t length)
{
	struct ctx *ctx;
	uint8_t u;

	if (length == 0x40 && dep->ram[0x10] == 0x38) {
		ctx = CTX_Find("IOC.ioc_52.CSRAM0");
		AN(ctx);
		dep->dst1 = (uint8_t*)(ctx + 1) + 0x100;
		ctx = CTX_Find("IOC.ioc_52.CSRAM1");
		AN(ctx);
		dep->dst2 = (uint8_t*)(ctx + 1) + 0x100;
	}

	if (length == 0x51 && dep->ram[0x10] == 0x30) {
		sc_tracef(dep->name, "Exp load_wcs_address.ioc");
		return (1);
	}

	if ((length == 0x40 || length == 0x28) && dep->ram[0x10] == 0x38) {
		sc_tracef(dep->name, "Exp load_control_store_200.ioc");
		for(u = 0x18; u < 0x38; u += 2) {
			*dep->dst1++ = dep->ram[u];
			*dep->dst2++ = dep->ram[u + 1];
		}
		return (1);

	}
	return (0);
}

static int
fiu_board(struct diagproc_exp_priv *dep, uint8_t length)
{
	struct ctx *ctx;
	uint8_t *dst;
	uint16_t ctr;
	uint64_t w;
	unsigned u;

	if (length == 0x52 && dep->ram[0x10] == 0x2f) {
		sc_tracef(dep->name, "Exp read_novram_data.fiu");
		upload(dep->ram + 0x22, "2c272b0204b6a1");
		SET_PT(dep);
		return(1);
	}

        if (length == 0x0f && dep->ram[0x10] == 0x18) {
		sc_tracef(dep->name, "Exp clear_parity.fiu");
		return(1);
	}

        if (length == 0x4d && dep->ram[0x10] == 0x38) {
		sc_tracef(dep->name, "Exp load_counter.fiu");
		return(1);
	}

	if (length == 0x4f && dep->ram[0x10] == 0x38) {
		sc_tracef(dep->name, "Exp load_hram_1.fiu");
		/*
		 * 0x008 0x040 1
		 * 0x004 0x080 2
		 * 0x002 0x100 4
		 * 0x001 0x200 8
		 */
		ctx = CTX_Find("FIU.fiu_55.HRAM1");
		AN(ctx);
		dst = (uint8_t*)(ctx + 1);
		for (ctr = 0; ctr < 1024; ctr++) {
			*dst = 0xf;
			if (((ctr >> 3) ^ (ctr >> 6)) & 1)
				*dst &= ~1;
			if (((ctr >> 2) ^ (ctr >> 7)) & 1)
				*dst &= ~2;
			if (((ctr >> 1) ^ (ctr >> 8)) & 1)
				*dst &= ~4;
			if (((ctr >> 0) ^ (ctr >> 9)) & 1)
				*dst &= ~8;
			dst++;
		}
		return (1);
	}

	if (length == 0x67 && dep->ram[0x10] == 0x3f) {
		sc_tracef(dep->name, "Exp load_hram_32_0.fiu");
		/*
		 * 0x008 0x040 1
		 * 0x004 0x080 2
		 * 0x010 0x100 4
		 * 0x020 0x200 8
		 */
		ctx = CTX_Find("FIU.fiu_55.HRAM0");
		AN(ctx);
		dst = (uint8_t*)(ctx + 1);
		for (ctr = 0; ctr < 1024; ctr++) {
			*dst = 0x0f;
			if (((ctr >> 3) ^ (ctr >> 6)) & 1)
				*dst &= ~1;
			if (((ctr >> 2) ^ (ctr >> 7)) & 1)
				*dst &= ~2;
			if (((ctr >> 4) ^ (ctr >> 8)) & 1)
				*dst &= ~4;
			if (((ctr >> 5) ^ (ctr >> 9)) & 1)
				*dst &= ~8;
			dst++;
		}
		return (1);
	}
	if (length == 0x9a && dep->ram[0x10] == 0x99) {
		ctx = CTX_Find("FIU.fiu_36.WCSRAM");
		AN(ctx);
		dep->dst1 = (uint8_t*)(ctx + 1) + 0x800;
	}
	if ((length == 0x9a || length == 0x88) && dep->ram[0x10] == 0x99) {
		sc_tracef(dep->name, "Exp load_control_store_200.fiu");
		for(u = 0x18; u < 0x98; u += 8) {
			w = 0;
			FIU_WCS_OFFS_LIT_0();
			FIU_WCS_OFFS_LIT_1();
			FIU_WCS_OFFS_LIT_2();
			FIU_WCS_OFFS_LIT_3();
			FIU_WCS_OFFS_LIT_4();
			FIU_WCS_OFFS_LIT_5();
			FIU_WCS_OFFS_LIT_6();
			FIU_WCS_OREG_SRC();
			FIU_WCS_LFL_0();
			FIU_WCS_LFL_1();
			FIU_WCS_LFL_2();
			FIU_WCS_LFL_3();
			FIU_WCS_LFL_4();
			FIU_WCS_LFL_5();
			FIU_WCS_LFL_6();
			FIU_WCS_LENGTH_SRC();
			FIU_WCS_LFREG_CNTL_0();
			FIU_WCS_LFREG_CNTL_1();
			FIU_WCS_FILL_MODE_SRC();
			FIU_WCS_OFFS_SRC();
			FIU_WCS_LOAD_OREG();
			FIU_WCS_LOAD_TAR();
			FIU_WCS_LOAD_VAR();
			FIU_WCS_LOAD_MDR();
			FIU_WCS_OP_SEL_0();
			FIU_WCS_OP_SEL_1();
			FIU_WCS_VMUX_SEL_0();
			FIU_WCS_VMUX_SEL_1();
			FIU_WCS_TIVI_SRC_0();
			FIU_WCS_TIVI_SRC_1();
			FIU_WCS_TIVI_SRC_2();
			FIU_WCS_TIVI_SRC_3();
			FIU_WCS_MEM_START_0();
			FIU_WCS_MEM_START_1();
			FIU_WCS_MEM_START_2();
			FIU_WCS_MEM_START_3();
			FIU_WCS_MEM_START_4();
			FIU_WCS_RDATA_SRC();
			FIU_WCS_PARITY();
			memcpy(dep->dst1, &w, sizeof w);
			dep->dst1 += sizeof w;
		}
		return(1);
	}
	return (0);
}

static int
mem32_board(struct diagproc_exp_priv *dep, uint8_t length, int board)
{
	struct ctx *ctx;
	uint8_t *dst;
	unsigned u;

	(void)board;

	if (length == 0x4b && dep->ram[0x10] == 0x2a) {
		sc_tracef(dep->name, "Exp read_novram_data.m32");
		upload(dep->ram + 0x19, "2f28ee02060000000000b6ee");
		SET_PT(dep);
		return(1);
	}

        if (length == 0x1e && dep->ram[0x10] == 0x18) {
		sc_tracef(dep->name, "Exp clear_parity_errors.m32");
		return(1);
	}

        if (length == 0x23 && dep->ram[0x10] == 0x19) {
		sc_tracef(dep->name, "Exp set_hit.m32");
		return(1);
	}

        if (length == 0x0d && dep->ram[0x10] == 0x18) {
		sc_tracef(dep->name, "Exp clear_hits.m32");
		return(1);
	}

	if (length == 0x41 && dep->ram[0x10] == 0x22) {
		sc_tracef(dep->name, "Exp clear_tagstore.m32");

		ctx = CTX_Find("MEM0.mem32_09.TAR");
		AN(ctx);
		dst = (uint8_t*)(ctx + 1);
		memset(dst, 0, 0x20000);
		for(u = 0; u < 0x4000; u++)
			dst[u * 8] = 0x7f;

		ctx = CTX_Find("MEM0.mem32_12.TBR");
		AN(ctx);
		dst = (uint8_t*)(ctx + 1);
		memset(dst, 0, 0x20000);
		for(u = 0; u < 0x4000; u++)
			dst[u * 8] = 0x7f;

		return(1);
	}
	return (0);
}

static int
mem0_board(struct diagproc_exp_priv *dep, uint8_t length)
{
	return (mem32_board(dep, length, 0));
}

static int
seq_board(struct diagproc_exp_priv *dep, uint8_t length)
{
	struct ctx *ctx;
	uint8_t *dst;
	uint16_t *dst2;
	uint16_t off;
	uint64_t w;
	unsigned u;

	if (length == 0x45 && dep->ram[0x10] == 0x27) {
		sc_tracef(dep->name, "Exp read_novram_data.seq");
		upload(dep->ram + 0x1a, "2d294b0205b82c");
		SET_PT(dep);
		return (1);
	}

        if (length == 0x1e && dep->ram[0x10] == 0x21) {
		sc_tracef(dep->name, "Exp clear_parity.seq");
		return(1);
	}

#if 0
        if (length == 0x45 && dep->ram[0x10] == 0x3d) {
		sc_tracef(dep->name, "Exp prep_load_dispatch_rams.seq");
		return(1);
	}
#endif

        if (length == 0x12 && dep->ram[0x10] == 0x1a) {
		sc_tracef(dep->name, "Exp load_counter.seq");
		return(1);
	}

	if (length == 0x9a && dep->ram[0x10] == 0x99) {
		ctx = CTX_Find("SEQ.seq_70.WCS");
		AN(ctx);
		dep->dst1 = (uint8_t*)(ctx + 1) + 0x800;
	}
	if ((length == 0x9a || length == 0x88) && dep->ram[0x10] == 0x99) {
		sc_tracef(dep->name, "Exp load_control_store_200.seq");
		for(u = 0x18; u < 0x98; u += 8) {
			w = 0;
			SEQ_WCS_BRANCH_ADR_0();
			SEQ_WCS_BRANCH_ADR_1();
			SEQ_WCS_BRANCH_ADR_2();
			SEQ_WCS_BRANCH_ADR_3();
			SEQ_WCS_BRANCH_ADR_4();
			SEQ_WCS_BRANCH_ADR_5();
			SEQ_WCS_BRANCH_ADR_6();
			SEQ_WCS_BRANCH_ADR_7();
			SEQ_WCS_BRANCH_ADR_8();
			SEQ_WCS_BRANCH_ADR_9();
			SEQ_WCS_BRANCH_ADR_10();
			SEQ_WCS_BRANCH_ADR_11();
			SEQ_WCS_BRANCH_ADR_12();
			SEQ_WCS_BRANCH_ADR_13();
			SEQ_WCS_PARITY();
			SEQ_WCS_LATCH();
			SEQ_WCS_BR_TYPE_0();
			SEQ_WCS_BR_TYPE_1();
			SEQ_WCS_BR_TYPE_2();
			SEQ_WCS_BR_TYPE_3();
			SEQ_WCS_BR_TIMING_0();
			SEQ_WCS_BR_TIMING_1();
			SEQ_WCS_COND_SEL_0();
			SEQ_WCS_COND_SEL_1();
			SEQ_WCS_COND_SEL_2();
			SEQ_WCS_COND_SEL_3();
			SEQ_WCS_COND_SEL_4();
			SEQ_WCS_COND_SEL_5();
			SEQ_WCS_COND_SEL_6();
			SEQ_WCS_LEX_ADR_0();
			SEQ_WCS_LEX_ADR_1();
			SEQ_WCS_EN_MICRO();
			SEQ_WCS_INT_READS_0();
			SEQ_WCS_INT_READS_1();
			SEQ_WCS_INT_READS_2();
			SEQ_WCS_RANDOM_0();
			SEQ_WCS_RANDOM_1();
			SEQ_WCS_RANDOM_2();
			SEQ_WCS_RANDOM_3();
			SEQ_WCS_RANDOM_4();
			SEQ_WCS_RANDOM_5();
			SEQ_WCS_RANDOM_6();
			memcpy(dep->dst1, &w, sizeof w);
			dep->dst1 += sizeof w;
		}
		return (1);
	}
	if (length == 0xb2 && dep->ram[0x10] == 0x9b) {
		ctx = CTX_Find("SEQ.seq_48.CLSDC");
		AN(ctx);
		dep->dst1 = (uint8_t*)(ctx + 1);

		ctx = CTX_Find("SEQ.seq_49.DECRM8");
		AN(ctx);
		dep->dst2 = (uint8_t*)(ctx + 1);

		ctx = CTX_Find("SEQ.seq_49.DECRM0");
		AN(ctx);
		dep->dst3 = (uint16_t*)(ctx + 1);
	}
	if ((length == 0xb2 || length == 0x8a) && dep->ram[0x10] == 0x9b) {
		sc_tracef(dep->name, "Exp load_dispatch_rams_200.seq");
		off = dep->ram[0x18] << 8;
		off |= dep->ram[0x19];
		if (!dep->ram[0x11])
			off >>= 6;

		dst = dep->dst1;
		if (!dep->ram[0x11])
			dst += 1024;
		dst += off;
		for(u = 0x1a; u < 0x9a; u += 8) {
			w = 0;
			SEQ_DEC_CUR_CLASS_0();
			SEQ_DEC_CUR_CLASS_1();
			SEQ_DEC_CUR_CLASS_2();
			SEQ_DEC_CUR_CLASS_3();
			*dst++ = w;
		}

		dst2 = dep->dst3;
		if (!dep->ram[0x11])
			dst2 += 1024;
		dst2 += off;

		for(u = 0x1a; u < 0x9a; u += 8) {
			w = 0;
			SEQ_DEC_USES_TOS();
			SEQ_DEC_IBUFF_FILL();
			SEQ_DEC_UADR_0();
			SEQ_DEC_UADR_1();
			SEQ_DEC_UADR_2();
			SEQ_DEC_UADR_3();
			SEQ_DEC_UADR_4();
			SEQ_DEC_UADR_5();
			SEQ_DEC_UADR_6();
			SEQ_DEC_UADR_7();
			SEQ_DEC_UADR_8();
			SEQ_DEC_UADR_9();
			SEQ_DEC_UADR_10();
			SEQ_DEC_UADR_11();
			SEQ_DEC_UADR_12();
			SEQ_DEC_PARITY();
			*dst2++ = w;
		}

		dst = dep->dst2;
		if (!dep->ram[0x11])
			dst += 1024;
		dst += off;
		for(u = 0x1a; u < 0x9a; u += 8) {
			w = 0;
			SEQ_DEC_CSA_VALID_1();
			SEQ_DEC_CSA_VALID_2();
			SEQ_DEC_CSA_FREE_0();
			SEQ_DEC_CSA_FREE_1();
			SEQ_DEC_CSA_VALID_0();
			SEQ_DEC_MEM_STRT_0();
			SEQ_DEC_MEM_STRT_1();
			SEQ_DEC_MEM_STRT_2();
			*dst++ = w;
		}
		return (1);
	}
	return (0);
}

static uint64_t
get_wdr(struct diagproc_exp_priv *dep, uint8_t offset)
{
	uint64_t wdr, m;
	unsigned v;
	int i;

	//printf("%s %02x: ", dep->name, offset);
	wdr = 0;
	m = 1ULL << 63;
	//for (i = 0; i < 12; i++)
	//	printf("%02x ", dep->ram[offset + i]);
	for (v = 0x80; v > 0x02; v >>= 1) {
		for (i = 11; i >= 0; i--) {
			if (v == 0x20 && i < 4)
				continue; // parity
			if (v == 0x10 && i >= 8)
				continue; // parity
			if (dep->ram[offset + i] & v) {
				//putchar('#');
				wdr |= m;
			} else {
				//putchar('-');
			}
			m >>= 1;
		}
	}
	//printf("=> %016jx\n", (uintmax_t)wdr);
	return (wdr);
}

static int
typ_val_rfload(struct diagproc_exp_priv *dep, uint8_t length, const char *aram, const char *bram, const char *suf)
{
	uint64_t wdr;
	unsigned w;
	struct ctx *ctx;
	uint8_t *dst;

	if (dep->ram[0x10] != 0xd9)
		return(0);

	if (length == 0xdc) {
		// LOAD_REGISTER_FILE_200.TYP (complete download)
		ctx = CTX_Find(aram);
		AN(ctx);
		dst = (uint8_t*)(ctx + 1);
		dep->dst1 = dst;

		ctx = CTX_Find(bram);
		AN(ctx);
		dst = (uint8_t*)(ctx + 1);
		dep->dst2 = dst;
	}
	if (length == 0xdc || length == 0xc8) {
		// LOAD_REGISTER_FILE_200.TYP (complete & modify downloads)
		sc_tracef(dep->name, "Exp load_register_file_200.%s", suf);
		for (w = 0x18; w < 0xd8; w += 12) {
			wdr = get_wdr(dep, w);
			memcpy(dep->dst1, &wdr, sizeof wdr);
			dep->dst1 += 8;
			memcpy(dep->dst2, &wdr, sizeof wdr);
			dep->dst2 += 8;
			fflush(stdout);
		}
		return (1);
	}
	return (0);
}

static int
typ_board(struct diagproc_exp_priv *dep, uint8_t length)
{
	struct ctx *ctx;
	uint64_t w;
	unsigned u;

	if (length == 0x40 && dep->ram[0x10] == 0x26) {
		sc_tracef(dep->name, "Exp read_novram_data.typ");
		upload(dep->ram + 0x19, "2b29dc0204b796");
		SET_PT(dep);
		return (1);
	}

        if (length == 0x0f && dep->ram[0x10] == 0x18) {
		sc_tracef(dep->name, "Exp clear_parity.typ");
		return(1);
	}

        if (length == 0x23 && dep->ram[0x10] == 0x27) {
		sc_tracef(dep->name, "Exp prep_load_register_file.typ");
		return(1);
	}

        if (length == 0x14 && dep->ram[0x10] == 0x1a) {
		sc_tracef(dep->name, "Exp load_diag_counter.typ");
		return(1);
	}

	if (typ_val_rfload(dep, length, "TYP.typ_16.ARAM", "TYP.typ_18.BRAM", "typ"))
		return (1);

	if (length == 0x9a && dep->ram[0x10] == 0x99) {
		ctx = CTX_Find("TYP.typ_50.WCSRAM");
		AN(ctx);
		dep->dst1 = (uint8_t*)(ctx + 1) + 0x800;
	}
	if ((length == 0x9a || length == 0x88) && dep->ram[0x10] == 0x99) {
		sc_tracef(dep->name, "Exp load_control_store_200.typ");
		for(u = 0x18; u < 0x98; u += 8) {
			w = 0;
			TYP_WCS_A_0();
			TYP_WCS_A_1();
			TYP_WCS_A_2();
			TYP_WCS_A_3();
			TYP_WCS_A_4();
			TYP_WCS_A_5();
			TYP_WCS_B_0();
			TYP_WCS_B_1();

			TYP_WCS_B_2();
			TYP_WCS_B_3();
			TYP_WCS_B_4();
			TYP_WCS_B_5();
			TYP_WCS_FRAME_0();
			TYP_WCS_FRAME_1();
			TYP_WCS_FRAME_2();
			TYP_WCS_FRAME_3();

			TYP_WCS_FRAME_4();
			TYP_WCS_C_LIT_0();
			TYP_WCS_C_LIT_1();
			TYP_WCS_RAND_0();
			TYP_WCS_RAND_1();
			TYP_WCS_RAND_2();
			TYP_WCS_RAND_3();
			TYP_WCS_C_0();

			TYP_WCS_C_1();
			TYP_WCS_C_2();
			TYP_WCS_C_3();
			TYP_WCS_C_4();
			TYP_WCS_C_5();
			TYP_WCS_PRIV_CHK_0();
			TYP_WCS_PRIV_CHK_1();
			TYP_WCS_PRIV_CHK_2();

			TYP_WCS_C_MUX_SEL();
			TYP_WCS_ALU_FUNC_0();
			TYP_WCS_ALU_FUNC_1();
			TYP_WCS_ALU_FUNC_2();
			TYP_WCS_ALU_FUNC_3();
			TYP_WCS_ALU_FUNC_4();
			TYP_WCS_C_SOURCE();
			TYP_WCS_MAR_CNTL_0();
			TYP_WCS_MAR_CNTL_1();
			TYP_WCS_MAR_CNTL_2();
			TYP_WCS_MAR_CNTL_3();
			TYP_WCS_CSA_CNTL_0();
			TYP_WCS_CSA_CNTL_1();
			TYP_WCS_CSA_CNTL_2();
			TYP_WCS_PARITY();
			memcpy(dep->dst1, &w, sizeof w);
			dep->dst1 += sizeof w;
		}
		return (1);
	}

	return (0);
}

static int
val_board(struct diagproc_exp_priv *dep, uint8_t length)
{
	struct ctx *ctx;
	uint64_t w;
	unsigned u;

	if (length == 0x40 && dep->ram[0x10] == 0x26) {
		sc_tracef(dep->name, "Exp read_novram_data.val");
		upload(dep->ram + 0x19, "2a28060103b796");
		SET_PT(dep);
		return (1);
	}

        if (length == 0x0f && dep->ram[0x10] == 0x18) {
		sc_tracef(dep->name, "Exp clear_parity.val");
		return(1);
	}

        if (length == 0x14 && dep->ram[0x10] == 0x1a) {
		sc_tracef(dep->name, "Exp load_diag_counter.val");
		return(1);
	}

        if (length == 0x22 && dep->ram[0x10] == 0x26) {
		sc_tracef(dep->name, "Exp prep_load_register_file.val");
		return(1);
	}

	if (typ_val_rfload(dep, length, "VAL.val_18.ARAM", "VAL.val_20.BRAM", "val"))
		return (1);
	if (length == 0x9a && dep->ram[0x10] == 0x99) {
		ctx = CTX_Find("VAL.val_54.WCSRAM");
		AN(ctx);
		dep->dst1 = (uint8_t*)(ctx + 1) + 0x800;
	}
	if ((length == 0x9a || length == 0x88) && dep->ram[0x10] == 0x99) {
		sc_tracef(dep->name, "Exp load_control_store_200.val");
		for(u = 0x18; u < 0x98; u += 8) {
			w = 0;
			VAL_WCS_A_0();
			VAL_WCS_A_1();
			VAL_WCS_A_2();
			VAL_WCS_A_3();
			VAL_WCS_A_4();
			VAL_WCS_A_5();
			VAL_WCS_B_0();
			VAL_WCS_B_1();
			VAL_WCS_B_2();
			VAL_WCS_B_3();
			VAL_WCS_B_4();
			VAL_WCS_B_5();
			VAL_WCS_FRAME_0();
			VAL_WCS_FRAME_1();
			VAL_WCS_FRAME_2();
			VAL_WCS_FRAME_3();
			VAL_WCS_FRAME_4();
			VAL_WCS_C_MUX_SEL_0();
			VAL_WCS_C_MUX_SEL_1();
			VAL_WCS_RAND_0();
			VAL_WCS_RAND_1();
			VAL_WCS_RAND_2();
			VAL_WCS_RAND_3();
			VAL_WCS_C_0();

			VAL_WCS_C_1();
			VAL_WCS_C_2();
			VAL_WCS_C_3();
			VAL_WCS_C_4();
			VAL_WCS_C_5();
			VAL_WCS_M_A_SRC_0();
			VAL_WCS_M_A_SRC_1();
			VAL_WCS_M_B_SRC_0();

			VAL_WCS_M_B_SRC_1();
			VAL_WCS_ALU_FUNC_0();
			VAL_WCS_ALU_FUNC_1();
			VAL_WCS_ALU_FUNC_2();
			VAL_WCS_ALU_FUNC_3();
			VAL_WCS_ALU_FUNC_4();
			VAL_WCS_C_SOURCE();
			VAL_WCS_PARITY();
			memcpy(dep->dst1, &w, sizeof w);
			dep->dst1 += sizeof w;
		}
		return (1);
	}

	return (0);
}

int
diagproc_exp_download(struct diagproc_exp_priv *dep, uint8_t length, uint8_t *ram, uint8_t *ip)
{
	uint8_t first = ram[0x10];
	int retval = 0;

	dep->ram = ram;
	dep->ip = ip;
	if (dep->board(dep, length)) {
		ram[0x04] = DIPROC_RESPONSE_DONE;
		retval = 1;
	} else {
		sc_tracef(dep->name, "Exp [0x%02x] @0x%02x 0x%02x 0x%02x 0x%02x", length, first, ram[first], ram[first+1], ram[first+2]);
	}
	return (retval);
}
