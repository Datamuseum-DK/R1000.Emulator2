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

static void
skip_code(unsigned int from, unsigned int to, const char *why)
{
	char buf[100];

	bprintf(buf, ".PC ' => ' 0x%x !PC .PC ' Skipping %s'", to, why);
	ioc_breakpoint_rpn(from, buf);
}

static void
hotfix_ioc_functional(void)
{

	ioc_breakpoint_rpn(0x80000088,
	    "'Hit self-test fail. ' regs ' ' stack ' ' finish");

	ioc_breakpoint_rpn(0x800000b4,
	    "'Self-test at ' .A6 ' Failed ' regs ' ' stack ' ' finish");

	ioc_breakpoint_rpn(0x80004d08,
	    "'Hit debugger ' regs ' ' stack ' ' finish");

	skip_code(0x80000568, 0x800007d0, "Memory parity");
	skip_code(0x800007f4, 0x800009b2, "I/O Bus control");
	skip_code(0x800009da, 0x80000a4a, "I/O Bus map parity");
	skip_code(0x80000a74, 0x80000b8a, "I/O bus transactions");
	skip_code(0x80001170, 0x8000117c, "RESHA VME sub-tests");
	skip_code(0x8000117c, 0x80001188, "RESHA LANCE sub-tests");
	// Local interrupts test
	skip_code(0x800011dc, 0x800011fc, "Local interrupts (vector 0x50)");
	skip_code(0x8000127a, 0x80001298, "Local interrupts (vector 0x51)");
	skip_code(0x80001358, 0x80001470, "Local interrupts (vector 0x52)");
	skip_code(0x80001502, 0x800015ce, "Illegal reference protection");
	skip_code(0x800015f2, 0x8000166c, "I/O bus parity");
	skip_code(0x8000169c, 0x800016d8, "I/O bus spurious interrupts");
	skip_code(0x80001700, 0x80001746, "Temperature sensors");
	skip_code(0x80001774, 0x800017f8, "IOC diagnostic processor");
	skip_code(0x80001880, 0x8000197c, "Clock margining");

	// If this is skipped we get 'No SCSI interrupt: Hard reset'
	// skip_code(0x80001188, 0x80001194, "RESHA DISK SUB-TESTs");
}

void
Ioc_HotFix_Ioc(void)
{

	hotfix_ioc_functional();

	skip_code(0x800001e4, 0x8000021a, "EEPROM CHECKSUM");
	skip_code(0x800003a4, 0x80000546, "512k RAM Test");
	skip_code(0x80000ba2, 0x80000bf2, "PIT  (=> DUART)");
	skip_code(0x80000c1a, 0x80000d20, "Modem DUART channel");
	skip_code(0x80000d4e, 0x80000dd6, "Diagnostic DUART channel");
	skip_code(0x80000dfc, 0x80000ec4, "Clock / Calendar");
	skip_code(0x80000fa0, 0x80000fda, "RESHA EEProm Interface ...");
	// skip_code(0x80001194, 0x800011a0, "RESHA TAPE SUB-TESTs");
	skip_code(0x8000181c, 0x8000185c, "Power margining");
	skip_code(0x80001982, 0x80001992, "final check");

	/*
	 * 80000060 20 3c 00 00 82 35          MOVE.L  #0x00008235,D0
	 * 80000066 51 c8 ff fe                DBF     D0,0x80000066
	 */
	ioc_breakpoint_rpn(0x80000066, "D0 0xa min !D0");

	/*
	 * 800000fe 20 3c 00 01 04 6a          MOVE.L  #0x0001046a,D0
	 * 80000104 53 80                      SUBQ.L  #0x1,D0
	 */
	ioc_breakpoint_rpn(0x80000104, "D0 0xa min !D0");

	/*
	 * 80000132 20 3c 00 00 82 35          MOVE.L  #0x00008235,D0
	 * 80000138 51 c8 ff fe                DBF     D0,0x80000138
	 */
	ioc_breakpoint_rpn(0x80000138, "D0 0xa min !D0");

	/*
	 * 80000338 20 3c 00 00 82 35          MOVE.L  #0x00008235,D0
	 * 8000033e 51 c8 ff fe                DBF     D0,0x8000033e
	 */
	ioc_breakpoint_rpn(0x8000033e, "D0 0xa min !D0");

	/*
	 * 80000348 20 3c 00 00 82 35          MOVE.L  #0x00008235,D0
	 * 8000034e 51 c8 ff fe                DBF     D0,0x8000034e
	 */
	ioc_breakpoint_rpn(0x8000034e, "D0 0xa min !D0");

}

