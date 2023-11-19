/*-
 * Copyright (c) 2021 Poul-Henning Kamp
 * All rights reserved.
 *
 * Author: Poul-Henning Kamp <phk@phk.freebsd.dk>
 *
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * PDF page references are to MCS-51_Users_Manual_Feb94.pdf
 */

#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "i8052_emul.h"

/*---------------------------------------------------------------------*/

static int __printflike(2, 3)
mcs51_diag(struct mcs51 *mcs51, const char *fmt, ...)
{
	va_list ap;

	va_start(ap, fmt);
	(void)vsnprintf(mcs51->errmsg, sizeof mcs51->errmsg, fmt, ap);
	va_end(ap);
	fprintf(stderr, "FATAL in %s:\n    %s\n", mcs51->ident, mcs51->errmsg);
	fprintf(stderr, "    PC=%04x", mcs51->pc);
	fprintf(stderr, " [%02x", mcs51->progmem[mcs51->pc]);
	fprintf(stderr, " %02x", mcs51->progmem[mcs51->pc + 1]);
	fprintf(stderr, " %02x", mcs51->progmem[mcs51->pc + 2]);
	fprintf(stderr, " %02x]\n", mcs51->progmem[mcs51->pc + 3]);
	exit(2);
}

/*---------------------------------------------------------------------*/

static void __printflike(2, 3)
mcs51_trace(struct mcs51 *mcs51, const char *fmt, ...)
{
	va_list ap;
	ssize_t left;

	if (!mcs51->do_trace)
		return;
	va_start(ap, fmt);
	left = (mcs51->tracebuf + sizeof mcs51->tracebuf) - mcs51->traceptr;
	assert(left > 3);
	*mcs51->traceptr++ = '\t';
	*mcs51->traceptr++ = '|';
	left -= 2;
	mcs51->traceptr += vsnprintf(mcs51->traceptr, left, fmt, ap);
	va_end(ap);
}

/*---------------------------------------------------------------------*/

static void
mcs51_push(struct mcs51 *mcs51, uint8_t val)
{
	mcs51->iram[++mcs51->sfr[SFR_SP]] = val;
	mcs51_trace(mcs51, "push 0x%02x", val);
}

static uint8_t
mcs51_pop(struct mcs51 *mcs51)
{
	uint8_t retval;

	retval = mcs51->iram[mcs51->sfr[SFR_SP]--];
	mcs51_trace(mcs51, "pop -> 0x%02x", retval);
	return (retval);
}

// Boolean argument to function
//lint -save -e730

static uint8_t
mcs51_carry(struct mcs51 *mcs51, int what)
{
	if (what > 0)
		mcs51->sfr[SFR_PSW] |= PSW_CY;
	else if (what == 0)
		mcs51->sfr[SFR_PSW] &= ~PSW_CY;
	mcs51_trace(mcs51, "C is %d", mcs51->sfr[SFR_PSW] >> 7);
	return (mcs51->sfr[SFR_PSW] >> 7);
}

static uint8_t
mcs51_direct_address(struct mcs51 *mcs51, uint8_t address, int what)
{
	uint8_t u, *up;

	if (address >= 0x80) {
		u = mcs51->sfrfunc[address](mcs51, address, what);
		mcs51_trace(mcs51, "sfr %s is 0x%02x",
		    mcs51->sfrnames[address], u);
		return (u);
	}
	up = mcs51->iram + address;
	if (what >= 0)
		*up = what;
	if ((address & 0x78) == (mcs51->sfr[SFR_PSW] & 0x18))
		mcs51_trace(mcs51, "R%d is 0x%02x", address & 7, *up);
	else
		mcs51_trace(mcs51, "direct 0x%02x is 0x%02x", address, *up);
	return(*up);
}

static uint8_t
mcs51_bit_address(struct mcs51 *mcs51, uint8_t address, int what)
{
	uint8_t retval;

	retval = mcs51->bitfunc[address](mcs51, address, what);
	mcs51_trace(mcs51, "bit %s is %x",
	    mcs51->bitnames[address], retval);
	return (retval);
}

static uint8_t*
mcs51_reg(struct mcs51 *mcs51, uint8_t regno)
{
	uint8_t u, *up;

	u = (mcs51->sfr[SFR_PSW] & 0x18) + regno;
	up = mcs51->iram + u;
	return (up);
}

#define RELJMP(cond)							\
	do {								\
		warg = mcs51->progmem[mcs51->npc++];			\
		if (warg & 0x80)					\
			warg |= 0xff00;					\
		warg += mcs51->npc;					\
		if (cond) {						\
			mcs51_trace(mcs51, "=> 0x%04x", warg);		\
			return (warg);					\
		} else {						\
			mcs51_trace(mcs51, "(0x%04x)", warg);		\
			return (mcs51->npc);				\
		}							\
	} while (0)

static uint16_t
mcs51_AJMP_ACALL(struct mcs51 *mcs51, uint8_t ins)
{
	uint16_t retval;

	retval = mcs51->progmem[mcs51->npc++];
	retval |= ((uint16_t)ins << 3) & 0x700;
	retval |= mcs51->npc & 0xf800;
	if (ins & 0x10) {
		mcs51_trace(mcs51, "ACALL\t0x%04x", retval);
		mcs51_push(mcs51, mcs51->npc & 0xff);
		mcs51_push(mcs51, mcs51->npc >> 8);
	} else {
		mcs51_trace(mcs51, "AJMP\t0x%04x", retval);
	}
	return (retval);
}

static uint8_t
mcs51_ADD(struct mcs51 *mcs51, uint8_t a1, uint8_t a2, int carry)
{
	uint16_t retval;

	retval = a1 + a2;
	if (carry)
		retval += mcs51_carry(mcs51, -1);
	(void)mcs51_carry(mcs51, retval >> 8);
	return (retval & 0xff);
}

static uint8_t
mcs51_SUBB(struct mcs51 *mcs51, uint8_t a1, uint8_t a2)
{
	uint16_t retval;

	retval = 256 + a1 - a2;
	retval -= mcs51_carry(mcs51, -1);
	(void)mcs51_carry(mcs51, !(retval >> 8));
	return (retval & 0xff);
}

#define ACC mcs51->sfr[SFR_ACC]

