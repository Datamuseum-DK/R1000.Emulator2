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

#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Infra/vsb.h"
#include "Chassis/r1000_arch.h"

int optreset;		// Some have it, some not.

volatile nanosec simclock;
volatile nanosec systemc_t_zero;
volatile int systemc_clock;

const char *tracepath;

static struct timespec t0;

void
hexdump(struct vsb *vsb, const void *ptr, size_t len, unsigned offset)
{
	const uint8_t *p = ptr;
	size_t c, u, v;

	AN(ptr);
	for (u = 0; u < len; u += 0x20) {
		VSB_printf(vsb, "%08zx", u + offset);
		for (v = 0; v < 0x20 && v + u < len; v++)
			VSB_printf(vsb, " %02x", p[u + v]);
		for (; v < 0x20 && v + u < len; v++)
			VSB_cat(vsb, "   ");
		VSB_cat(vsb, " |");
		for (v = 0; v < 0x20 && v + u < len; v++) {
			c = p[u+v];
			if (c < 0x20 || c > 0x7e)
				c = '.';
			VSB_putc(vsb, c);
		}
		VSB_putc(vsb, '|');
		VSB_putc(vsb, '\n');
	}
}

void
finish(int status, const char *why)
{
	struct rusage rus;
	struct timespec tx;
	double ds, dr, dt;

	printf("Begin statistics\n");

	AZ(clock_gettime(CLOCK_MONOTONIC, &tx));
	dr = 1e-9 * tx.tv_nsec;
	dr -= 1e-9 * t0.tv_nsec;
	dr += tx.tv_sec - t0.tv_sec;
	printf("  %12.6f s\tWall Clock Time\n", dr);

	dt = ucycle * 200e-9;
	printf("  %15.9f s\tSystemC simulation\n", dt);
	if (dt > 0 && dr > dt)
		printf("  1/%.1f\t\tSystemC Simulation ratio\n", dr / dt);
	else if (dt > 0)
		printf("  %10.4f\t\tSystemC Simulation ratio\n", dt / dr);

	ds = simclock * 1e-9;
	printf("  %15.9f s\tIOC simulation\n", ds);

	dt = 1e-9 * ioc_t_stopped;
	printf("  %12.6f s\tIOC stopped\n", dt);
	printf("%7ju\t\t\tIOC instructions\n", ioc_nins);

	AZ(getrusage(RUSAGE_SELF, &rus));

	printf("  %5ld.%03ld s\t\tUser time\n",
	    rus.ru_utime.tv_sec, rus.ru_utime.tv_usec / 1000L);
	printf("  %5ld.%03ld s\t\tSystem time\n",
	    rus.ru_stime.tv_sec, rus.ru_stime.tv_usec / 1000L);
	printf("%7ld\t\t\tMax RSS\n", rus.ru_maxrss);

	printf("End statistics\n");

	printf("Terminating because: %s\n", why);

	printf("Exit status 0x%x\n", status);

	exit (status);
}

#define ARG_SPEC "T:U:"

int
main(int argc, char **argv)
{
	int ch, i;
	char buf[BUFSIZ];
	const char *p, *q;
	const char *argv0 = argv[0];

	AZ(clock_gettime(CLOCK_MONOTONIC, &t0));
	setbuf(stdout, NULL);
	setbuf(stderr, NULL);


	while ((ch = getopt(argc, argv, ARG_SPEC)) != -1) {
		switch (ch) {
		case 'T':
			tracepath = optarg;
			break;
		default:
			fprintf(stderr, "Usage...\n");
			exit(0);
		}
	}
	argc -= optind;
	argv += optind;

	if (tracepath == NULL) {
		p = getenv("TMPDIR");
		if (p == NULL)
			p = "/tmp";
		q = strrchr(argv0, '/');
		if (q == NULL)
			q = argv0;
		else
			q++;
		bprintf(buf, "%s/_%s", p, q);
		tracepath = strdup(buf);
	}
	AN(tracepath);

	bprintf(buf, "%s.trace", tracepath);
	trace_fd = open(buf, O_WRONLY|O_CREAT|O_TRUNC, 0644);
	if (trace_fd < 0) {
		fprintf(stderr, "Cannot open tracefile '%s': %s\n",
		    buf, strerror(errno));
		exit(2);
	}

	CTX_init(tracepath);
	diagbus_init();
	mem_init();
	ioc_init();


	for (i = 0; i < argc; i++) {
		if (Cli_Exec(argv[i]))
			exit(2);
	}

	printf("CLI stdin open\n");

	(void)Cli_From_File(stdin, 0);
	return (0);
}
