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

#include <fcntl.h>
#include <stdlib.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Infra/elastic.h"

struct elastic *
elastic_new(int mode, const char *name)
{
	struct elastic *ep;

	AN(name);
	ep = calloc(1, sizeof *ep);
	AN(ep);
	VTAILQ_INIT(&ep->chunks_in);
	VTAILQ_INIT(&ep->chunks_out);
	VTAILQ_INIT(&ep->subscribers);
	AZ(pthread_mutex_init(&ep->mtx, NULL));
	AZ(pthread_cond_init(&ep->cond_in, NULL));
	AZ(pthread_cond_init(&ep->cond_out, NULL));
	assert(mode == O_RDONLY || mode == O_RDWR || mode == O_WRONLY);
	ep->text = 1;
	ep->mode = mode;
	ep->bits_per_char = 8;
	ep->name = strdup(name);
	AN(ep->name);
	return (ep);
}

/* Output Subscriptions ***********************************************/

int
elastic_subscriber_fetch(struct elastic_subscriber **espp,
    void **pptr, size_t *plen)
{
	struct elastic_subscriber *esp;
	struct chunk *cp;
	struct elastic *ep;

	AN(espp);
	esp = *espp;
	AN(esp);
	ep = esp->ep;
	AN(ep);

	AZ(pthread_mutex_lock(&ep->mtx));
	while (!esp->die && VTAILQ_EMPTY(&esp->chunks)) {
		AZ(pthread_cond_signal(&esp->ep->cond_out));
		AZ(pthread_cond_wait(&esp->cond, &ep->mtx));
	}
	cp = VTAILQ_FIRST(&esp->chunks);
	if (cp != NULL)
		VTAILQ_REMOVE(&esp->chunks, cp, next);
	AZ(pthread_mutex_unlock(&ep->mtx));

	if (cp != NULL) {
		*pptr = cp->ptr;
		*plen = cp->len;
		free(cp);
		return (1);
	}
	AN(esp->die);
	*pptr = NULL;
	*plen = 0;
	AZ(pthread_cond_destroy(&esp->cond));
	free(esp);
	*espp = NULL;
	return (0);
}

static void *
elastic_subscriber_thread(void *priv)
{
	struct elastic_subscriber *esp = priv;
	void *ptr;
	size_t len;

	AN(esp->func);
	AN(esp->priv);
	while (elastic_subscriber_fetch(&esp, &ptr, &len)) {
		AN(ptr);
		AN(len);
		esp->func(esp->priv, ptr, len);
		free(ptr);
	}
	return (NULL);
}

struct elastic_subscriber *
elastic_subscribe(struct elastic *ep, elastic_deliver_f *func, void *priv)
{
	struct elastic_subscriber *esp;

	assert(ep->mode != O_RDONLY);
	esp = calloc(1, sizeof *esp);
	AN(esp);
	esp->ep = ep;
	esp->func = func;
	esp->priv = priv;
	AZ(pthread_cond_init(&esp->cond, NULL));
	VTAILQ_INIT(&esp->chunks);
	AZ(pthread_mutex_lock(&ep->mtx));
	VTAILQ_INSERT_TAIL(&ep->subscribers, esp, next);
	if (!VTAILQ_EMPTY(&ep->chunks_out))
		VTAILQ_CONCAT(&esp->chunks, &ep->chunks_out, next);
	AZ(pthread_mutex_unlock(&ep->mtx));
	if (esp->func != NULL) {
		AZ(pthread_create(&esp->thread, NULL,
		    elastic_subscriber_thread, esp));
		AZ(pthread_detach(esp->thread));
	}
	return (esp);
}

void
elastic_unsubscribe(struct elastic *ep, struct elastic_subscriber *esp)
{

	AN(ep);
	AN(esp);
	AZ(pthread_mutex_lock(&ep->mtx));
	esp->die = 1;
	VTAILQ_REMOVE(&ep->subscribers, esp, next);
	AZ(pthread_mutex_unlock(&ep->mtx));
	AZ(pthread_cond_signal(&esp->cond));
}

/* Input injections ***************************************************/

void
elastic_inject(struct elastic *ep, const void *ptr, ssize_t len)
{
	struct chunk *cp;

	if (len < 0)
		len = strlen(ptr);
	if (len == 0)
		return;
	cp = calloc(1, sizeof *cp);
	AN(cp);
	cp->ptr = malloc(len);
	AN(cp->ptr);
	memcpy(cp->ptr, ptr, len);
	cp->len = len;
	AZ(pthread_mutex_lock(&ep->mtx));
	VTAILQ_INSERT_TAIL(&ep->chunks_in, cp, next);
	AZ(pthread_cond_signal(&ep->cond_in));
	AZ(pthread_mutex_unlock(&ep->mtx));
}

/* Driver Interface ***************************************************/

nanosec
elastic_nsec_per_char(const struct elastic *ep)
{

	AN(ep);
	return(ep->bits_per_char * 1000000000 / ep->bits_per_sec);
}

static struct chunk *
mk_chunk(const void *ptr, ssize_t len)
{
	struct chunk *cp;

	cp = calloc(1, sizeof *cp);
	AN(cp);
	cp->ptr = malloc(len);
	AN(cp->ptr);
	memcpy(cp->ptr, ptr, len);
	cp->len = len;
	return (cp);
}