static int
mcs51_check_irq(struct mcs51 *mcs51)
{
	uint16_t vector = 0;

	mcs51_trace(mcs51, "{%02x %02x %d}", mcs51->sfr[SFR_IE], mcs51->sfr[SFR_IP], mcs51->irq_state);
	if (!(mcs51->sfr[SFR_IE] & 0x80))
		return(0);
	if (mcs51->irq_state & 2)
		return(0);
	if ((mcs51->sfr[SFR_SCON] & 3) && (mcs51->sfr[SFR_IE] & 0x10)) {
		if (mcs51->sfr[SFR_IP] & 0x10) {
			mcs51->irq_state |= 2;
			vector = 0x0023;
		} else if (!mcs51->irq_state) {
			mcs51->irq_state |= 1;
			vector = 0x0023;
		}
	}
	if (!vector)
		return (0);
	mcs51_trace(mcs51, "INTERRUPT\t0x%04x", mcs51->pc);
	mcs51_push(mcs51, mcs51->pc & 0xff);
	mcs51_push(mcs51, mcs51->pc >> 8);
	mcs51->pc = vector;
	return (1);
}

uint16_t
MCS51_SingleStep(struct mcs51 *mcs51)
{
	uint8_t ins, arg, *u8p, arg2;
	uint16_t warg;

	mcs51->traceptr = mcs51->tracebuf;

	if (mcs51_check_irq(mcs51))
		return(mcs51->pc);

	mcs51->npc = mcs51->pc;

	ins = mcs51->progmem[mcs51->npc++];

	switch (ins) {
	case 0x00: // NOP
		mcs51_trace(mcs51, "NOP");
		break;
	case 0x01: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x02: // LJMP addr16
		warg = mcs51->progmem[mcs51->npc++] << 8;
		warg |= mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "LJMP\t0x%04x", warg);
		mcs51->npc = warg;
		break;
	case 0x03: // RR A
		arg = ACC;
		ACC >>= 1;
		ACC |= (arg << 7);
		mcs51_trace(mcs51, "RR\tA\t|A is 0x%02x", ACC);
		break;
	case 0x04: // INC A
		ACC++;
		mcs51_trace(mcs51, "INC\tA\t|A is 0x%02x", ACC);
		break;
	case 0x05: // INC direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "INC\t0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, arg2 + 1);
		break;
	case 0x06: // INC @Rn
	case 0x07: // INC @Rn
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "INC\t@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		mcs51->iram[*u8p]++;
		mcs51_trace(mcs51, "0x%02x is 0x%02x",
		    *u8p, mcs51->iram[*u8p]);
		break;
	case 0x08: // INC Rn
	case 0x09: // INC Rn
	case 0x0a: // INC Rn
	case 0x0b: // INC Rn
	case 0x0c: // INC Rn
	case 0x0d: // INC Rn
	case 0x0e: // INC Rn
	case 0x0f: // INC Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		(*u8p)++;
		mcs51_trace(mcs51, "INC\tR%d\t|R%d is 0x%02x",
		    ins & 7, ins & 7, *u8p);
		break;
	case 0x10: // JBC bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "JBC\t0x%02x", arg);
		arg2 = mcs51_bit_address(mcs51, arg, -1);
		if (arg2)
			(void)mcs51_bit_address(mcs51, arg, 0);
		RELJMP(arg2);
		break;
	case 0x11: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x12: // LCALL addr16
		warg = mcs51->progmem[mcs51->npc++] << 8;
		warg |= mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "LJMP\t0x%04x", warg);
		mcs51_push(mcs51, mcs51->npc & 0xff);
		mcs51_push(mcs51, mcs51->npc >> 8);
		return(warg);
		break;
	case 0x13: // RRC A
		arg = ACC;
		mcs51_trace(mcs51, "RRC\tA");
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		ACC >>= 1;
		ACC |= mcs51_carry(mcs51, -1) << 7;
		(void)mcs51_carry(mcs51, arg & 1);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x14: // DEC A
		ACC -= 1;
		mcs51_trace(mcs51, "DEC\tA\t|A is 0x%02x", ACC);
		break;
	case 0x15: // DEC direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "DEC\t0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, arg2 - 1);
		break;
	case 0x16: // DEC @Rn
	case 0x17: // DEC @Rn
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "DEC\t@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		mcs51->iram[*u8p]--;
		mcs51_trace(mcs51, "0x%02x is 0x%02x",
		    *u8p, mcs51->iram[*u8p]);
		break;
	case 0x18: // DEC Rn
	case 0x19: // DEC Rn
	case 0x1a: // DEC Rn
	case 0x1b: // DEC Rn
	case 0x1c: // DEC Rn
	case 0x1d: // DEC Rn
	case 0x1e: // DEC Rn
	case 0x1f: // DEC Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		(*u8p)--;
		mcs51_trace(mcs51, "DEC\tR%d\t|R%d is 0x%02x",
		    ins & 7, ins & 7, *u8p);
		break;
	case 0x20: // JB bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "JB\t0x%02x", arg);
		RELJMP(mcs51_bit_address(mcs51, arg, -1));
		break;
	case 0x21: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x22: // RET
		mcs51_trace(mcs51, "RET");
		warg = mcs51_pop(mcs51) << 8;
		warg |= mcs51_pop(mcs51);
		return (warg);
		break;
	case 0x23: // RL A
		warg = ACC << 1;
		ACC = warg & 0xfe;
		ACC |= (warg >> 8);
		mcs51_trace(mcs51, "RL\tA\t|A is 0x%02x", ACC);
		break;
	case 0x24: // ADD A,#data
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ADD\tA,#0x%02x", arg);
		ACC = mcs51_ADD(mcs51, ACC, arg, 0);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x25: // ADD A,direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ADD\tA,0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		ACC = mcs51_ADD(mcs51, ACC, arg2, 0);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x26: // ADD A,@Ri
	case 0x27: // ADD A,@Ri
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "ADD\tA,@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		ACC = mcs51_ADD(mcs51, ACC, mcs51->iram[*u8p], 0);
		mcs51_trace(mcs51, "0x%02x is 0x%02x\t|A is 0x%02x",
		    *u8p, mcs51->iram[*u8p], ACC);
		break;
	case 0x28: // ADD A,Rn
	case 0x29: // ADD A,Rn
	case 0x2a: // ADD A,Rn
	case 0x2b: // ADD A,Rn
	case 0x2c: // ADD A,Rn
	case 0x2d: // ADD A,Rn
	case 0x2e: // ADD A,Rn
	case 0x2f: // ADD A,Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		mcs51_trace(mcs51, "ADD\tA,R%d\t|R%d is 0x%02x",
		    ins & 7, ins & 7, *u8p);
		ACC = mcs51_ADD(mcs51, ACC, *u8p, 0);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x30: // JNB bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "JNB\t0x%02x", arg);
		RELJMP(!mcs51_bit_address(mcs51, arg, -1));
		break;
	case 0x31: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x32: // RETI
		mcs51_trace(mcs51, "RETI");
		warg = mcs51_pop(mcs51) << 8;
		warg |= mcs51_pop(mcs51);
		if (mcs51->irq_state & 2)
			mcs51->irq_state &= ~2;
		else if (mcs51->irq_state & 1)
			mcs51->irq_state &= ~1;
		return (warg);
		break;
	case 0x33: // RLC A
		warg = ACC << 1;
		mcs51_trace(mcs51, "RCL\tA");
		if (mcs51_carry(mcs51, -1))
			warg |= 1;
		(void)mcs51_carry(mcs51, warg >> 8);
		ACC = warg;
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x34: // ADDC A,#data
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ADDC\tA,#0x%02x", arg);
		ACC = mcs51_ADD(mcs51, ACC, arg, 1);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x35: // ADDC A,direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ADDC\tA,0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		ACC = mcs51_ADD(mcs51, ACC, arg2, 1);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x36: // ADDC A,@Ri
	case 0x37: // ADDC A,@Ri
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "ADD\tA,@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		ACC = mcs51_ADD(mcs51, ACC, mcs51->iram[*u8p], 1);
		mcs51_trace(mcs51, "0x%02x is 0x%02x\t|A is 0x%02x",
		    *u8p, mcs51->iram[*u8p], ACC);
		break;
	case 0x38: // ADDC A,Rn
	case 0x39: // ADDC A,Rn
	case 0x3a: // ADDC A,Rn
	case 0x3b: // ADDC A,Rn
	case 0x3c: // ADDC A,Rn
	case 0x3d: // ADDC A,Rn
	case 0x3e: // ADDC A,Rn
	case 0x3f: // ADDC A,Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		mcs51_trace(mcs51, "ADDC\tA,R%d\t|R%d is 0x%02x",
		    ins & 7, ins & 7, *u8p);
		ACC = mcs51_ADD(mcs51, ACC, *u8p, 1);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x40: // JC bit
		mcs51_trace(mcs51, "JC");
		RELJMP(mcs51_carry(mcs51, -1));
		break;
	case 0x41: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x42: // ORL direct, A
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ORL\t0x%02x,A", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, arg2 | ACC);
		break;
	case 0x43: // ORL direct, imm
		arg = mcs51->progmem[mcs51->npc++];
		arg2 = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ORL\t0x%02x,#0x%02x", arg, arg2);
		warg = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, warg | arg2);
		break;
	case 0x44: // ORL A,imm
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ORL\tA,#0x%02x", arg);
		ACC |= arg;
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x45: // ORL A,direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ORL\tA,0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		ACC |= arg2;
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x46: // ORL A,@Ri
	case 0x47: // ORL A,@Ri
		u8p = mcs51_reg(mcs51, ins & 1);
		ACC |= mcs51->iram[*u8p];
		mcs51_trace(mcs51, "ORL\tA,@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		mcs51_trace(mcs51, "0x%02x is 0x%02x\t|A is 0x%02x",
		    *u8p, mcs51->iram[*u8p], ACC);
		break;
	case 0x48: // ORL Rn
	case 0x49: // ORL Rn
	case 0x4a: // ORL Rn
	case 0x4b: // ORL Rn
	case 0x4c: // ORL Rn
	case 0x4d: // ORL Rn
	case 0x4e: // ORL Rn
	case 0x4f: // ORL Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		ACC |= *u8p;
		mcs51_trace(mcs51, "ORL\tA,R%d\t|R%d is 0x%02x\t|A is 0x%02x",
		    ins & 7, ins & 7, *u8p, ACC);
		break;
	case 0x50: // JNC bit
		mcs51_trace(mcs51, "JNC");
		RELJMP(!mcs51_carry(mcs51, -1));
		break;
	case 0x51: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x52: // ANL direct, A
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ANL\t0x%02x,A", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, arg2 & ACC);
		break;
	case 0x53: // ANL direct,#data
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ANL\t0x%02x,#0x%02x", arg, mcs51->progmem[mcs51->npc]);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, arg2 & mcs51->progmem[mcs51->npc++]);
		break;
	case 0x54: // ANL A,#data
		arg = mcs51->progmem[mcs51->npc++];
		ACC &= arg;
		mcs51_trace(mcs51, "ALN\tA,#0x%02x\t|A is 0x%02x", arg, ACC);
		break;
	case 0x55: // ANL A,direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ANL\tA,0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		ACC &= arg2;
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x56: // ANL A,@Ri
	case 0x57: // ANL A,@Ri
		u8p = mcs51_reg(mcs51, ins & 1);
		ACC &= mcs51->iram[*u8p];
		mcs51_trace(mcs51, "ALN\tA,@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		mcs51_trace(mcs51, "0x%02x is 0x%02x\t|A is 0x%02x",
		    *u8p, mcs51->iram[*u8p], ACC);
		break;
	case 0x58: // ANL Rn
	case 0x59: // ANL Rn
	case 0x5a: // ANL Rn
	case 0x5b: // ANL Rn
	case 0x5c: // ANL Rn
	case 0x5d: // ANL Rn
	case 0x5e: // ANL Rn
	case 0x5f: // ANL Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		ACC &= *u8p;
		mcs51_trace(mcs51, "ANL\tA,R%d\t|R%d is 0x%02x\t|A is 0x%02x",
		    ins & 7, ins & 7, *u8p, ACC);
		break;
	case 0x60: // JZ bit,rel
		mcs51_trace(mcs51, "JZ");
		RELJMP(!ACC);
		break;
	case 0x61: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x62: // XRL direct, A
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "XRL\t0x%02x,A", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, arg2 ^ ACC);
		break;
	case 0x63: // XRL direct,#data
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "XRL\t0x%02x,#0x%02x", arg, mcs51->progmem[mcs51->npc]);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg, arg2 ^ mcs51->progmem[mcs51->npc++]);
		break;
	case 0x64: // XRL A,#data
		arg = mcs51->progmem[mcs51->npc++];
		ACC &= arg;
		mcs51_trace(mcs51, "XRL\tA,#0x%02x\t|A is 0x%02x", arg, ACC);
		break;
	case 0x65: // XRL A,direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "XRL\tA,0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		ACC ^= arg2;
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x66: // XRL A,@Ri
	case 0x67: // XRL A,@Ri
		u8p = mcs51_reg(mcs51, ins & 1);
		ACC ^= mcs51->iram[*u8p];
		mcs51_trace(mcs51, "XRL\tA,@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		mcs51_trace(mcs51, "0x%02x is 0x%02x\t|A is 0x%02x",
		    *u8p, mcs51->iram[*u8p], ACC);
		break;
	case 0x68: // XRL Rn
	case 0x69: // XRL Rn
	case 0x6a: // XRL Rn
	case 0x6b: // XRL Rn
	case 0x6c: // XRL Rn
	case 0x6d: // XRL Rn
	case 0x6e: // XRL Rn
	case 0x6f: // XRL Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		ACC ^= *u8p;
		mcs51_trace(mcs51, "XRL\tA,R%d\t|R%d is 0x%02x\t|A is 0x%02x",
		    ins & 7, ins & 7, *u8p, ACC);
		break;
	case 0x70: // JNZ bit,rel
		mcs51_trace(mcs51, "JNZ");
		RELJMP(ACC);
		break;
	case 0x71: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x72: // ORL C,bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ORL\tC,0x%02x", arg);
		if (mcs51->bitfunc[arg](mcs51, arg, -1))
			(void)mcs51_carry(mcs51, 1);
		break;
	case 0x73: // JMP @A+DPTR
		warg = (uint16_t)(mcs51->sfr[SFR_DPH]) << 8;
		warg |= mcs51->sfr[SFR_DPL];
		warg += ACC;
		mcs51_trace(mcs51, "JMP\t@A+DPTR\t|A is 0x%02x\t=> 0x%04x",
		    ACC, warg);
		return (warg);
		break;
	case 0x74: // MOV A,#data
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\tA,#0x%02x", arg);
		ACC = arg;
		break;
	case 0x75: // MOV direct,#data
		arg = mcs51->progmem[mcs51->npc++];
		arg2 = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\t0x%02x,#0x%02x", arg, arg2);
		(void)mcs51_direct_address(mcs51, arg, arg2);
		break;
	case 0x76: // MOV @Ri,#data
	case 0x77: // MOV @Ri,#data
		arg = mcs51->progmem[mcs51->npc++];
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "MOV\t@R%d,#0x%02x\t|R%d is 0x%02x",
		    ins & 1, arg, ins & 1, *u8p);
		mcs51->iram[*u8p] = arg;
		break;
	case 0x78: // MOV Rn,#data
	case 0x79: // MOV Rn,#data
	case 0x7a: // MOV Rn,#data
	case 0x7b: // MOV Rn,#data
	case 0x7c: // MOV Rn,#data
	case 0x7d: // MOV Rn,#data
	case 0x7e: // MOV Rn,#data
	case 0x7f: // MOV Rn,#data
		arg = mcs51->progmem[mcs51->npc++];
		u8p = mcs51_reg(mcs51, ins & 7);
		mcs51_trace(mcs51, "MOV\tR%d,#0x%02x",
		    ins & 7, arg);
		*u8p = arg;
		break;
	case 0x80: // SJMP
		mcs51_trace(mcs51, "SJMP");
		RELJMP(1);
		break;
	case 0x81: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x82: // ANL C,bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "ORL\tC,0x%02x", arg);
		if (!mcs51_bit_address(mcs51, arg, -1))
			(void)mcs51_carry(mcs51, 0);
		break;
	// 0x83 MOVC A,@A+PC
	case 0x84: // DIV AB
		mcs51_trace(mcs51, "DIV\tAB");
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		mcs51_trace(mcs51, "B is 0x%02x", mcs51->sfr[SFR_B]);
		arg = ACC / mcs51->sfr[SFR_B];
		arg2 = ACC % mcs51->sfr[SFR_B];
		ACC = arg;
		mcs51->sfr[SFR_B] = arg2;
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		mcs51_trace(mcs51, "B is 0x%02x", mcs51->sfr[SFR_B]);
		(void)mcs51_carry(mcs51, 0);
		break;
	case 0x85: // 0x85 MOV dataaddr,dataaddr
		arg = mcs51->progmem[mcs51->npc++];
		arg2 = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\t0x%02x,0x%02x", arg, arg2);
		warg = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_direct_address(mcs51, arg2, warg);
		break;
	case 0x86: // MOV direct,@Rn
	case 0x87: // MOV direct,@Rn
		arg = mcs51->progmem[mcs51->npc++];
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "MOV\t0x%02x,@R%d", arg, ins & 1);
		mcs51_trace(mcs51, "R%d is 0x%02x", ins & 1, *u8p);
		(void)mcs51_direct_address(mcs51, arg, mcs51->iram[*u8p]);
		break;
	case 0x88: // MOV direct,Rn
	case 0x89: // MOV direct,Rn
	case 0x8a: // MOV direct,Rn
	case 0x8b: // MOV direct,Rn
	case 0x8c: // MOV direct,Rn
	case 0x8d: // MOV direct,Rn
	case 0x8e: // MOV direct,Rn
	case 0x8f: // MOV direct,Rn
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\t0x%02x,R%d", arg, ins & 7);
		(void)mcs51_direct_address(mcs51, arg, *mcs51_reg(mcs51, ins & 7));
		break;
	case 0x90: // MOV DPTR, #imm16
		mcs51->sfr[SFR_DPH] = mcs51->progmem[mcs51->npc++];
		mcs51->sfr[SFR_DPL] = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\tDPTR,0x%02x%02x",
		    mcs51->sfr[SFR_DPH], mcs51->sfr[SFR_DPL]);
		break;
	case 0x91: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0x92: // MOV bit, C
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\t0x%02x,C", arg);
		(void)mcs51_bit_address(mcs51, arg, mcs51_carry(mcs51, -1));
		break;
	case 0x93: // MOVC A,@A+DPTR
		warg = (uint16_t)(mcs51->sfr[SFR_DPH]) << 8;
		warg |= mcs51->sfr[SFR_DPL];
		mcs51_trace(mcs51, "MOVC\tA,@A+DPTR\t|A is 0x%02x\t|DPTR is 0x%04x",
		    ACC, warg);
		warg += ACC;
		ACC = mcs51->progmem[warg];
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x94: // SUBB A,#imm
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "SUBB\tA,#0x%02x", arg);
		ACC = mcs51_SUBB(mcs51, ACC, arg);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x95: // SUBB A,data_addr
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "SUBB\tA,0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		ACC = mcs51_SUBB(mcs51, ACC, arg2);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	case 0x96: // SUBB A,@R0
	case 0x97: // SUBB A,@R1
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "SUBB\tA,@R%d\t|R%d is 0x%02x",
		    ins & 1, ins & 1, *u8p);
		ACC = mcs51_SUBB(mcs51, ACC, mcs51->iram[*u8p]);
		mcs51_trace(mcs51, "0x%02x is 0x%02x\t|A is 0x%02x",
		    *u8p, mcs51->iram[*u8p], ACC);
		break;
	case 0x98: // SUBB A,R0
	case 0x99: // SUBB A,R1
	case 0x9a: // SUBB A,R2
	case 0x9b: // SUBB A,R3
	case 0x9c: // SUBB A,R4
	case 0x9d: // SUBB A,R5
	case 0x9e: // SUBB A,R6
	case 0x9f: // SUBB A,R7
		u8p = mcs51_reg(mcs51, ins & 7);
		mcs51_trace(mcs51, "SUBB\tA,R%d\t|R%d is 0x%02x",
		    ins & 7, ins & 7, *u8p);
		ACC = mcs51_SUBB(mcs51, ACC, *u8p);
		mcs51_trace(mcs51, "A is 0x%02x", ACC);
		break;
	// 0xa0 ORL C,bitadr
	case 0xa1: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0xa2: // MOV C, bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\tC,0x%02x", arg);
		(void)mcs51_carry(mcs51, mcs51_bit_address(mcs51, arg, -1));
		break;
	case 0xa3: // INC DPTR
		if (!++mcs51->sfr[SFR_DPL])
		    ++mcs51->sfr[SFR_DPH];
		mcs51_trace(mcs51, "INC\tDPTR\tDPTR is 0x%02x%02x",
		    mcs51->sfr[SFR_DPH], mcs51->sfr[SFR_DPL]);
		break;
	case 0xa4: // MUL AB
		warg = ACC * mcs51->sfr[SFR_B];
		ACC = warg & 0xff;
		mcs51->sfr[SFR_B] = warg >> 8;
		mcs51_trace(mcs51, "MUL\tAB\t|A is 0x%02x\t|B is 0x%02x",
		    ACC, mcs51->sfr[SFR_B]);
		// XXX: OVERFLOW BIT
		(void)mcs51_carry(mcs51, 0);
		break;
	// 0xa5 reserved
	case 0xa6: // MOV @Ri,direct
	case 0xa7: // MOV @Ri,direct
		arg = mcs51->progmem[mcs51->npc++];
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "MOV\t@R%d,0x%02x\t|R%d is 0x%02x",
		    ins & 1, arg, ins & 1, *u8p);
		mcs51->iram[*u8p] = mcs51_direct_address(mcs51, arg, -1);
		break;
	case 0xa8: // MOV Rn,direct
	case 0xa9: // MOV Rn,direct
	case 0xaa: // MOV Rn,direct
	case 0xab: // MOV Rn,direct
	case 0xac: // MOV Rn,direct
	case 0xad: // MOV Rn,direct
	case 0xae: // MOV Rn,direct
	case 0xaf: // MOV Rn,direct
		u8p = mcs51_reg(mcs51, ins & 7);
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\tR%d,0x%02x",
		    ins & 7, arg);
		*u8p = mcs51_direct_address(mcs51, arg, -1);
		break;
	// 0xb0 ANL C, bitadr
	case 0xb1: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0xb2: // CPL bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "CPL\t0x%02x", arg);
		warg = mcs51_bit_address(mcs51, arg, -1);
		(void)mcs51_bit_address(mcs51, arg, 1 - warg);
		break;
	case 0xb3: // CPL C
		mcs51_trace(mcs51, "CPL\tC");
		(void)mcs51_carry(mcs51, !mcs51_carry(mcs51, -1));
		break;
	case 0xb4: // CJNE A,#data,rel
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "CJNE\tA,#0x%02x", arg);
		(void)mcs51_carry(mcs51, ACC < arg);
		RELJMP(ACC != arg);
		break;
	case 0xb5: // CJNE A,data addr
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "CJNE\tA,0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		(void)mcs51_carry(mcs51, ACC < arg2);
		RELJMP(ACC != arg2);
		break;
	case 0xb6: // CJNE @Ri,#data,rel
	case 0xb7: // CJNE @Ri,#data,rel
		u8p = mcs51_reg(mcs51, ins & 1);
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "CJNE\t@R%d,#0x%02x", ins & 1, arg);
		mcs51_trace(mcs51, "R%d is 0x%02x\t0x%02x is 0x%02x",
		    ins & 1, *u8p, *u8p, mcs51->iram[*u8p]);
		(void)mcs51_carry(mcs51, (mcs51->iram[*u8p]) < arg);
		RELJMP(mcs51->iram[*u8p] != arg);
		break;
	// 0xb8-0xbf: CJNE Ri,#imm
	case 0xb8: // CJNE R0,#imm
	case 0xb9: // CJNE R1,#imm
	case 0xba: // CJNE R2,#imm
	case 0xbb: // CJNE R3,#imm
	case 0xbc: // CJNE R4,#imm
	case 0xbd: // CJNE R5,#imm
	case 0xbe: // CJNE R6,#imm
	case 0xbf: // CJNE R7,#imm
		u8p = mcs51_reg(mcs51, ins & 7);
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "CJNE\tR%d,#0x%02x", ins & 7, arg);
		mcs51_trace(mcs51, "R%d is 0x%02x", ins & 7, *u8p);
		(void)mcs51_carry(mcs51, (*u8p) < arg);
		RELJMP(*u8p != arg);
		break;
	case 0xc0: // PUSH direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "PUSH\t0x%02x", arg);
		mcs51_push(mcs51, mcs51_direct_address(mcs51, arg, -1));
		break;
	case 0xc1: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0xc2: // CLR bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "CLR\t0x%02x", arg);
		(void)mcs51_bit_address(mcs51, arg, 0);
		break;
	case 0xc3: // CLR C
		mcs51_trace(mcs51, "CLR C");
		(void)mcs51_carry(mcs51, 0);
		break;
	case 0xc4: // SWAP A
		warg = ACC;
		warg <<= 4;
		ACC = warg | (warg >> 8);
		mcs51_trace(mcs51, "SWAP\tA\t|A is 0x%02x",
		    ACC);
		break;
	// 0xc5: XXH A,data adr
	// 0xc6: XXH A,@R0
	// 0xc7: XXH A,@R1
	case 0xc8: // XCH A,R0
	case 0xc9: // XCH A,R1
	case 0xca: // XCH A,R2
	case 0xcb: // XCH A,R3
	case 0xcc: // XCH A,R4
	case 0xcd: // XCH A,R5
	case 0xce: // XCH A,R6
	case 0xcf: // XCH A,R7
		u8p = mcs51_reg(mcs51, ins & 7);
		arg = *u8p;
		*u8p = ACC;
		ACC = arg;
		mcs51_trace(mcs51, "XCH\tA,R%d\t|A is 0x%02x\t|R%d is 0x%02x",
		    ins & 7, ACC, ins & 7, *u8p);
		break;
	case 0xd0: // POP direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "POP\t0x%02x", arg);
		(void)mcs51_direct_address(mcs51, arg, mcs51_pop(mcs51));
		break;
	case 0xd1: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0xd2: // SETB bit
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "SETB\t0x%02x", arg);
		(void)mcs51_bit_address(mcs51, arg, 1);
		break;
	case 0xd3: // SETB C
		mcs51_trace(mcs51, "SETB\tC");
		(void)mcs51_carry(mcs51, 1);
		break;
	// case 0xd4: DA A
	case 0xd5: // DJNZ direct,rel
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "DJNZ\t0x%02x", arg);
		arg2 = mcs51_direct_address(mcs51, arg, -1);
		arg2--;
		(void)mcs51_direct_address(mcs51, arg, arg2);
		RELJMP(arg2);
		break;
	// 0xd6: XCH A,@R0
	// 0xd7: XCH A,@R1
	case 0xd8: // DJNZ Rn,rel
	case 0xd9: // DJNZ Rn,rel
	case 0xda: // DJNZ Rn,rel
	case 0xdb: // DJNZ Rn,rel
	case 0xdc: // DJNZ Rn,rel
	case 0xdd: // DJNZ Rn,rel
	case 0xde: // DJNZ Rn,rel
	case 0xdf: // DJNZ Rn,rel
		u8p = mcs51_reg(mcs51, ins & 7);
		mcs51_trace(mcs51, "DJNZ\tR%d\t|R%d is 0x%02x",
		    ins & 7, ins & 7, *u8p);
		(*u8p)--;
		mcs51_trace(mcs51, "R%d is 0x%02x",
		    ins & 7, *u8p);
		RELJMP(*u8p);
		break;
	// 0xe0: MOVX A,@DPTR
	case 0xe1: return (mcs51_AJMP_ACALL(mcs51, ins));
	// 0xe2: MOVX A,@R0
	// 0xe3: MOVX A,@R1
	case 0xe4: // CLR A
		mcs51_trace(mcs51, "CLR\tA");
		ACC = 0;
		break;
	case 0xe5: // MOV A,direct
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\tA,0x%02x", arg);
		ACC = mcs51_direct_address(mcs51, arg, -1);
		break;
	case 0xe6: // MOV A,@Ri
	case 0xe7: // MOV A,@Ri
		u8p = mcs51_reg(mcs51, ins & 1);
		ACC = mcs51->iram[*u8p];
		mcs51_trace(mcs51, "MOV\tA,@R%d\t|R%d is 0x%02x\t|A is 0x%02x",
		    ins & 1, ins & 1, *u8p, ACC);
		break;
	case 0xe8: // MOV A,Rn
	case 0xe9: // MOV A,Rn
	case 0xea: // MOV A,Rn
	case 0xeb: // MOV A,Rn
	case 0xec: // MOV A,Rn
	case 0xed: // MOV A,Rn
	case 0xee: // MOV A,Rn
	case 0xef: // MOV A,Rn
		u8p = mcs51_reg(mcs51, ins & 7);
		ACC = *u8p;
		mcs51_trace(mcs51, "MOV\tA,R%d\t|A is 0x%02x",
		    ins & 7, ACC);
		break;
	// case 0xf0: // MOVX @DPTR,A
	case 0xf1: return (mcs51_AJMP_ACALL(mcs51, ins));
	case 0xf2: // MOVX @Ri,A
	case 0xf3: // MOVX @Ri,A
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "MOVX\t@R%d,A\tEXT::0x%02x is 0x%02x",
		    ins & 1, *u8p, ACC);
		assert(mcs51->movx8_write);
		mcs51->movx8_write(mcs51, *u8p, ACC);
		break;
	case 0xf4: // CPL A
		ACC ^= 0xff;
		mcs51_trace(mcs51, "CPL\tA\t|A is 0x%02x", ACC);
		break;
	case 0xf5: // MOV direct,A
		arg = mcs51->progmem[mcs51->npc++];
		mcs51_trace(mcs51, "MOV\t0x%02x,A", arg);
		(void)mcs51_direct_address(mcs51, arg, ACC);
		break;
	case 0xf6: // MOV @Ri,A
	case 0xf7: // MOV @Ri,A
		u8p = mcs51_reg(mcs51, ins & 1);
		mcs51_trace(mcs51, "MOV\t@R%d,A\t|R%d is 0x%02x\t|A is 0x%02x",
		    ins & 1, ins & 1, *u8p, ACC);
		mcs51->iram[*u8p] = ACC;
		break;
	case 0xf8: // MOV Rn,direct
	case 0xf9: // MOV Rn,direct
	case 0xfa: // MOV Rn,direct
	case 0xfb: // MOV Rn,direct
	case 0xfc: // MOV Rn,direct
	case 0xfd: // MOV Rn,direct
	case 0xfe: // MOV Rn,direct
	case 0xff: // MOV Rn,direct
		u8p = mcs51_reg(mcs51, ins & 7);
		*u8p = ACC;
		mcs51_trace(mcs51, "MOV\tR%d,A\t|R%d is 0x%02x",
		    ins & 7, ins & 7, ACC);
		break;
	default:
		(void)mcs51_diag(mcs51, "Unimplemented Instruction");
		break;
	}

	return (mcs51->npc);
}