static void
ioc_hotfix_resha_functional(void)
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

void
Ioc_HotFix_Resha(void)
{

	ioc_hotfix_resha_functional();

	/*
	 * 00077176 24 3c 00 0b 42 0f          MOVE.L  #0x000b420f,D2
	 * 0007717c 08 38 00 01 90 01          BTST.B  #0x1,IO_UART_STATUS
	 * 00077182 67 1e                      BEQ     0x771a2
	 */
	ioc_breakpoint_rpn(0x0007717c, "D2 0xa min !D2");

	/*
	 * 00074588 20 3c 00 00 05 00          MOVE.L  #0x00000500,D0
	 * 0007458e 53 80                      SUBQ.L  #0x1,D0
	 * 00074590 66 fc                      BNE     0x7458e
	 */
	ioc_breakpoint_rpn(0x0007458e, "D0 0xa min !D0");

	/*
	 * 00077386                    SCSI_T_AWAIT_INTERRUPT():
	 * 00077386 2f 00                      MOVE.L  D0,-(A7)
	 * 00077388 20 3c 00 00 05 00          MOVE.L  #0x00000500,D0
	 * 0007738e 53 80                      SUBQ.L  #0x1,D0
	 * 00077390 66 fc                      BNE     0x7738e
	 */
	ioc_breakpoint_rpn(0x0007738e, "D0 0xa min !D0");

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

static void
hotfix_kernel_4_2_14(void)
{
	/*
	 * 0000648e 20 3c 00 23 7c 4d          MOVE.L  #0x00237c4d,D0
	 * 00006494 53 80                      SUBQ.L  #0x1,D0
	 */
	ioc_breakpoint_rpn(0x00006494, "D0 0xa min !D0");

	/*
	 * 00009234 20 3c 00 03 ff ff          MOVE.L  #0x0003ffff,D0
	 * 0000923a 13 fc 00 0a 93 03 ec 00    MOVE.B  #0x0a,IO_SCSI_T_00_OWN_ID_CDB_SIZE
	 * 00009242 13 fc 00 00 93 03 ec 18    MOVE.B  #0x00,IO_SCSI_T_18_CMD
	 * 0000924a 4e b9 00 00 92 10          JSR     0x9210
	 */
	ioc_breakpoint_rpn(0x0000923a, "D0 0xa min !D0");

	/*
	 * 00009442 20 3c 00 03 ff ff          MOVE.L  #0x0003ffff,D0
	 * 00009448 33 fc 00 30 93 03 e0 08    MOVE.W  #0x0030,IO_RESHA_RES_CTL
	 * 00009450 4e b9 00 00 92 10          JSR     0x9210
	 */
	ioc_breakpoint_rpn(0x00009448, "D0 0xa min !D0");

	/*
	 * 00009512 20 3c 00 07 ff ff          MOVE.L  #0x0007ffff,D0
	 * 00009518 33 fc 00 30 93 03 e0 08    MOVE.W  #0x0030,IO_RESHA_RES_CTL
	 * 00009520 4e b9 00 00 92 10          JSR     0x9210
	 */
	ioc_breakpoint_rpn(0x00009518, "D0 0xa min !D0");

	/*
	 * 00009572 30 3c 7f ff                MOVE.W  #0x7fff,D0
	 * 00009576 53 40                      SUBQ.W  #0x1,D0
	 * 00009578 6c fc                      BGE     0x9576
	 * 0000957a 30 3c 7f ff                MOVE.W  #0x7fff,D0
	 * 0000957e 4e b9 00 00 91 ec          JSR     0x91ec
	 */
	ioc_breakpoint_rpn(0x00009576, "D0 0xa min !D0");

	/*
	 * 00005c52 20 3c 00 00 05 00          MOVE.L #0x00000500,D0
	 * 00005c58 53 80                      SUBQ.L #0x1,D0
	 * 00005c5a 66 fc                      BNE 0x5c58
	 * 00005c5c 51 c9 ff f4                DBF D1,0x5c52
	 */
	ioc_breakpoint_rpn(0x00005c58, "D0 0xa min !D0");
}

static void
hotfix_kernel_4_2_18(void)
{
	/*
	 * 00005d14                    DELAY_LOOP(D1):
	 * 00005d14 2f 00                      MOVE.L  D0,-(A7)
	 * 00005d16 20 3c 00 00 05 00          MOVE.L  #0x00000500,D0
	 * 00005d1c 53 80                      SUBQ.L  #0x1,D0
	 * 00005d1e 66 fc                      BNE     0x5d1c
	 * 00005d20 51 c9 ff f4                DBF     D1,0x5d16
	 * 00005d24 20 1f                      MOVE.L  (A7)+,D0
	 * 00005d26 4e 75                      RTS
	 */
	ioc_breakpoint_rpn(0x00005d1c, "D0 0x20 min !D0");

	/*
	 * 000066d0 20 3c 00 23 7c 4d     MOVE.L  #0x00237c4d,D0
	 * 000066d6 53 80                 SUBQ.L  #0x1,D0
	 * 000066d8 66 fc                 BNE     0x66d6
	 */
	ioc_breakpoint_rpn(0x000066d6, "D0 0x20 min !D0");

	/*
	 * 00009818 20 3c 00 03 ff ff          MOVE.L  #0x0003ffff,D0
	 * 0000981e 13 fc 00 0a 93 03 ec 00    MOVE.B  #0x0a,IO_SCSI_T_00_OWN_ID_CDB_SIZE
	 * 00009826 13 fc 00 00 93 03 ec 18    MOVE.B  #0x00,IO_SCSI_T_18_CMD
	 * 0000982e 4e b9 00 00 97 f4          JSR     0x97f4
	 */
	ioc_breakpoint_rpn(0x0000981e, "D0 0x400 min !D0");

	/*
	 * 00009af6 20 3c 00 07 ff ff          MOVE.L  #0x0007ffff,D0
	 * 00009afc 33 fc 00 30 93 03 e0 08    MOVE.W  #0x0030,IO_RESHA_RES_CTL
	 * 00009b04 4e b9 00 00 97 f4          JSR     0x97f4
	 */
	ioc_breakpoint_rpn(0x00009afc, "D0 0x20 min !D0");

	/*
	 * 00009b56 30 3c 7f ff                MOVE.W  #0x7fff,D0
	 * 00009b5a 53 40                      SUBQ.W  #0x1,D0
	 * 00009b5c 6c fc                      BGE     0x9b5a
	 * 00009b5e 30 3c 7f ff                MOVE.W  #0x7fff,D0
	 * 00009b62 4e b9 00 00 97 d0          JSR     0x97d0
	 * 00009b68 0c 00 00 42                CMPI.B  #0x42,D0
	 */
	ioc_breakpoint_rpn(0x00009b5a, "D0 0x20 min !D0");

	ioc_breakpoint_rpn(0x00008ab8,
	    "'Hit Estop. ' regs ' ' stack ' ' finish");
}

static int v_matchproto_(ioc_bpt_f)
Ioc_HotFix_Kernel(void *priv, uint32_t adr)
{
	unsigned u, v;
	char buf[BUFSIZ];

	(void)priv;
	(void)adr;
	for (u = 0; u < 0x800; u++)
		if (m68k_debug_read_memory_8(u) == 0x40 &&
		    m68k_debug_read_memory_32(u) == 0x40282329)
			break;
	if (u == 0x800) {
		printf("Kernel not recognized, no patches applied.\n");
		return (0);
	}
	for (v = 0; v < BUFSIZ; v++) {
		switch(m68k_debug_read_memory_8(u + v)) {
		case 0x00:
		case 0x0a:
		case 0x22:
		case 0x3e:
		case 0x5c:
			buf[v] = '\0';
			break;
		default:
			buf[v] = m68k_debug_read_memory_8(u + v);
			continue;
		}
		break;
	}
	if (!strcmp(buf, "@(#)400S IOP KERNEL,4_2_18,92/08/06,16:15:00")) {
		hotfix_kernel_4_2_18();
	} else if (!strcmp(buf,
	    "@(#)400S IOP KERNEL,4_2_14,92/05/07,16:15:00")) {
		hotfix_kernel_4_2_14();
	} else {
		printf("No hotfix for kernel %s\n", buf);
		return (0);
	}
	printf("Hotfixes applied to kernel %s\n", buf);
	cli_start_internal_syscall_tracing();
	return (0);
}
