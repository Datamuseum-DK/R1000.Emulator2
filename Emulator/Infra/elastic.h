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

struct elastic_match;

typedef void elastic_deliver_f(void *priv, const void *, size_t);

struct chunk {
	VTAILQ_ENTRY(chunk)		next;
	uint8_t				*ptr;
	ssize_t				len;
	ssize_t				read;
};

struct elastic_subscriber {
	VTAILQ_ENTRY(elastic_subscriber)	next;
	struct elastic			*ep;
	elastic_deliver_f		*func;
	void				*priv;
	pthread_t			thread;
	int				die;
	pthread_cond_t			cond;
	VTAILQ_HEAD(,chunk)		chunks;
};

struct elastic {
	VTAILQ_HEAD(,elastic_subscriber)	subscribers;
	VTAILQ_HEAD(,chunk)		chunks_out;
	VTAILQ_HEAD(,chunk)		chunks_in;
	int				text;
	int				mode;
	nanosec				bits_per_char;
	nanosec				bits_per_sec;
	pthread_mutex_t			mtx;
	pthread_cond_t			cond_in;
	pthread_cond_t			cond_out;

	struct elastic_match		*em;
	struct elastic_fd		*out;
	cli_func_f			*break_function;
};

struct elastic *elastic_new(int mode);
nanosec elastic_nsec_per_char(const struct elastic *ep);

/* "output" side */
int elastic_subscriber_fetch(struct elastic_subscriber **espp,
    void **pptr, size_t *plen);
struct elastic_subscriber *elastic_subscribe(struct elastic *ep,
    elastic_deliver_f *, void *);
void elastic_unsubscribe(struct elastic *ep, struct elastic_subscriber *);
void elastic_inject(struct elastic *ep, const void *ptr, ssize_t len);

/* "input" side */
void elastic_put(struct elastic *ep, const void *ptr, ssize_t len);
int elastic_drain(struct elastic *ep);
ssize_t elastic_get(struct elastic *ep, void *ptr, ssize_t len);
int elastic_empty(const struct elastic *ep);

void Elastic_Cli(struct elastic *, struct cli *);
cli_func_f cli_elastic_serial;
cli_func_f cli_elastic_input;
cli_func_f cli_elastic_output;
cli_func_f cli_elastic_tcp;
cli_func_f cli_elastic_telnet;
cli_func_f cli_elastic_match;

struct elastic_fd *elastic_fd_start(
    struct elastic *ep, int fd, int mode, int selfdestruct);
void elastic_fd_stop(struct elastic_fd **efpp);