/*---------------------------------------------------------------------*/

static unsigned
mcs51_bitfunc_wrong(struct mcs51 *mcs51, uint8_t bit_adr, int what)
{
	uint8_t *u, b;
	const char *name = mcs51->sfrnames[bit_adr & ~7];

	u = mcs51->sfr + (bit_adr & ~7);
	b = 1 << (bit_adr & 7);
	if (what < 0) {
		mcs51_trace(mcs51, "*** WRONG BITFUNC 0x%02x %s.%d query",
		    bit_adr, name, bit_adr & 7);
	} else if (what == 0) {
		mcs51_trace(mcs51, "*** WRONG BITFUNC 0x%02x %s.%d <- %d",
		    bit_adr, name, bit_adr & 7, what);
		*u &= ~b;
	} else {
		mcs51_trace(mcs51, "*** WRONG BITFUNC 0x%02x %s.%d <- %d",
		    bit_adr, name, bit_adr & 7, what);
		*u |= b;
	}
	b = *u & b ? 1 : 0;
	mcs51_trace(mcs51, "%s is 0x%02x", name, *u);
	return (b);
}

static unsigned
mcs51_bitfunc_ram(struct mcs51 *mcs51, uint8_t bit_adr, int what)
{
	uint8_t *u, b;

	u = mcs51->iram + 0x20 + (bit_adr >> 3);
	b = 1 << (bit_adr & 7);
	if (what == 0)
		*u &= ~b;
	else if (what == 1)
		*u |= b;
	b = *u & b ? 1 : 0;
	return (b);
}

