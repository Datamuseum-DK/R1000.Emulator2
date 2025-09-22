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

#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

#include "Infra/r1000.h"
#include "Infra/elastic.h"

struct acceptor_arg {
	struct elastic			*ep;
	int				fd;
	int				fd2;
	int				telnet;
	struct elastic_subscriber	*ws;
};

static void
elastic_fd_txfunc(void *priv, const void *src, size_t len)
{
	struct acceptor_arg *aa = priv;

	(void)write(aa->fd2, src, len);
}

/*--------------------------------------------------------------------*/

static void
report_sockadr(const char *name, int fd)
{
	int i;
	struct sockaddr_storage ss;
	socklen_t sl;
	char abuf[1024];
	char pbuf[1024];

	sl = sizeof ss;
	memset(&ss, 0, sizeof ss);
	i = getsockname(fd, (void*)&ss, &sl);
	assert(i == 0);

	i = getnameinfo((void*)&ss, sl, abuf, sizeof abuf, pbuf, sizeof pbuf,
	   NI_NUMERICHOST | NI_NUMERICSERV);
	if (i) {
		/*
		 * XXX this printf is shitty, but we may not have space
		 * for the gai_strerror in the bufffer :-(
		 */
		fprintf(stderr, "getnameinfo = %d %s\n", i, gai_strerror(i));
		if (i == EAI_SYSTEM)
			fprintf(stderr, "errno = %d %s\n", errno, strerror(errno));
		return;
	}
	printf("%s listening on %s %s\n", name, abuf, pbuf);
}

static void *
elastic_telnet_acceptor(void *priv)
{
	struct acceptor_arg aa;
	int fd;
	uint8_t buf[4];
	ssize_t sz;
	int skip;

	memcpy(&aa, priv, sizeof aa);
	free(priv);

	AZ(listen(aa.fd, 0));
	while (1) {
		fd = accept(aa.fd, NULL, NULL);
		aa.fd2 = fd;
		aa.ws = elastic_subscribe(aa.ep, elastic_fd_txfunc, &aa);

		buf[0] = 255;		// TELNET
		buf[1] = 251;		// WILL
		buf[2] = 1;		// ECHO
		(void)write(fd, buf, 3);

		buf[0] = 255;		// TELNET
		buf[1] = 251;		// WILL
		buf[2] = 3;		// SUPRESS_GO_AHEAD
		(void)write(fd, buf, 3);

		buf[0] = 255;		// TELNET
		buf[1] = 253;		// DO
		buf[2] = 3;		// SUPRESS_GO_AHEAD
		(void)write(fd, buf, 3);

		skip = 0;
		while (1) {
			sz = read(fd, buf, 1);
			if (sz <=  0) {
				elastic_unsubscribe(aa.ep, aa.ws);
				(void)(close(fd));
				break;
			} else if (sz == 1 && buf[0]) {
				if (skip) {
					skip--;
				} else if (buf[0] == 0xff) {
					skip = 2;
				} else {
					elastic_inject(aa.ep, buf, 1);
				}
			}
		}
	}
}

static void
elastic_telnet_passive(struct elastic *ep, struct cli *cli, const char *where)
{
	struct addrinfo hints, *res, *res0;
	int error, s, ns = 0;
	char *a, *p;
	struct acceptor_arg *aa;
	pthread_t pt;
	int val;

	a = strdup(where);
	AN(a);
	p = strchr(a, ':');
	if (p == NULL)
		p = strchr(a, ' ');
	AN(p);
	*p++ = '\0';

	memset(&hints, 0, sizeof hints);
	hints.ai_family = 0;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE;
	error = getaddrinfo(*a ? a : NULL, p, &hints, &res0);
	if (error) {
		free(a);
		Cli_Error(cli, "Error: %s\n", gai_strerror(error));
		return;
	}
	for (res = res0; res != NULL; res = res->ai_next) {
		s = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
		if (s < 0)
			continue;
		val = 1;
		AZ(setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &val, sizeof val));
		if (bind(s, res->ai_addr, res->ai_addrlen) < 0) {
			AZ(close(s));
			s = -1;
			continue;
		}
		aa = calloc(sizeof *aa, 1);
		AN(aa);
		aa->ep = ep;
		aa->fd = s;
		aa->telnet = 1;
		report_sockadr(aa->ep->name, aa->fd);
		AZ(pthread_create(&pt, NULL, elastic_telnet_acceptor, aa));
		ns++;
	}
	free(a);
	if (ns == 0)
		Cli_Error(cli, "Could not bind: %s\n", strerror(errno));
}

static void
elastic_tcp_active(struct elastic *ep, struct cli *cli, const char *where)
{
	struct addrinfo hints, *res, *res0;
	int error, s;
	char *a, *p;

	a = strdup(where);
	AN(a);
	p = strchr(a, ':');
	if (p == NULL)
		p = strchr(a, ' ');
	AN(p);
	*p++ = '\0';

	memset(&hints, 0, sizeof hints);
	hints.ai_family = PF_INET;
	hints.ai_socktype = SOCK_STREAM;
	error = getaddrinfo(a, p, &hints, &res0);
	if (error) {
		free(a);
		Cli_Error(cli, "Error: %s\n", gai_strerror(error));
		return;
	}
	s = -1;
	for (res = res0; res != NULL; res = res->ai_next) {
		s = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
		if (s < 0)
			continue;
		if (connect(s, res->ai_addr, res->ai_addrlen) < 0) {
			AZ(close(s));
			s = -1;
			continue;
		}
		break;
	}
	free(a);
	if (s == -1)
		Cli_Error(cli, "Could not connect: %s\n", strerror(errno));
	else
		(void)elastic_fd_start(ep, s, -1, 1);
}

void v_matchproto_(cli_func_f)
cli_elastic_tcp(struct cli *cli)
{
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "[<host>:]<port>", "Connect to TCP socket");
		return;
	}
	elastic_tcp_active(ep, cli, cli->av[1]);
}

void v_matchproto_(cli_func_f)
cli_elastic_telnet(struct cli *cli)
{
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "[<host>:]<port>", "Start TELNET server");
		return;
	}
	elastic_telnet_passive(ep, cli, cli->av[1]);
}
