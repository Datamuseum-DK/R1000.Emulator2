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

#include <fcntl.h>
#include <inttypes.h>
#include <pthread.h>
#include <regex.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/time.h>

#include "Infra/r1000.h"
#include "Infra/vqueue.h"

#include "Chassis/r1000_arch.h"

struct component {
	VTAILQ_ENTRY(component)	list;
	char			*name;
	uint32_t		*flags;
};

static pthread_t sc_runner;
static pthread_mutex_t sc_mtx;
static pthread_cond_t sc_cond;
static double sc_quota = 0;
static int sc_quota_exit = 0;
int sc_started;
struct timespec sc_t0;

double
sc_main_get_quota(void)
{
	double retval;
	int fin;

	AZ(pthread_mutex_lock(&sc_mtx));
	if (sc_started == 1) {
		AZ(pthread_cond_signal(&sc_cond));
		sc_started = 2;
	}
	retval = sc_quota;
	while (retval <= 0 && (sc_started < 4 || !sc_quota_exit)) {
		AZ(pthread_cond_wait(&sc_cond, &sc_mtx));
		retval = sc_quota;
	}
	sc_quota -= retval;
	fin = sc_quota_exit && retval == 0;
	AZ(pthread_mutex_unlock(&sc_mtx));
	if (fin) {
		fprintf(stderr, "QQQ sc_started %d retval %g %a\n", sc_started, retval, retval);
		finish(1, "SystemC quota exhausted");
	}
	assert(retval > 0);
	return (retval);
}

static void v_matchproto_(cli_func_f)
cli_sc_launch(struct cli *cli)
{

	if (cli->help) {
		Cli_Usage(cli, "",
		    "Launch SystemC models of boards.");
		return;
	}

	systemc_clock = 1;

	AZ(pthread_mutex_init(&sc_mtx, NULL));
	AZ(pthread_cond_init(&sc_cond, NULL));

	sc_started = 1;

	AZ(pthread_create(&sc_runner, NULL, sc_main_thread, NULL));

	AZ(pthread_mutex_lock(&sc_mtx));
	while (sc_started < 2)
		AZ(pthread_cond_wait(&sc_cond, &sc_mtx));

	AZ(clock_gettime(CLOCK_MONOTONIC, &sc_t0));
	systemc_t_zero = simclock;
	sc_started = 3;
	AZ(pthread_mutex_unlock(&sc_mtx));
}

static void v_matchproto_(cli_func_f)
cli_sc_quota_add(struct cli *cli)
{
	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<seconds>", "Add time to SystemC quota.");
		return;
	}
	AZ(pthread_mutex_lock(&sc_mtx));
	sc_quota += strtod(cli->av[1], NULL);
	sc_started = 4;
	Cli_Printf(cli, "SC_QUOTA = %.9f\n", sc_quota);
	AZ(pthread_cond_signal(&sc_cond));
	AZ(pthread_mutex_unlock(&sc_mtx));
}

static void v_matchproto_(cli_func_f)
cli_sc_quota_wait(struct cli *cli)
{
	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL, "Wait for SystemC quota to expire.");
		return;
	}
	AZ(pthread_mutex_lock(&sc_mtx));
	while (sc_quota > 0) {
		AZ(pthread_mutex_unlock(&sc_mtx));
		usleep(100000);
		AZ(pthread_mutex_lock(&sc_mtx));
	}
	AZ(pthread_mutex_unlock(&sc_mtx));
}

static void v_matchproto_(cli_func_f)
cli_sc_quota_exit(struct cli *cli)
{
	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL,
		    "Exit emulator when SystemC quota expires.");
		return;
	}
	AZ(pthread_mutex_lock(&sc_mtx));
	sc_quota_exit = 1;
	AZ(pthread_mutex_unlock(&sc_mtx));
}

static const struct cli_cmds cli_sc_quota_cmds[] = {
	{ "add",		cli_sc_quota_add },
	{ "exit",		cli_sc_quota_exit },
	{ "wait",		cli_sc_quota_wait },
	{ NULL,			NULL },
};

static void v_matchproto_(cli_func_f)
cli_sc_quota(struct cli *cli)
{
	Cli_Dispatch(cli, cli_sc_quota_cmds);
}

static void v_matchproto_(cli_func_f)
cli_sc_wait(struct cli *cli)
{
	double e;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "[<seconds>]",
		    "Wait until SystemC time reaches seconds.");
		return;
	}

	e = strtod(cli->av[1], NULL);
	do
		usleep(10000);
	while (e > sc_when());
}