unsigned
mcs51_bitfunc_default(struct mcs51 *mcs51, uint8_t bit_adr, int what)
{
	uint8_t *u, b, s;

	s = bit_adr & ~7;
	u = mcs51->sfr + s;
	b = 1 << (bit_adr & 7);
	if (what == 0)
		*u &= ~b;
	else if (what == 1)
		*u |= b;
	b = *u & b ? 1 : 0;
	return (b);
}

/*---------------------------------------------------------------------*/

static unsigned
mcs51_sfrfunc_wrong(struct mcs51 *mcs51, uint8_t sfr_adr, int what)
{

	if (what < 0) {
		mcs51_trace(mcs51, "*** WRONG SFRFUNC 0x%02x %s query",
		    sfr_adr, mcs51->sfrnames[sfr_adr]);
	} else {
		mcs51_trace(mcs51, "*** WRONG SFRFUNC 0x%02x %s <- %02x",
		    sfr_adr, mcs51->sfrnames[sfr_adr], what);
		mcs51->sfr[sfr_adr] = what;
	}
	return (mcs51->sfr[sfr_adr]);
}

static unsigned
mcs51_sfrfunc_default(struct mcs51 *mcs51, uint8_t sfr_adr, int what)
{
	if (what >= 0)
		mcs51->sfr[sfr_adr] = what;
	return (mcs51->sfr[sfr_adr]);
}

