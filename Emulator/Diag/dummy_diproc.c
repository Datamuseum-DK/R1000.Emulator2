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

#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Infra/vsb.h"
#include "Diag/diag.h"
#include "Diag/diagproc.h"

#include "Infra/elastic.h"

struct i8052 {
	const char			*name;
	uint8_t				address;
	uint8_t				ram[256];
	struct elastic_subscriber	*esp;
	pthread_t			thread;
	unsigned			response;
};

static void
i8052_tx_diagbus(const struct i8052 *i52, uint8_t x)
{
	Trace(trace_diagbus, "%s_DUMMY TX 0x%02x", i52->name, x);
	elastic_inject(diag_elastic, &x, 1);
}

static unsigned
i8052_rx_diagbus(struct i8052 *i52)
{
	void *ptr;
	size_t len;
	uint8_t *u8p;
	unsigned retval;

	AN(elastic_subscriber_fetch(&i52->esp, &ptr, &len));
	assert(len == 2);
	u8p = ptr;
	assert(u8p[0] < 2);
	retval = u8p[0]<<8;
	retval |= u8p[1];
	free(ptr);
	return (retval);
}

#define UPDATE_KOOPMAN32(hashvar, newbyte) \
	do { \
		hashvar = (((hashvar) << 32) + (newbyte)) % 0xFFFFFFFB; \
	} while (0)

static void *
i8052_thread(void *priv)
{
	struct i8052 *i52 = priv;
	struct diagproc dp[1];
	uint8_t csum, counter, pointer, reply;
	unsigned u;
	uint8_t u8;
	struct vsb *vsb;
	uint64_t hash;
	int me;

	vsb = VSB_new_auto();
	AN(vsb);

	dp->ip = &dp->ram[0];
	dp->name = i52->name;
	dp->ram = i52->ram;

	reply = 0;
	while (1) {
		u = i8052_rx_diagbus(i52);
		if (!(u & 0x100))
			continue;
		me = (u & 0x1f) == i52->address;
		if (!me)
			continue;
		u8 = u & 0xff;
		switch (u8 >> 4) {
		case 0x0:
			if (reply && i52->response != (int)DIPROC_RESPONSE_TIMEOUT) {
				i8052_tx_diagbus(i52, reply);
			} else {
				i8052_tx_diagbus(i52, i52->response);
			}
			reply = 0;
			break;
		case 0x2:
			pointer = i8052_rx_diagbus(i52);
			counter = i8052_rx_diagbus(i52);
			csum = 0;
			i52->ram[0x11] = 0x02;
			VSB_clear(vsb);
			VSB_printf(vsb, " %02x", i52->ram[0x11]);
			i8052_tx_diagbus(i52, i52->ram[0x11]);
			csum += i52->ram[0x11];
			while (counter--) {
				u8 = i52->ram[pointer++];
				csum += u8;
				i8052_tx_diagbus(i52, u8);
				VSB_printf(vsb, " %02x", u8);
			}
			i8052_tx_diagbus(i52, csum);
			AZ(VSB_finish(vsb));
			break;
		case 0x8:
			reply = (int)DIPROC_RESPONSE_RESET;
			break;
		case 0xa:
			pointer = 0x10;
			csum = 0;
			hash = 0;
			counter = i8052_rx_diagbus(i52);
			hash = 0;
			csum += counter;
			VSB_clear(vsb);
			UPDATE_KOOPMAN32(hash, counter);
			while (counter--) {
				u8 = i8052_rx_diagbus(i52);
				csum += u8;
				if (counter > 0 && (pointer <= 0x10 || pointer >= i52->ram[0x10])) {
					UPDATE_KOOPMAN32(hash, u8);
				}
				i52->ram[pointer++] = u8;
				VSB_printf(vsb, " %02x", u8);
			}
			AZ(VSB_finish(vsb));
			assert (csum == i8052_rx_diagbus(i52));
			UPDATE_KOOPMAN32(hash, 0);
			dp->dl_hash = hash;
			dp->ip = &dp->ram[0];
			if (i52->address == 0x6) {
				diagproc_turbo_typ(dp);
			} else if (i52->address == 0xc) {
				dp->ip = &dp->ram[0];
				diagproc_turbo_mem32(dp);
			}
			break;
		default:
			break;
		}
	}
}

static void
i8052_start(unsigned address, const char *name, unsigned response)
{
	struct i8052 *i52;

	i52 = calloc(sizeof *i52, 1);
	AN(i52);
	i52->name = name;
	i52->address = address;
	i52->response = response;
	i52->esp = elastic_subscribe(diag_elastic, NULL, NULL);
	AZ(pthread_create(&i52->thread, NULL, i8052_thread, i52));
}

void v_matchproto_(cli_func_f)
cli_diproc_dummy(struct cli *cli)
{
	int i;
	unsigned response = (int)DIPROC_RESPONSE_DONE;

	if (cli->help || cli->ac < 2) {
		Cli_Usage(cli, "[-<status>] <board> …",
		    "Implement dummy DIPROC.  Default status is OK."
		);
		if (cli->ac == 1) {
			cli_diproc_help_status(cli);
			cli_diproc_help_board(cli);
		}
		return;
	}
	for (i = 1; i < cli->ac; i++) {
		if (cli->av[i][0] == '-') {
#define RESPONSE(num, name) \
			if (!strcasecmp(#name, cli->av[i] + 1)) { \
				response = num; \
				continue; \
			}
			RESPONSE_TABLE(RESPONSE)
#undef RESPONSE
			Cli_Error(cli, "Unknown response: \"%s\"\n",
			    cli->av[i]);
			return;
		}
#define BOARD(upper, lower, address) \
		if (!strcasecmp(cli->av[i], #lower)) { \
			i8052_start(address, "DUMMY_" #upper, response); \
			continue; \
		}
		BOARD_TABLE(BOARD)
#undef BOARD
		Cli_Error(cli, "Unknown diproc: \"%s\"\n", cli->av[i]);
		return;
	}
}