static void v_matchproto_(cli_func_f)
cli_sc_rate(struct cli *cli)
{
	struct timespec t1;
	double d, e;

	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL,
		    "Report SystemC simulation rates.");
		return;
	}

	AZ(clock_gettime(CLOCK_MONOTONIC, &t1));
	e = sc_when();
	d = 1e-9 * (t1.tv_nsec - sc_t0.tv_nsec);
	d += (t1.tv_sec - sc_t0.tv_sec);
	Cli_Printf(cli, "SC real time: %.3f\tsim time: %.3f\tratio: %.3f\n", d, e, d / e);
}

int sc_forced_reset;

static void v_matchproto_(cli_func_f)
cli_sc_force_reset(struct cli *cli)
{
	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL,
		    "Force reset signal high for IOC without IOP\n");
		return;
	}
	sc_forced_reset = 1;
}

static const struct cli_cmds cli_r1000_cmds[] = {
	{ "launch",		cli_sc_launch },
	{ "quota",		cli_sc_quota },
	{ "rate",		cli_sc_rate },
	{ "wait",		cli_sc_wait },
	{ "watchdog",		cli_sc_watchdog },
	{ "force_reset",	cli_sc_force_reset },
	{ NULL,			NULL },
};

void v_matchproto_(cli_func_f)
cli_r1000(struct cli *cli)
{
	Cli_Dispatch(cli, cli_r1000_cmds);
}

static uint64_t ucycle;

double
sc_now(void)
{
	return (ucycle * 200);
}

void *
sc_main_thread(void *priv)
{
	struct r1000_arch_state *state = r1000_arch_new();

	(void)priv;
	(void)sc_main_get_quota();
	while(1) {
		r1000_arch_micro_cycle(state);
		ucycle += 1;
	}
	return(0);
}

double
sc_when(void)
{
	return (ucycle * 200e-9);
}

static pthread_t fido_thread;
static int fido_patience = 60;
static int fido_started = 0;
static int fido_dont_bite = 0;

static void *
fido(void *priv)
{
	uint64_t last_exec = 0, last_instr = 0, last_act = 0;
	uint64_t this_exec, this_instr, this_act;
	struct timespec t0, t1;
	double d, dl, e, el, dt;

	(void)priv;
	sleep(fido_patience);
	dl = el = 0;
	AZ(clock_gettime(CLOCK_MONOTONIC, &t1));
	while (1) {
		t0 = t1;
		sleep(fido_patience);
		AZ(clock_gettime(CLOCK_MONOTONIC, &t1));
		e = sc_when();
		dt = 1e-9 * (t1.tv_nsec - t0.tv_nsec);
		dt += (t1.tv_sec - t0.tv_sec);

		this_exec = this_instr = this_act = 0;

		if (el > 0) {
			d = 1e-9 * (t1.tv_nsec - sc_t0.tv_nsec);
			d += (t1.tv_sec - sc_t0.tv_sec);
			printf("FIDO: r %.1f s %.3f ds %.4f / %.3f",
			    d, e, e - el, d / e);
			if (e - el > 0)
				printf("  d/ %.3f", (d - dl) / (e - el));
			else
				printf("  d/' %.3f", 0.0 );
			printf(" Mda %.1f",
			    (1e-6 * (this_act - last_act)) / dt);
			printf(" kdm %.1f",
			    (1e-3 * (this_instr - last_instr)) / dt);
			printf("\n");
		}
		el = e;
		dl = d;

		if (fido_dont_bite ||
		    (this_exec > last_exec && this_instr > last_instr)) {
			last_act = this_act;
			last_exec = this_exec;
			last_instr = this_instr;
		} else if (last_instr == 0) {
			finish(9, "SC Watchdog have seen no mcs51 activity");
		} else if (last_exec == 0) {
			finish(9, "SC Watchdog have seen no exp activity");
		} else if (this_instr == last_instr) {
			finish(8, "SC Watchdog sees DIPROC mcs51 stalled");
		} else {
			assert (this_exec == last_exec);
			finish(8, "SC Watchdog sees DIPROC exp stalled");
		}
	}
}

void v_matchproto_(cli_func_f)
cli_sc_watchdog(struct cli *cli)
{
	int patience;

	if (cli->help || cli->ac < 2 || cli->ac > 3) {
		Cli_Usage(cli, "[-dont_bite] <seconds>",
		    "Tickle watchdog periodically.");
		return;
	}

	if (!strcmp(cli->av[1], "-dont_bite")) {
		fido_dont_bite = 1;
		if (cli->ac == 2)
			patience = 60;
		else
			patience = strtoul(cli->av[2], NULL, 0);
	} else {
		patience = strtoul(cli->av[1], NULL, 0);
	}
	if (patience < 1) {
		Cli_Error(cli, "Too short patience for fido: %d\n", patience);
		return;
	}
	fido_patience = patience;
	if (!fido_started) {
		AZ(pthread_create(&fido_thread, NULL, fido, NULL));
		fido_started = 1;
	}
}