/*---------------------------------------------------------------------*/

static unsigned
mcs51_bitfunc_psw_p(struct mcs51 *mcs51, uint8_t bit_adr, int what)
{
	unsigned acc, par;

	(void)bit_adr;
	if (what == -1) {
		acc = mcs51->sfr[SFR_ACC];
		par = acc;
		par ^= (acc >> 1);
		par ^= (acc >> 2);
		par ^= (acc >> 3);
		par ^= (acc >> 4);
		par ^= (acc >> 5);
		par ^= (acc >> 6);
		par ^= (acc >> 7);
		par &= 1;
		mcs51_trace(mcs51, "Parity (0x%02x) = %x", mcs51->sfr[SFR_ACC], par);
		return (par);
	}
	return (0);
}

/*---------------------------------------------------------------------*/

uint8_t
MCS51_REG(struct mcs51 *mcs51, int reg)
{
	return (*mcs51_reg(mcs51, reg & 7));
}

/*---------------------------------------------------------------------*/

void
MCS51_TimerTick(struct mcs51 *mcs51)
{
	if (!(mcs51->sfr[SFR_TCON] & 0x10))
		return;
	mcs51->sfr[SFR_TL0]++;
	if (mcs51->sfr[SFR_TL0])
		return;
	mcs51->sfr[SFR_TH0]++;
	if (mcs51->sfr[SFR_TH0])
		return;
	mcs51->sfr[SFR_TCON] |= 0x20;
}

