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
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Iop/memspace.h"
#include "Infra/vend.h"

static uint8_t resha_eeprom[32768];

void
ioc_load_eeproms(void)
{
	uint8_t tmp[0x8000];

	Firmware_Copy(tmp, sizeof tmp, "IOC_EEPROM");
	memcpy(ioc_eeprom_space + 0x0000, tmp + 0x0000, 0x2000);
	memcpy(ioc_eeprom_space + 0x2000, tmp + 0x4000, 0x2000);
	memcpy(ioc_eeprom_space + 0x4000, tmp + 0x2000, 0x2000);
	memcpy(ioc_eeprom_space + 0x6000, tmp + 0x6000, 0x2000);

	Ioc_HotFix_Ioc();

	Firmware_Copy(resha_eeprom, sizeof resha_eeprom, "RESHA_EEPROM");

	Ioc_HotFix_Resha();
}

/**********************************************************************/

void v_matchproto_(mem_post_write)
resha_page_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	(void)debug;
	(void)width;
	(void)adr;
	// See 0x80000fa8-80000fb4
	space[1] = space[0];
}

void v_matchproto_(mem_pre_read)
resha_eeprom_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	unsigned u;

	(void)debug;
	(void)width;
	u = (resha_page_space[0] << 8) | adr;
	u &= 0x7fff;
	memcpy(space + adr, resha_eeprom + u, width);
}