void
elastic_put(struct elastic *ep, const void *ptr, ssize_t len)
{
	struct chunk *cp;
	struct elastic_subscriber *esp;

	assert(ep->mode != O_RDONLY);
	if (len < 0)
		len = strlen(ptr);
	if (len == 0)
		return;
	AZ(pthread_mutex_lock(&ep->mtx));
	if (VTAILQ_EMPTY(&ep->subscribers)) {
		cp = mk_chunk(ptr, len);
		VTAILQ_INSERT_TAIL(&ep->chunks_out, cp, next);
	} else {
		VTAILQ_FOREACH(esp, &ep->subscribers, next) {
			cp = mk_chunk(ptr, len);
			VTAILQ_INSERT_TAIL(&esp->chunks, cp, next);
			AZ(pthread_cond_signal(&esp->cond));
		}
	}
	AZ(pthread_mutex_unlock(&ep->mtx));
}

int
elastic_drain(struct elastic *ep)
{
	struct elastic_subscriber *esp;
	int busy = 0;

	if (VTAILQ_EMPTY(&ep->subscribers))
		return (-1);
	do {
		AZ(pthread_mutex_lock(&ep->mtx));
		busy = 0;
		VTAILQ_FOREACH(esp, &ep->subscribers, next)
			if (!VTAILQ_EMPTY(&esp->chunks))
				busy = 1;
		if (busy)
			AZ(pthread_cond_wait(&ep->cond_out, &ep->mtx));
		AZ(pthread_mutex_unlock(&ep->mtx));
	} while(busy);
	return (0);
}

ssize_t
elastic_get(struct elastic *ep, void *ptr, ssize_t len)
{
	struct chunk *cp;

	assert(ep->mode != O_WRONLY);
	AZ(pthread_mutex_lock(&ep->mtx));
	while (VTAILQ_EMPTY(&ep->chunks_in))
		AZ(pthread_cond_wait(&ep->cond_in, &ep->mtx));
	cp = VTAILQ_FIRST(&ep->chunks_in);
	if (cp->len - cp->read < len)
		len = cp->len - cp->read;
	memcpy(ptr, cp->ptr + cp->read, len);
	cp->read += len;
	if (cp->read == cp->len) {
		VTAILQ_REMOVE(&ep->chunks_in, cp, next);
		free(cp->ptr);
		free(cp);
	}
	AZ(pthread_mutex_unlock(&ep->mtx));
	return (len);
}

int
elastic_empty(const struct elastic *ep)
{
	return(VTAILQ_EMPTY(&ep->chunks_in));
}

static void v_matchproto_(cli_func_f)
cli_elastic_baud(struct cli *cli)
{
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<baud>", "Set speed in bits per second.");
		return;
	}
	ep->bits_per_sec = atoi(cli->av[1]);
}

static void v_matchproto_(cli_func_f)
cli_elastic_binary(struct cli *cli)
{
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL, "Set Binary Mode.");
		return;
	}
	ep->text = 0;
}

static void v_matchproto_(cli_func_f)
cli_elastic_cps(struct cli *cli)
{
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<cps>", "Set speed in characters per second.");
		return;
	}
	ep->bits_per_sec = atoi(cli->av[1]) * ep->bits_per_char;
}

static void v_matchproto_(cli_func_f)
cli_elastic_hex(struct cli *cli)
{
	struct elastic *ep = cli->elastic;
	uint8_t u8;
	int i;

	if (cli->help || cli->ac < 2) {
		Cli_Usage(cli, "<hex> …", "Inject bytes in hexadecimal.");
		return;
	}
	for (i = 1; i < cli->ac; i++) {
		u8 = (uint8_t)strtoul(cli->av[i], NULL, 16);
		elastic_inject(ep, &u8, 1);
	}
}

static void v_matchproto_(cli_func_f)
cli_elastic_here(struct cli *cli)
{
	struct elastic *ep = cli->elastic;
	int i;

	if (cli->help || cli->ac < 2) {
		Cli_Usage(cli, "<string> …", "Inject strings with CR.");
		return;
	}
	for (i = 1; i < cli->ac; i++) {
		elastic_inject(ep, cli->av[i], -1);
		elastic_inject(ep, "\r", -1);
	}
}

static void v_matchproto_(cli_func_f)
cli_elastic_text(struct cli *cli)
{
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL, "Set Text Mode.");
		return;
	}
	ep->text = 1;
}

static void v_matchproto_(cli_func_f)
cli_elastic_break(struct cli *cli)
{
	struct elastic *ep = cli->elastic;

	if (ep->break_function != NULL)
		ep->break_function(cli);
}

static const struct cli_cmds cli_elastic_cmds[] = {
	{ "<",			cli_elastic_input },
	{ "<<",			cli_elastic_here },
	{ ">",			cli_elastic_output },
	{ ">>",			cli_elastic_output },
	{ "baud",		cli_elastic_baud },
	{ "binary",		cli_elastic_binary },
	{ "break",		cli_elastic_break },
	{ "cps",		cli_elastic_cps },
	{ "hex",		cli_elastic_hex },
	{ "match",		cli_elastic_match },
	{ "serial",		cli_elastic_serial },
	{ "tcp",		cli_elastic_tcp },
	{ "telnet",		cli_elastic_telnet },
	{ "text",		cli_elastic_text },
	{ NULL,			NULL },
};

void
Elastic_Cli(struct elastic *ep, struct cli *cli)
{

	AN(ep);
	AZ(cli->elastic);
	cli->elastic = ep;
	Cli_Dispatch(cli, cli_elastic_cmds);
	cli->elastic = NULL;
}