/*---------------------------------------------------------------------*/

void
MCS51_Reset(struct mcs51 *mcs51)
{
	// Intel 272383-002, Feb 94, Table 2, Page 2-9
	mcs51->sfr[SFR_ACC] = 0x00;
	mcs51->sfr[SFR_B] = 0x00;
	mcs51->sfr[SFR_PSW] = 0x00;
	mcs51->sfr[SFR_SP] = 0x07;
	mcs51->sfr[SFR_DPH] = 0x00;
	mcs51->sfr[SFR_DPL] = 0x00;
	mcs51->sfr[SFR_P0] = 0xff;
	mcs51->sfr[SFR_P1] = 0xff;
	mcs51->sfr[SFR_P2] = 0xff;
	mcs51->sfr[SFR_P3] = 0xff;
	mcs51->sfr[SFR_IP] = 0x00;
	mcs51->sfr[SFR_IE] = 0x00;
	mcs51->sfr[SFR_TMOD] = 0x00;
	mcs51->sfr[SFR_TCON] = 0x00;
	mcs51->sfr[SFR_SCON] = 0x00;
#ifdef SFR_T2CON
	mcs51->sfr[SFR_T2CON] = 0x00;
#endif
	mcs51->sfr[SFR_TH0] = 0x00;
	mcs51->sfr[SFR_TL0] = 0x00;
	mcs51->sfr[SFR_TH1] = 0x00;
	mcs51->sfr[SFR_TL1] = 0x00;
#ifdef SFR_TH2
	mcs51->sfr[SFR_TH2] = 0x00;
	mcs51->sfr[SFR_TL2] = 0x00;
#endif
#ifdef SFR_RCAP2H
	mcs51->sfr[SFR_RCAP2H] = 0x00;
	mcs51->sfr[SFR_RCAP2L] = 0x00;
#endif
	mcs51->sfr[SFR_SBUF] = 0x00;
	mcs51->sfr[SFR_PCON] = 0x00;
	mcs51->irq_state = 0;
	mcs51->pc = 0;
}

