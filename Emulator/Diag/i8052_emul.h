
#ifndef MCS51_SFRS
#define MCS51_SFRS \
	SFRMACRO(0x80, P0) \
	SFRMACRO(0x81, SP) \
	SFRMACRO(0x82, DPL) \
	SFRMACRO(0x83, DPH) \
	SFRMACRO(0x87, PCON) \
	SFRMACRO(0x88, TCON) \
	SFRMACRO(0x89, TMOD) \
	SFRMACRO(0x8a, TL0) \
	SFRMACRO(0x8b, TL1) \
	SFRMACRO(0x8c, TH0) \
	SFRMACRO(0x8d, TH1) \
	SFRMACRO(0x90, P1) \
	SFRMACRO(0x98, SCON) \
	SFRMACRO(0x99, SBUF) \
	SFRMACRO(0xa0, P2) \
	SFRMACRO(0xa8, IE) \
	SFRMACRO(0xb0, P3) \
	SFRMACRO(0xb8, IP) \
	SFRMACRO(0xc8, T2CON) \
	SFRMACRO(0xd0, PSW) \
	SFRMACRO(0xd8, CCON) \
	SFRMACRO(0xe0, ACC) \
	SFRMACRO(0xf0, B)
#endif /* MCS51_SFRS */

enum sfr_e {
#define SFRMACRO(num, nam) SFR_##nam = num,
MCS51_SFRS
#undef SFRMACRO
};

struct mcs51;

typedef unsigned bitfunc_f(struct mcs51 *, uint8_t bit_adr, int what);
typedef unsigned sfrfunc_f(struct mcs51 *, uint8_t sfr_adr, int what);

typedef void movx8_write(struct mcs51 *, uint8_t adr, int data);

struct mcs51 {
	const char	*ident;
	void		*priv;
	char		errmsg[256];
	char		tracebuf[256];
	char		*traceptr;

	uint32_t	do_trace;

	int		irq_state;

#define PSW_CY 0x80
#define PSW_AC 0x40
#define PSW_F0 0x20
#define PSW_RS1 0x10
#define PSW_RS0 0x08
#define PSW_OV 0x04
#define PSW_P 0x01

	uint8_t		*progmem;
	size_t		progmem_size;

	uint8_t		iram[256];
	size_t		iram_size;

	uint16_t	pc;
	uint16_t	npc;

	uint8_t		sfr[256];

	bitfunc_f	*bitfunc[256];
	sfrfunc_f	*sfrfunc[256];
	movx8_write	*movx8_write;

	char		*sfrnames[256];
	char		*bitnames[256];
};

struct mcs51 * MCS51_Create(const char *ident);
int MCS51_SetProgMem(struct mcs51 *mcs51, const void *ptr, size_t len);
uint16_t MCS51_SingleStep(struct mcs51 *mcs51);
uint8_t MCS51_REG(struct mcs51 *mcs51, int reg);
void MCS51_SetSFR(struct mcs51 *mcs51, uint8_t adr, sfrfunc_f *,
    const char *fmt, ...);
void MCS51_SetBit(struct mcs51 *mcs51, uint8_t adr, bitfunc_f *,
    const char *fmt, ...);
void MCS51_SetSFRBits(struct mcs51 *mcs51, uint8_t adr, bitfunc_f *,
    const char *b7, const char *b6, const char *b5, const char *b4,
    const char *b3, const char *b2, const char *b1, const char *b0);
unsigned mcs51_bitfunc_default(struct mcs51 *mcs51, uint8_t bit_adr, int what);
void MCS51_TimerTick(struct mcs51 *mcs51);
void MCS51_Reset(struct mcs51 *mcs51);

void MCS51_Rx(struct mcs51 *mcs51, uint8_t byte, uint8_t ninth);
