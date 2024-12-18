#include <pthread.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Chassis/r1000sc_priv.h"
#include "Infra/context.h"
#include "Diag/diagproc.h"

static pthread_t fido_thread;
static int fido_patience = 60;
static int fido_started = 0;
static int fido_dont_bite = 0;

static void *
fido(void *priv)
{
	struct ctx *cp;
	struct ctx ccp;
	void *ctx_iter_priv;
	const struct diagproc_context *dctx;
	uint64_t last_exec = 0, last_instr = 0, last_act = 0;
	uint64_t this_exec, this_instr, this_act;
	struct timespec t0, t1;
	double d, dl, e, el, dt;
	char *p;

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
		ctx_iter_priv = NULL;
		while(1) {
			cp = CTX_Iter(&ctx_iter_priv);
			if (cp == NULL)
				break;
			this_act += cp->activations;
			if (strstr(cp->ident, "PROC") == NULL)
				continue;
			ccp = *cp;
			p = strchr(ccp.ident, ' ');
			if (p != NULL)
				*p = '\0';

			dctx = (const void*)(cp+1);
			if (!fido_dont_bite) {
				printf("FIDO barks: %s act %ju mcs51 %ju exp %ju\n",
				    ccp.ident,
				    (uintmax_t)cp->activations,
				    (uintmax_t)dctx->instructions,
				    (uintmax_t)dctx->executions
				);
			}
			this_exec += dctx->executions;
			this_instr += dctx->instructions;
		}

		if (el > 0) {
			d = 1e-9 * (t1.tv_nsec - sc_t0.tv_nsec);
			d += (t1.tv_sec - sc_t0.tv_sec);
			printf("FIDO: r %.1f s %.3f ds %.3f / %.2f",
			    d, e, e - el, d / e);
			if (e - el > 0)
				printf("  d/' %.1f", (d - dl) / (e - el));
			else
				printf("  d/' %.1f", 0.0 );
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
