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
#include <termios.h>

#include "Infra/r1000.h"
#include "Infra/elastic.h"

struct elastic_fd {
	struct elastic			*ep;
	int				fd;
	int				has_thread;
	int				selfdestruct;
	pthread_t			rxt;
	struct elastic_subscriber	*ws;
};

static void *
elastic_fd_rxthread(void *priv)
{
	struct elastic_fd *efp = priv;
	char buf[1];
	ssize_t sz;

	while (1) {
		sz = read(efp->fd, buf, 1);
		if (sz != 1)
			break;
		elastic_inject(efp->ep, buf, 1);
	}
	if (efp->selfdestruct) {
		if (efp->ws != NULL)
			elastic_unsubscribe(efp->ep, efp->ws);
		AZ(close(efp->fd));
		free(efp);
	}
	return (NULL);
}

static void
elastic_fd_txfunc(void *priv, const void *src, size_t len)
{
	struct elastic_fd *efp = priv;
	const char *p = src;
	char buf[1];

	if (!efp->ep->text) {
		(void)write(efp->fd, src, len);
		return;
	}
	while (len--) {
		buf[0] = *p++ & 0x7f;
		switch (buf[0]) {
		case 0x00:
		case 0x11:
		case 0x13:
			break;
		default:
			(void)write(efp->fd, buf, 1);
			break;
		}
	}
}

struct elastic_fd *
elastic_fd_start(struct elastic *ep, int fd, int mode, int selfdestruct)
{
	struct elastic_fd *efp;

	AN(ep);
	assert(fd > STDERR_FILENO);

	if (mode == -1)
		mode = ep->mode;
	else
		assert(ep->mode == O_RDWR || ep->mode == mode);

	efp = calloc(1, sizeof *efp);
	AN(efp);
	efp->fd = fd;
	efp->ep = ep;
	efp->selfdestruct = selfdestruct;
	if (mode != O_RDONLY)
		efp->ws = elastic_subscribe(ep, elastic_fd_txfunc, efp);
	if (mode != O_WRONLY) {
		efp->has_thread = 1;
		AZ(pthread_create(&efp->rxt, NULL, elastic_fd_rxthread, efp));
		if (selfdestruct)
			AZ(pthread_detach(efp->rxt));
	}
	return(efp);
}

void
elastic_fd_stop(struct elastic_fd **efpp)
{
	struct elastic_fd *efp;
	void *p;

	AN(efpp);
	efp = *efpp;
	*efpp = NULL;
	AZ(efp->selfdestruct);
	AZ(close(efp->fd));
	if (efp->ws != NULL)
		elastic_unsubscribe(efp->ep, efp->ws);
	if (efp->has_thread)
		AZ(pthread_join(efp->rxt, &p));
	free(efp);
}

void v_matchproto_(cli_func_f)
cli_elastic_serial(struct cli *cli)
{
	int fd, i;
	struct termios tt;
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<filename>", "Open serial port.");
		return;
	}

	fd = open(cli->av[1], O_RDWR | O_NONBLOCK);
	if (fd < 0 && errno == EPERM) {
		usleep(100000);
		fd = open(cli->av[1], O_RDWR | O_NONBLOCK);
	}
	if (fd < 0) {
		Cli_Error(cli, "Cannot open %s: %s\n",
		    cli->av[1], strerror(errno));
		return;
	}

	i = fcntl(fd, F_GETFL);
	if (i == -1) {
		Cli_Error(cli, "Cannot fcntl(F_GETFL) %s: %s\n",
		    cli->av[1], strerror(errno));
		(void)close(fd);
		return;
	}
	i = fcntl(fd, F_SETFL, i & ~O_NONBLOCK);
	if (i == -1) {
		Cli_Error(cli, "Cannot fcntl(F_SETFL) %s: %s\n",
		    cli->av[1], strerror(errno));
		(void)close(fd);
		return;
	}

	if (tcgetattr(fd, &tt)) {
		Cli_Error(cli, "Not a tty %s: %s\n",
		    cli->av[1], strerror(errno));
		AZ(close(fd));
		return;
	}
	cfmakeraw(&tt);
	tt.c_cflag |= CLOCAL;
	tt.c_cc[VMIN] = 1;
	tt.c_cc[VTIME] = 0;
	cli->ac -= 2;
	cli->av += 2;

	assert(tcsetattr(fd, TCSAFLUSH, &tt) == 0);
	(void)elastic_fd_start(ep, fd, -1, 1);
}

void v_matchproto_(cli_func_f)
cli_elastic_input(struct cli *cli)
{
	int fd;
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<filename>", "Read input from filename");
		return;
	}
	if (ep->mode == O_WRONLY) {
		Cli_Error(cli, "Only inputs can '%s'\n", *cli->av);
		return;
	}
	fd = open(cli->av[1], O_RDONLY);
	if (fd < 0) {
		Cli_Error(cli, "Cannot open '%s' for reading: %s\n",
		    cli->av[1], strerror(errno));
		return;
	}

	(void)elastic_fd_start(ep, fd, O_RDONLY, 1);
}

void v_matchproto_(cli_func_f)
cli_elastic_output(struct cli *cli)
{
	int fd;
	const char *what;
	struct elastic *ep = cli->elastic;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<filename>", "Send output to filename");
		return;
	}
	if (ep->mode == O_RDONLY) {
		Cli_Error(cli, "Only outputs can '%s'\n", *cli->av);
		return;
	}

	if (!strcmp(*cli->av, ">")) {
		fd = open(cli->av[1], O_WRONLY|O_CREAT|O_TRUNC, 0644);
		what = "writing";
	} else {
		fd = open(cli->av[1], O_WRONLY|O_CREAT|O_APPEND, 0644);
		what = "appending";
	}

	if (fd < 0) {
		Cli_Error(cli, "Cannot open '%s' for %s: %s\n",
		    cli->av[1], what, strerror(errno));
		return;
	}

	if (ep->out != NULL)
		elastic_fd_stop(&ep->out);
	ep->out = elastic_fd_start(ep, fd, O_WRONLY, 0);
}
