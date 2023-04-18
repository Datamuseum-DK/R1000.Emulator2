
#include "Infra/r1000.h"
#include "Diag/diag.h"

static void
mod_fiu_mar(uint8_t *firmware)
{
	// fiu_53 Reorder MAR.NAME[0..7] & F.ADR.NAME[0..7]
	firmware[0xcbc] = 0xe1;
	firmware[0xcc5] = 0xc1;
	firmware[0xcce] = 0xa1;
	firmware[0xcd7] = 0x81;
	firmware[0xce0] = 0x61;
	firmware[0xce9] = 0x41;
	firmware[0xcf2] = 0x21;
	firmware[0xcfb] = 0x01;

	// fiu_53 Reorder MAR.NAME[8..15] & F.ADR.NAME[8..15]
	firmware[0xcbd] = 0xe2;
	firmware[0xcc6] = 0xc2;
	firmware[0xccf] = 0xa2;
	firmware[0xcd8] = 0x82;
	firmware[0xce1] = 0x62;
	firmware[0xcea] = 0x42;
	firmware[0xcf3] = 0x22;
	firmware[0xcfc] = 0x02;

	// fiu_53 Reorder MAR.NAME[16..23] & F.ADR.NAME[16..12]
	firmware[0xcbe] = 0xe3;
	firmware[0xcc7] = 0xc3;
	firmware[0xcd0] = 0xa3;
	firmware[0xcd9] = 0x83;
	firmware[0xce2] = 0x63;
	firmware[0xceb] = 0x43;
	firmware[0xcf4] = 0x23;
	firmware[0xcfd] = 0x03;

	// fiu_53 Reorder MAR.NAME[24..31] & F.ADR.NAME[24..31]
	firmware[0xcbf] = 0xe4;
	firmware[0xcc8] = 0xc4;
	firmware[0xcd1] = 0xa4;
	firmware[0xcda] = 0x84;
	firmware[0xce3] = 0x64;
	firmware[0xcec] = 0x44;
	firmware[0xcf5] = 0x24;
	firmware[0xcfe] = 0x04;

	// fiu_53 Reorder MAR.OFFS[0..7] & F.ADR.OFFS[0..7]
	firmware[0xcc0] = 0xc6;
	firmware[0xcc9] = 0xa6;
	firmware[0xcd2] = 0x86;
	firmware[0xcdb] = 0x66;
	firmware[0xce4] = 0x46;
	firmware[0xced] = 0x26;
	firmware[0xcf6] = 0x06;
	firmware[0xcff] = 0xe5;

	// fiu_53 Reorder MAR.OFFS[8..15] & F.ADR.OFFS[8..15]
	firmware[0xcc1] = 0xc7;
	firmware[0xcca] = 0xa7;
	firmware[0xcd3] = 0x87;
	firmware[0xcdc] = 0x67;
	firmware[0xce5] = 0x47;
	firmware[0xcee] = 0x27;
	firmware[0xcf7] = 0x07;
	firmware[0xd00] = 0xe6;

	// fiu_53 Reorder MAR.OFFS[16..23] & F.ADR.OFFS[16..23]
	firmware[0xcc2] = 0xc8;
	firmware[0xccb] = 0xa8;
	firmware[0xcd4] = 0x88;
	firmware[0xcdd] = 0x68;
	firmware[0xce6] = 0x48;
	firmware[0xcef] = 0x28;
	firmware[0xcf8] = 0x08;
	firmware[0xd01] = 0xe7;

}

static void
mod_fiu_uir_move(uint8_t *firmware, unsigned from, unsigned to)
{
	unsigned a_from, a_to, i, j, k, base = 0xd4e, base2 = 0xd97;

	(void)firmware;
	a_from = base + (from >> 3) + 9 * (7 - (from & 7));
	a_to = base + (to >> 3) + 9 * (7 - (to & 7));

	printf("FROM %u 0x%x TO %u 0x%x (0x%02x)\n", from, a_from, to, a_to, firmware[a_from]);
	assert(firmware[a_to] == 0x1f);
	firmware[a_to] = firmware[a_from];
	firmware[a_from] = 0x1f;

	for (i = 0; i < 8; i++) {
		k = 0;
		for (j = 0 ; j < 8; j++) {
			k <<= 1;
			if (firmware[base + i * 9 + j] != 0x1f)
				k |= 1;
		}
		if (k != firmware[base + i * 9 + 8]) {
			printf("I %u k 0x%02x was 0x%02x\n", i, k, firmware[base + i * 9 + 8]);
			firmware[base + i * 9 + 8] = k;
			firmware[base2 + i] = k;
		}
	}
}

static void
mod_fiu_uir(uint8_t *firmware)
{
	unsigned i, j;

	mod_fiu_uir_move(firmware, 31, 23); // load_mdr
	mod_fiu_uir_move(firmware, 27, 31); // tivi_src3
	mod_fiu_uir_move(firmware, 19, 27); // vmux_sel1
	mod_fiu_uir_move(firmware, 29, 22); // load_var
	mod_fiu_uir_move(firmware, 25, 29); // tivi_src1
	mod_fiu_uir_move(firmware, 17, 25); // op_sel1
	mod_fiu_uir_move(firmware, 15, 17); // lfreg_cntl1
	mod_fiu_uir_move(firmware, 30, 15); // load_tar (tmp move)
	mod_fiu_uir_move(firmware, 26, 30); // tivi_src2
	mod_fiu_uir_move(firmware, 18, 26); // vmux_sel0
	mod_fiu_uir_move(firmware, 20, 18); // fill_mode_src
	mod_fiu_uir_move(firmware, 28, 20); // load_oreg
	mod_fiu_uir_move(firmware, 24, 28); // tivi_src0
	mod_fiu_uir_move(firmware, 16, 24); // op_sel0
	mod_fiu_uir_move(firmware, 14, 16); // lfreg_cntl0
	mod_fiu_uir_move(firmware, 13, 14); // lfl6
	mod_fiu_uir_move(firmware, 12, 13); // lfl5
	mod_fiu_uir_move(firmware, 11, 12); // lfl4
	mod_fiu_uir_move(firmware, 10, 11); // lfl3
	mod_fiu_uir_move(firmware,  9, 10); // lfl2
	mod_fiu_uir_move(firmware,  8,  9); // lfl1
	mod_fiu_uir_move(firmware,  7,  8); // lfl0
	mod_fiu_uir_move(firmware, 21,  7); // oreg_src
	mod_fiu_uir_move(firmware, 15, 21); // load_tar
	mod_fiu_uir_move(firmware, 40, 15); // length_src
	mod_fiu_uir_move(firmware, 41, 19); // offs_src
	mod_fiu_uir_move(firmware, 39, 38); // parity

	for (i = 0; i < 8; i++) {
		for (j = 0 ; j < 9; j++) {
			printf(" %02x", firmware[0xd4e + i * 9 + j]);
		}
		printf("\n");
	}
	for (i = 0; i < 9; i++) {
		printf(" %02x", firmware[0xd97 + i]);
	}
	printf("\n");
}

void
diproc1_mod(uint8_t *firmware, unsigned mod)
{

	printf("DIPROC FW1 mod %u\n", mod);
	switch (mod) {
	case 0:
		break;
	case 1:
		mod_fiu_mar(firmware);
		break;
	case 2:
		mod_fiu_mar(firmware);
		mod_fiu_uir(firmware);
		break;
	case 16:
		break;
	case 17:
		mod_fiu_mar(firmware);
		break;
	default:
		WRONG();
	}
}
