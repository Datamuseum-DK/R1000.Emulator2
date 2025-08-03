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

#ifndef R1000_ARCH
#define R1000_ARCH

void r1000_arch_new(void);
void r1000_arch_micro_cycle(void);

extern int sc_started;

void pit_clock(void);

extern uint16_t mp_refresh_count;
extern uint16_t mp_cur_uadr;
extern unsigned mp_fiu_freeze;
extern unsigned mp_fiu_unfreeze;
extern unsigned mp_ioc_trace;
extern unsigned mp_nua_bus;
extern unsigned mp_seq_prepped;
extern unsigned mp_seq_halted;

double sc_now(void);

void *sc_main_thread(void *priv);

double sc_main_get_quota(void);

double sc_when(void);

extern const char *tracepath;

extern int sc_forced_reset;
extern struct timespec sc_t0;

cli_func_f cli_sc_watchdog;

#endif /* R1000_ARCH */