/*---------------------------------------------------------------------*/

void
MCS51_Rx(struct mcs51 *mcs51, uint8_t byte, uint8_t ninth)
{
	if (!(mcs51->sfr[SFR_SCON] & 0x10))
		return;
	if (mcs51->sfr[SFR_SCON] & 0x01)
		return;				// RX OVERRUN
	mcs51->sfr[SFR_SBUF] = byte;
	if (ninth)
		mcs51->sfr[SFR_SCON] |= 0x08;
	else
		mcs51->sfr[SFR_SCON] &= ~0x08;
	if (ninth || !(mcs51->sfr[SFR_SCON] & 0x20))
		mcs51->sfr[SFR_SCON] |= 0x01;
}

/*---------------------------------------------------------------------*/

int
MCS51_SetProgMem(struct mcs51 *mcs51, const void *ptr, size_t len)
{
	mcs51->progmem = realloc(mcs51->progmem, len);
	if (mcs51->progmem == NULL)
		return (mcs51_diag(mcs51, "Malloc failed"));
	(void)memcpy(mcs51->progmem, ptr, len);
	mcs51->progmem_size = len;
	return (0);
}

void
MCS51_SetSFR(struct mcs51 *mcs51, uint8_t adr, sfrfunc_f *func,
    const char *fmt, ...)
{
	char *name;
	va_list ap;

	assert(mcs51);
	assert(func);
	assert(fmt);
	va_start(ap, fmt);
	(void)vasprintf(&name, fmt, ap);
	assert(name != NULL);
	if (mcs51->sfrnames[adr] != NULL)
		free(mcs51->sfrnames[adr]);
	mcs51->sfrnames[adr] = name;
	mcs51->sfrfunc[adr] = func;
}

