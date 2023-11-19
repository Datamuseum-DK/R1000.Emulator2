/*-
 * Copyright (c) 2022 Poul-Henning Kamp
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

#include <stdlib.h>
#include <unistd.h>

#include "Infra/r1000.h"

static void v_matchproto_(cli_func_f)
cli_firmware_patch(struct cli *cli)
{
	unsigned offset, val;
	size_t sz;
	uint8_t *ptr;
	int i;
	char *err;

	if (cli->help || cli->ac < 3) {
		Cli_Usage(cli, "<offset> <byte>…", "Write bytes at offset.");
		return;
	}

	ptr = Firmware_Get(cli->av[1], &sz);
	if (ptr == NULL) {
		Cli_Error(cli, "Firmware image '%s' not found\n", cli->av[1]);
		return;
	}

	err = NULL;
	offset = strtoul(cli->av[2], &err, 0);
	if ((err != NULL && *err != '\0')) {
		Cli_Error(cli, "Cannot grog <offset>");
		return;
	}

	for (i = 3; cli->av[i] != NULL; i++) {
		if (offset >= sz) {
			Cli_Error(cli, "<offset> past end of firmware image.");
			return;
		}
		err = NULL;
		val = strtoul(cli->av[i], &err, 0);
		if ((err != NULL && *err != '\0') || val > 0xff) {
			Cli_Error(cli, "Cannot grog <byte> (%s)", cli->av[i]);
			return;
		}
		ptr[offset++] = val;
	}
}

/**********************************************************************/

static const struct cli_cmds cli_firmware_cmds[] = {
	{ "patch",		cli_firmware_patch },
	{ NULL,			NULL },
};

void v_matchproto_(cli_func_f)
cli_firmware(struct cli *cli)
{

	Cli_Dispatch(cli, cli_firmware_cmds);
}
