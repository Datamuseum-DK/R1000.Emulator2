/*-
 * Copyright (c) 2005-2020 Poul-Henning Kamp
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
 */

#ifndef INFRA_MICROTRACE_H
#define INFRA_MICROTRACE_H

void microtrace(const uint8_t *p, size_t l);

/*
 * Layout of microtrace entries:
 *
 * bytes  bits
 *   2    0 0 payload[14]
 *   2    0 1 0 0 X X X X payload[8]
 *   4    0 1 0 1 X X X X payload[24]
 *  10    0 1 1 0 X X X X payload[72]
 *  18    0 1 1 1 X X X X payload[136]
 *   4    1 payload[31]
 */

#define UTRACE_TABLE(UTRACE_MACRO) \
	UTRACE_MACRO(0x00, UADR, "Micro instruction address") \
	UTRACE_MACRO(0x40, CONS_RX, "Console RX char") \
	UTRACE_MACRO(0x41, CONS_TX, "Console TX char") \
	UTRACE_MACRO(0x42, REQ_FIFO_RD, "Read Request Fifo") \
	UTRACE_MACRO(0x43, REQ_FIFO_WR, "Write Request Fifo") \
	UTRACE_MACRO(0x44, RESP_FIFO_RD, "Read Response Fifo") \
	UTRACE_MACRO(0x45, RESP_FIFO_WR, "Write Response Fifo") \
	UTRACE_MACRO(0x50, CSEG, "Code Segment") \
	UTRACE_MACRO(0x51, CURINS, "Current Instruction") \
	UTRACE_MACRO(0x60, SCSI_D, "SCSI DISK CDB") \
	UTRACE_MACRO(0x61, SCSI_T, "SCSI TAPE CDB") \
	UTRACE_MACRO(0x62, RAM_RD, "IOP RAM read") \
	UTRACE_MACRO(0x63, RAM_WR, "IOP RAM write") \
	UTRACE_MACRO(0x70, MAILBOX, "Mailbox") \
	UTRACE_MACRO(0x71, ATAGMEM,  "A TAG memory") \
	UTRACE_MACRO(0x72, BTAGMEM,  "B TAG memory") \
	UTRACE_MACRO(0x80, DISP, "Code offset and display") \

enum microtrace {
	#define UTM(nbr, sym, what) UT_##sym = nbr,
		UTRACE_TABLE(UTM)
	#undef UTM
};

#endif /* INFRA_MICROTRACE_H */