void
MCS51_SetBit(struct mcs51 *mcs51, uint8_t adr, bitfunc_f *func,
    const char *fmt, ...)
{
	char *name;
	va_list ap;

	assert(mcs51);
	assert(func);
	assert(fmt);
	va_start(ap, fmt);
	(void)vasprintf(&name, fmt, ap);
	assert(name != NULL);
	if (mcs51->bitnames[adr] != NULL)
		free(mcs51->bitnames[adr]);
	mcs51->bitnames[adr] = name;
	mcs51->bitfunc[adr] = func;
}

void
MCS51_SetSFRBits(struct mcs51 *mcs51, uint8_t adr, bitfunc_f *func,
    const char *b7, const char *b6, const char *b5, const char *b4,
    const char *b3, const char *b2, const char *b1, const char *b0)
{
	if (b0 == NULL) b0 = "0";
	if (b1 == NULL) b1 = "1";
	if (b2 == NULL) b2 = "2";
	if (b3 == NULL) b3 = "3";
	if (b4 == NULL) b4 = "4";
	if (b5 == NULL) b5 = "5";
	if (b6 == NULL) b6 = "6";
	if (b7 == NULL) b7 = "7";
	MCS51_SetBit(mcs51, adr + 0, func, "%s.%s", mcs51->sfrnames[adr], b0);
	MCS51_SetBit(mcs51, adr + 1, func, "%s.%s", mcs51->sfrnames[adr], b1);
	MCS51_SetBit(mcs51, adr + 2, func, "%s.%s", mcs51->sfrnames[adr], b2);
	MCS51_SetBit(mcs51, adr + 3, func, "%s.%s", mcs51->sfrnames[adr], b3);
	MCS51_SetBit(mcs51, adr + 4, func, "%s.%s", mcs51->sfrnames[adr], b4);
	MCS51_SetBit(mcs51, adr + 5, func, "%s.%s", mcs51->sfrnames[adr], b5);
	MCS51_SetBit(mcs51, adr + 6, func, "%s.%s", mcs51->sfrnames[adr], b6);
	MCS51_SetBit(mcs51, adr + 7, func, "%s.%s", mcs51->sfrnames[adr], b7);
}

struct mcs51 *
MCS51_Create(const char *ident)
{
	struct mcs51 *mcs51;
	unsigned u;

	mcs51 = calloc(sizeof *mcs51, 1);
	if (mcs51 == NULL)
		return (mcs51);

	mcs51->ident = strdup(ident);
	if (mcs51->ident == NULL) {
		free(mcs51);
		return (NULL);
	}

	mcs51->iram_size = 256;

	for (u = 0; u < 128; u++)
		MCS51_SetBit(mcs51, u, mcs51_bitfunc_ram,
		    "0x02x.%d", 0x20 + (u >> 3), u & 7);
	for (u = 128; u < 256; u++)
		MCS51_SetBit(mcs51, u, mcs51_bitfunc_wrong, "0x02x", u);

	for (u = 0; u < 256; u++)
		MCS51_SetSFR(mcs51, u, mcs51_sfrfunc_wrong, "0x%02x", u);

#define SFRMACRO(num, nam) MCS51_SetSFR(mcs51, num, mcs51_sfrfunc_wrong, #nam);
MCS51_SFRS
#undef SFRMACRO

	MCS51_SetSFR(mcs51, SFR_ACC, mcs51_sfrfunc_default, "ACC");
	MCS51_SetSFRBits(mcs51, SFR_ACC, mcs51_bitfunc_default,
	    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

	MCS51_SetSFR(mcs51, SFR_B, mcs51_sfrfunc_default, "B");
	MCS51_SetSFRBits(mcs51, SFR_B, mcs51_bitfunc_default,
	    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

	MCS51_SetSFR(mcs51, SFR_IP, mcs51_sfrfunc_default, "IP");
	MCS51_SetSFRBits(mcs51, SFR_IP, mcs51_bitfunc_default,
	    NULL, "PPC", "PT2", "PS", "PT1", "PX1", "PT0", "PX0");

	MCS51_SetSFR(mcs51, SFR_IE, mcs51_sfrfunc_default, "IE");
	MCS51_SetSFRBits(mcs51, SFR_IE, mcs51_bitfunc_default,
	    "EA", "EC", "ET2", "ES", "ET1", "EX1", "ET0", "EX0");

	MCS51_SetSFR(mcs51, SFR_TMOD, mcs51_sfrfunc_default, "TMOD");

	MCS51_SetSFR(mcs51, SFR_TCON, mcs51_sfrfunc_default, "TCON");
	MCS51_SetSFRBits(mcs51, SFR_TCON, mcs51_bitfunc_default,
	    "TF1", "TR1", "TF0", "TR0", "IE1", "IT1", "IE0", "IT0");

	MCS51_SetSFR(mcs51, SFR_T2CON, mcs51_sfrfunc_default, "T2CON");
	MCS51_SetSFRBits(mcs51, SFR_T2CON, mcs51_bitfunc_default,
	    "TF2", "EXF2", "RCLK", "TCLK", "EXEN2", "TR2", "C/T2", "CP/RL2");

	MCS51_SetSFR(mcs51, SFR_CCON, mcs51_sfrfunc_default, "CCON");
	MCS51_SetSFRBits(mcs51, SFR_CCON, mcs51_bitfunc_default,
	    "CF", "CR", NULL, "CCF4", "CCF3", "CCF2", "CCF1", "CCF0");

	MCS51_SetSFR(mcs51, SFR_SCON, mcs51_sfrfunc_default, "SCON");
	MCS51_SetSFRBits(mcs51, SFR_SCON, mcs51_bitfunc_default,
	    "SM0", "SM1", "SM2", "REN", "TB8", "RB8", "TI", "RI");

	MCS51_SetSFR(mcs51, SFR_SBUF, mcs51_sfrfunc_default, "SBUF");

	MCS51_SetSFR(mcs51, SFR_PSW, mcs51_sfrfunc_default, "PSW");
	MCS51_SetSFRBits(mcs51, SFR_PSW, mcs51_bitfunc_default,
	    "CY", "AC", "F0", "RS1", "RS0", "OV", NULL, "P");
	MCS51_SetBit(mcs51, SFR_PSW + 0, mcs51_bitfunc_psw_p, "PSW.p");

	MCS51_SetSFR(mcs51, SFR_SP, mcs51_sfrfunc_default, "SP");

	MCS51_Reset(mcs51);
	return (mcs51);
}
//lint -restore
