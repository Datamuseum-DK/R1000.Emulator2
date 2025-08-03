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
 * This file contains hotfixes to make things work and truncate spin/delay
 * loops (to reduce instruction tracing volume).
 *
 * Functional changes are segregated in *_function() functions.
 *
 */

#include <stdint.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Iop/memspace.h"
#include "Infra/vend.h"

static ioc_bpt_f Ioc_HotFix_Kernel;
static ioc_bpt_f Ioc_HotFix_Bootloader;

void
Ioc_HotFix_Ioc(void)
{

	ioc_breakpoint_rpn(0x80000088,
	    "'Hit self-test fail. ' regs ' ' stack ' ' finish");

	ioc_breakpoint_rpn(0x800000b4,
	    "'Self-test at ' .A6 ' Failed ' regs ' ' stack ' ' finish");

	ioc_breakpoint_rpn(0x80004d08,
	    "'Hit debugger ' regs ' ' stack ' ' finish");

	// skip_code(0x80001194, 0x800011a0, "RESHA TAPE SUB-TESTs");
}

void
Ioc_HotFix_Resha(void)
{

	ioc_breakpoint_rpn(0x00071286,
	    "'Hit RESHA self-test fail. ' regs ' ' stack ' ' finish");

	ioc_breakpoint_rpn(0x0007056e,
	    "'Hit RESHA self-test fail. ' regs ' ' stack ' ' finish");

	ioc_breakpoint_rpn(0x000766a2,
	    "'Hit RESHA self-test fail. ' regs ' ' stack ' ' finish");

	ioc_breakpoint_rpn(0x00071554,
	    "'Hit RESHA TAPE interrupt fail. ' regs ' ' stack ' ' finish");

	/*
	 * 0007678a 4e f0 01 e1 00 04          JMP     ((#4))
	 */
	ioc_breakpoint(0x0007678a, Ioc_HotFix_Kernel, NULL);

	/*
	 * 000741d4 20 7c 00 05 40 00          MOVEA.L #0x00054000,A0
	 * [...]
	 * 000741e6 4e d0                      JMP     (A0)
	 */
	ioc_breakpoint(0x00054000, Ioc_HotFix_Bootloader, NULL);
}

static int v_matchproto_(ioc_bpt_f)
Ioc_HotFix_Bootloader(void *priv, uint32_t adr)
{

	(void)priv;
	(void)adr;
	/*
	 * 000541ee 32 3c 7f ff                MOVE.W  #0x7fff,D1
	 * 000541f2 20 3c 00 00 05 00          MOVE.L  #0x00000500,D0
	 * 000541f8 53 80                      SUBQ.L  #0x1,D0
	 * 000541fa 66 fc                      BNE     0x541f8
	 * 000541fc 08 39 00 07 93 03 e8 1f    BTST.B  #0x7,IO_SCSI_D_1f_AUX_STATUS
	 * 00054204 66 1c                      BNE     0x54222
	 * 00054206 51 c9 ff ea                DBF     D1,0x541f2
	 */
	if (0 && m68k_debug_read_memory_32(0x541ee) == 0x323c7fff) {
		ioc_breakpoint_rpn(0x000541f2, "D1 0x2 min !D1");
		ioc_breakpoint_rpn(0x000541f8, "D0 0x2 min !D0");
	}

	/*
	 * 000540f6 4e f0 01 e1 00 04         JMP     ((#4))
	 */
	if (m68k_debug_read_memory_32(0x540f6) == 0x4ef001e1 &&
	    m68k_debug_read_memory_16(0x540fa) == 0x0004) {
		ioc_breakpoint(0x000540f6, Ioc_HotFix_Kernel, NULL);
	}
	return (1);
}

static int v_matchproto_(ioc_bpt_f)
Ioc_HotFix_Kernel(void *priv, uint32_t adr)
{
	(void)priv;
	(void)adr;
	cli_start_internal_syscall_tracing();
	return (0);
}
