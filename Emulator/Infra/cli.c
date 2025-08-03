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
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Infra/vav.h"
#include "Infra/vsb.h"
#include "Iop/iop.h"

static int cli_echo_cmds = 1;

static void
cli_exit(struct cli *cli)
{
	uint16_t w = 0;

	if (cli->help || cli->ac > 2) {
		Cli_Usage(cli, "[<exit status>]", "Exit emulator.");
		return;
	}
	cli->ac--;
	cli->av++;
	if (cli->ac == 1)
		w = atoi(cli->av[0]);
	finish(w, "CLI asked for it");
}

/**********************************************************************/

static void
cli_include(struct cli *cli)
{
	FILE *fi;
	const char *fn;
	int old_echo = cli_echo_cmds;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "[+|-]<filename>", "Include CLI commands from filename.");
		return;
	}

	fn = cli->av[1];
	if (cli->av[1][0] == '-') {
		cli_echo_cmds = 0;
		fn++;
	} else if (cli->av[1][0] == '+') {
		cli_echo_cmds = 1;
		fn++;
	}
	fi = fopen(fn, "r");
	if (fi == NULL) {
		Cli_Error(cli, "Cannot open '%s' for reading: %s\n",
		    fn, strerror(errno));
		return;
	}
	if (Cli_From_File(fi, 1))
		Cli_Error(cli, "");
	AZ(fclose(fi));
	if (cli->av[1][0] == '-' || cli->av[1][0] == '+')
		cli_echo_cmds = old_echo;
}

/**********************************************************************/

static void
cli_echo(struct cli *cli)
{

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "+|-", "Control echo of CLI commands to stdout.");
		return;
	}

	if (!strcmp(cli->av[1], "+"))
		cli_echo_cmds = 1;
	else if (!strcmp(cli->av[1], "-"))
		cli_echo_cmds = 0;
	else
		Cli_Error(cli, "Did not understand '%s', use '+' or '-'\n", cli->av[1]);
}

/**********************************************************************/

void
Cli_Printf(struct cli *cli, const char *fmt, ...)
{
	va_list ap;

	(void)cli;

	va_start(ap, fmt);
	(void)vprintf(fmt, ap);
	va_end(ap);
}

void
Cli_Error(struct cli *cli, const char *fmt, ...)
{
	va_list ap;

	cli->status = 1;

	va_start(ap, fmt);
	(void)vprintf(fmt, ap);
	va_end(ap);
}

void
Cli_Unknown(struct cli *cli)
{

	Cli_Printf(cli, "Unknown argument '%s'\n", cli->av[0]);
	cli->status = 1;
}

static cli_func_f cli_help;

static const struct cli_cmds cli_cmds[] = {
	{ "?",			cli_help },
	{ "console",		cli_ioc_console },
	{ "dfs",		Cli_dfs },
	{ "diagbus",		cli_diagbus },
	{ "diproc",		cli_diproc },
	{ "disk",		cli_scsi_disk },
	{ "echo",		cli_echo },
	{ "firmware",		cli_firmware },
	{ "exit",		cli_exit },
	{ "help",		cli_help },
	{ "include",		cli_include },
	{ "iop",		cli_ioc },
	{ "modem",		cli_ioc_modem },
	{ "r1000",		cli_r1000 },
	{ "tape",		cli_scsi_tape },
	{ "trace",		cli_trace },
	{ NULL,			NULL },
};

void
Cli_Usage(struct cli *cli, const char *args, const char *fmt, ...)
{
	va_list ap;

	if (cli->help && cli->ac == 0) {
		Cli_Printf(cli, "\t%s", VSB_data(cli->path));
		if (args != NULL)
			Cli_Printf(cli, " %s\n", args);
		else
			Cli_Printf(cli, "\n");
	} else {
		Cli_Printf(cli, "Usage:\t");
		Cli_Printf(cli, "%s", VSB_data(cli->path));
		if (args != NULL)
			Cli_Printf(cli, " %s", args);
		Cli_Printf(cli, "\n\t");
		va_start(ap, fmt);
		(void)vprintf(fmt, ap);
		va_end(ap);
		Cli_Printf(cli, "\n");
	}
}

