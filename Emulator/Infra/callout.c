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

#include <stdlib.h>
#include <pthread.h>

#include "Infra/r1000.h"

struct callout {
	VTAILQ_ENTRY(callout)		next;
	nanosec				when;
	nanosec				repeat;
	const struct callout_how	*how;
	void				*priv;
};

struct sleeps {
	VTAILQ_ENTRY(sleeps)		next;
	pthread_cond_t			cond;
};

typedef void callout_func_f(const struct callout *);

struct callout_how {
	callout_func_f			*func;
};

static pthread_mutex_t callout_mtx = PTHREAD_MUTEX_INITIALIZER;

static VTAILQ_HEAD(,callout) callouts = VTAILQ_HEAD_INITIALIZER(callouts);
static VTAILQ_HEAD(,sleeps) idle_sleeps = VTAILQ_HEAD_INITIALIZER(idle_sleeps);

static void
callout_insert_locked(struct callout *co)
{
	struct callout *co2;

	AN(co);
	AN(co->how);

	VTAILQ_FOREACH(co2, &callouts, next)
		if (co2->when > co->when)
			break;
	if (co2 == NULL)
		VTAILQ_INSERT_TAIL(&callouts, co, next);
	else
		VTAILQ_INSERT_BEFORE(co2, co, next);
}

static void
callout_insert(struct callout *co)
{
	AN(co);
	AN(co->how);

	AZ(pthread_mutex_lock(&callout_mtx));
	callout_insert_locked(co);
	AZ(pthread_mutex_unlock(&callout_mtx));
}

/**********************************************************************/

struct priv_sig_cond {
	pthread_mutex_t		*mtx;
	pthread_cond_t		*cond;
};

static void
callout_func_signal_cond(const struct callout *co)
{
	struct priv_sig_cond *psc;

	psc = co->priv;
	AZ(pthread_mutex_lock(psc->mtx));
	AZ(pthread_cond_signal(psc->cond));
	AZ(pthread_mutex_unlock(psc->mtx));
}

static const struct callout_how callout_signal_cond_how = {
	// .name = "Signal Condvar",
	.func = callout_func_signal_cond,
};

void
callout_signal_cond(pthread_cond_t *cond,
    pthread_mutex_t *mtx, nanosec when, nanosec repeat)
{
	struct callout *co;
	struct priv_sig_cond *psc;
	char *p;

	p = calloc(sizeof *co + sizeof *psc, 1);
	AN(p);
	co = (void*)p;
	psc = (void*)(p + sizeof *co);
	psc->cond = cond;
	psc->mtx = mtx;
	co->when = simclock + when;
	co->repeat = repeat;
	co->priv = psc;
	co->how = &callout_signal_cond_how;
	callout_insert(co);
}

/**********************************************************************/

struct priv_sig_callback {
	callout_callback_f	*func;
	void			*priv;
};

static void
callout_func_callback(const struct callout *co)
{
	struct priv_sig_callback *psc;

	psc = co->priv;
	psc->func(psc->priv);
}

static const struct callout_how callout_callback_how = {
	// .name = "Callback",
	.func = callout_func_callback,
};

void
callout_callback(callout_callback_f *func,
    void *priv, nanosec when, nanosec repeat)
{
	struct callout *co;
	struct priv_sig_callback *psc;

	co = calloc(sizeof *co + sizeof *psc, 1);
	AN(co);
	psc = (void*)(co + 1);
	psc->func = func;
	psc->priv = priv;
	co->when = simclock + when;
	co->repeat = repeat;
	co->priv = psc;
	co->how = &callout_callback_how;
	callout_insert(co);
}

/**********************************************************************/

static void
callout_func_sleep(const struct callout *co)
{
	struct sleeps *slp;

	slp = co->priv;
	AZ(pthread_cond_signal(&slp->cond));
}

static const struct callout_how callout_sleep_how = {
	// .name = "Signal Condvar",
	.func = callout_func_sleep,
};

void
callout_sleep(nanosec duration)
{
	struct sleeps *slp;
	struct callout *co;

	co = calloc(sizeof *co, 1);
	AN(co);

	AZ(pthread_mutex_lock(&callout_mtx));
	slp = VTAILQ_FIRST(&idle_sleeps);
	if (slp != NULL) {
		VTAILQ_REMOVE(&idle_sleeps, slp, next);
	} else {
		AZ(pthread_mutex_unlock(&callout_mtx));
		slp = calloc(sizeof *slp, 1);
		AN(slp);
		AZ(pthread_cond_init(&slp->cond, NULL));
		AZ(pthread_mutex_lock(&callout_mtx));
	}
	co->when = simclock + duration;
	co->how = &callout_sleep_how;
	co->priv = slp;
	callout_insert_locked(co);
	AZ(pthread_cond_wait(&slp->cond, &callout_mtx));
	VTAILQ_INSERT_HEAD(&idle_sleeps, slp, next);
	AZ(pthread_mutex_unlock(&callout_mtx));
}

/**********************************************************************/

nanosec
callout_poll(void)
{
	struct callout *co;
	nanosec rv = 0;

	while (1) {
		rv = 0;
		AZ(pthread_mutex_lock(&callout_mtx));
		co = VTAILQ_FIRST(&callouts);
		if (co != NULL && co->when < simclock) {
			VTAILQ_REMOVE(&callouts, co, next);
		} else {
			if (co != NULL)
				rv = co->when;
			co = NULL;
		}
		AZ(pthread_mutex_unlock(&callout_mtx));
		if (co == NULL)
			return (rv);
		co->how->func(co);
		if (co->repeat > 0) {
			co->when += co->repeat;
			callout_insert(co);
		} else {
			free(co);
		}
	}
}