static void
cli_call_func(struct cli *cli, const struct cli_cmds *cc)
{
	struct vsb *old_path = cli->path;

	AN(cc);
	AN(cc->cmd);
	AN(cc->func);
	cli->cmd = cc->cmd;
	cli->path = VSB_new_auto();
	AN(cli->path);
	if (VSB_len(old_path)) {
		VSB_cat(cli->path, VSB_data(old_path));
		VSB_cat(cli->path, " ");
	}
	VSB_cat(cli->path, cc->cmd);
	AZ(VSB_finish(cli->path));
	cc->func(cli);
	VSB_destroy(&cli->path);
	cli->path = old_path;
}

static void
cli_int_dispatch(struct cli *cli, const struct cli_cmds *cmds)
{
	const struct cli_cmds *cc;

	for (cc = cmds; cc->cmd != NULL; cc++)
		if (!strcasecmp(cc->cmd, *cli->av))
			break;

	if (cc->func != NULL) {
		cli_call_func(cli, cc);
		return;
	}

	Cli_Error(cli, "CLI error, no command: ");
	Cli_Printf(cli, "[%s] ", VSB_data(cli->path));
	Cli_Printf(cli, "%s\n", *cli->av);
}

static void v_matchproto_(cli_func_f)
cli_help(struct cli *cli)
{

	if (cli->help) {
		Cli_Usage(cli, " [cmds…]", "Print brief usage.");
		return;
	}

	cli->help = 1;
	VSB_clear(cli->path);
	AZ(VSB_finish(cli->path));
	Cli_Dispatch(cli, cli_cmds);
}

void
Cli_Dispatch(struct cli *cli, const struct cli_cmds *cmds)
{
	const struct cli_cmds *cc;

	if (cli->help == 1 && cli->ac == 0) {
		for (cc = cmds; cc->cmd != NULL; cc++)
			cli_call_func(cli, cc);
	} else if (cli->help == 1 && cli->ac < 2) {
		cli->ac--;
		cli->av++;
		for (cc = cmds; cc->cmd != NULL; cc++)
			cli_call_func(cli, cc);
		cli->av--;
		cli->ac++;
	} else if (cli->help == 0 && cli->ac < 2) {
		cli->help = 1;
		Cli_Error(cli, "Usage:\n");
		for (cc = cmds; cc->cmd != NULL; cc++)
			cli_call_func(cli, cc);
	} else if (cli->ac >= 1) {
		cli->ac--;
		cli->av++;
		cli_int_dispatch(cli, cmds);
		cli->ac++;
		cli->av--;
	}
}

int
Cli_Exec(const char *s)
{
	int ac, i;
	char **av;
	struct cli cli;

	av = VAV_Parse(s, &ac, ARGV_COMMENT);
	AN(av);
	if (av[0] != NULL) {
		printf("CLI error: %s\n", av[0]);
		VAV_Free(av);
		return (1);
	}
	if (av[1] == NULL) {
		VAV_Free(av);
		return (0);
	}
	if (cli_echo_cmds) {
		printf("CLI «");
		for (i = 1; i < ac; i++) {
			if (strchr(av[i], ' ') != NULL)
				printf(" \"%s\"", av[i]);
			else
				printf(" %s", av[i]);
		}
		printf(" »\n");
	}
	memset(&cli, 0, sizeof cli);
	cli.ac = ac - 1;
	cli.av = av + 1;
	cli.path = VSB_new_auto();
	AN(cli.path);
	AZ(VSB_finish(cli.path));
	cli_int_dispatch(&cli, cli_cmds);
	VSB_destroy(&cli.path);
	VAV_Free(av);
	return (cli.status);
}

int
Cli_From_File(FILE *fi, int fatal)
{
	char buf[BUFSIZ];
	char *p;
	int rv = 0;

	while (1) {
		if (fgets(buf, sizeof buf, fi) != buf)
			break;
		p = strchr(buf, '\n');
		if (p != NULL)
			*p = '\0';
		rv = Cli_Exec(buf);
		if (rv < 0 || (rv && fatal))
			break;
	}
	return (rv);
}
