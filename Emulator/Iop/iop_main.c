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
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Musashi/m68k.h"
#include "Infra/vsb.h"
#include "Infra/vend.h"
#include "Iop/memspace.h"

#define IOC_CPU_TYPE	M68K_CPU_TYPE_68020

static pthread_t ioc_cpu;


volatile int iop_running;
static uintmax_t ioc_maxins = 0;
uintmax_t ioc_nins = 0;
uintmax_t ioc_t_stopped = 0;
static uintmax_t ioc_cpu_quota = 0;
static unsigned ioc_cpu_running = 0;
static pthread_cond_t ioc_cpu_cond_state = PTHREAD_COND_INITIALIZER;
static pthread_cond_t ioc_cpu_cond = PTHREAD_COND_INITIALIZER;
static pthread_cond_t ioc_cpu_sleep = PTHREAD_COND_INITIALIZER;
static pthread_mutex_t ioc_cpu_mtx = PTHREAD_MUTEX_INITIALIZER;

unsigned ioc_fc;

unsigned int ioc_pc;
static unsigned key_switch;

/**********************************************************************
 */

void
ioc_wake_cpu(void)
{
	AZ(pthread_cond_signal(&ioc_cpu_sleep));
}

/**********************************************************************
 */

void
ioc_stop_cpu(void)
{
	AZ(pthread_mutex_lock(&ioc_cpu_mtx));
	ioc_cpu_quota = 0;
	AZ(pthread_mutex_unlock(&ioc_cpu_mtx));
}

void
ioc_wait_cpu_running(void)
{
	AZ(pthread_mutex_lock(&ioc_cpu_mtx));
	while (!ioc_cpu_running)
		AZ(pthread_cond_wait(&ioc_cpu_cond_state, &ioc_cpu_mtx));
	AZ(pthread_mutex_unlock(&ioc_cpu_mtx));
}

static void
ioc_wait_cpu_stopped(void)
{
	AZ(pthread_mutex_lock(&ioc_cpu_mtx));
	while (ioc_cpu_quota || ioc_cpu_running)
		AZ(pthread_cond_wait(&ioc_cpu_cond_state, &ioc_cpu_mtx));
	AZ(pthread_mutex_unlock(&ioc_cpu_mtx));
}

static void
ioc_start_cpu(uintmax_t quota)
{
	if (!quota)
		quota = 1ULL << 60;

	AZ(pthread_mutex_lock(&ioc_cpu_mtx));
	AZ(ioc_cpu_running);
	ioc_cpu_quota = quota;
	AZ(pthread_cond_broadcast(&ioc_cpu_cond));
	AZ(pthread_mutex_unlock(&ioc_cpu_mtx));
}

void v_matchproto_(cli_func_f)
cli_ioc_switch(struct cli *cli)
{
	if (cli->ac == 2 && !strcmp(cli->av[1], "-normal")) {
		key_switch = 0;
	} else if (cli->ac == 2 && !strcmp(cli->av[1], "-interactive")) {
		key_switch = 8;
	} else {
		Cli_Usage(cli, "-normal|-interactive", "Keyswitch");
	}
}

void v_matchproto_(cli_func_f)
cli_ioc_reset(struct cli *cli)
{
	if (cli->help || cli->ac > 2) {
		Cli_Usage(cli, "[-stop]", "Reset IOC CPU.");
		return;
	}
	if (cli->ac == 2 && !strcmp(cli->av[1], "-stop")) {
		Cli_Error(cli, "Unknown argument '%s'.\n", cli->av[1]);
	}
	ioc_stop_cpu();
	ioc_wait_cpu_stopped();

	/*
	 * The "BOOTTIME" signal on page ioc_03 inverts the MSB address bit
	 * for the first few clock-cycles to get the RESET vector and SP
	 * read from EEPROM instead of RAM.  We simulate this by copying the
	 * first 8 bytes from EEPROM to RAM.
	 */
	if (!vbe64dec(ioc_eeprom_space))
		ioc_load_eeproms();
	m68k_write_memory_32(0x0, m68k_read_memory_32(0x80000000));
	m68k_write_memory_32(0x4, m68k_read_memory_32(0x80000004));
	m68k_pulse_reset();
	if (cli->ac == 1)
		ioc_start_cpu(0);
}

void v_matchproto_(cli_func_f)
cli_ioc_state(struct cli *cli)
{
	struct vsb *vsb;

	vsb = VSB_new_auto();
	AN(vsb);
	AZ(pthread_mutex_lock(&ioc_cpu_mtx));
	if (ioc_cpu_running)
		VSB_printf(vsb, "IOC CPU is running\n");
	else
		VSB_printf(vsb, "IOC CPU is stopped\n");
	ioc_dump_cpu_regs(vsb);
	AZ(pthread_mutex_unlock(&ioc_cpu_mtx));
	AZ(VSB_finish(vsb));
	Cli_Printf(cli, "%s", VSB_data(vsb));
	VSB_destroy(&vsb);
}

void v_matchproto_(cli_func_f)
cli_ioc_step(struct cli *cli)
{
	uintmax_t uj = 1;

	if (cli->help || cli->ac > 2) {
		Cli_Usage(cli, "[count]", "Single step IOC CPU.");
		return;
	}
	cli->ac--;
	cli->av++;
	if (cli->ac == 1)
		uj = strtoumax(cli->av[0], NULL, 0);
	if (ioc_cpu_running) {
		Cli_Error(cli, "IOC CPU is running\n");
		return;
	}
	ioc_start_cpu(uj);
	ioc_wait_cpu_stopped();
	cli_ioc_state(cli);
}

void v_matchproto_(cli_func_f)
cli_ioc_stop(struct cli *cli)
{
	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL, "Stop IOC CPU.");
		return;
	}
	ioc_stop_cpu();
	ioc_wait_cpu_stopped();
	cli_ioc_state(cli);
}

void v_matchproto_(cli_func_f)
cli_ioc_start(struct cli *cli)
{
	if (cli->help || cli->ac != 1) {
		Cli_Usage(cli, NULL, "Start IOC CPU.");
		return;
	}
	ioc_start_cpu(0);
}

void v_matchproto_(cli_func_f)
cli_ioc_maxins(struct cli *cli)
{

	if (cli->help) {
		Cli_Usage(cli, "<count>",
		    "Terminate after count instructions.");
		return;
	}
	ioc_maxins = strtoumax(cli->av[0], NULL, 0);
}

/**********************************************************************/

void v_matchproto_(mem_pre_read)
io_sreg8_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{

	(void)debug;
	(void)width;
	(void)adr;

	// Margining off
	space[0] |= 0x80;
	space[2] &= ~0x02;

	// EXTID
	space[3] &= ~0x70;
	space[3] |= 0x20;

	// KEY SWITCH
	space[3] &= ~0x08;
	space[3] |= key_switch;
}

/**********************************************************************/

unsigned int
m68k_read_disassembler_16(unsigned int address)
{
	return m68k_debug_read_memory_16(address);
}

unsigned int
m68k_read_disassembler_32(unsigned int address)
{
	return m68k_debug_read_memory_32(address);
}


/* Disassembler */
static void
make_hex(char* buff, unsigned int pc, unsigned int length)
{
	char* ptr = buff;

	for(;length>0;length -= 2)
	{
		sprintf(ptr, "%04x", m68k_read_disassembler_16(pc));
		pc += 2;
		ptr += 4;
		if(length > 2)
			*ptr++ = ' ';
	}
}

static void
cpu_trace(unsigned int pc, uint8_t *peg)
{

	char buff[100];
	char buff2[100];
	unsigned int instr_size;
	static unsigned int last_pc = 0;
	static unsigned repeats = 0;

	AN(peg);
	if (*peg & PEG_NOTRACE)
		return;
	instr_size = m68k_disassemble(buff, pc, IOC_CPU_TYPE);
	make_hex(buff2, pc, instr_size);
	if (pc != last_pc) {
		if (repeats)
			Trace(trace_ioc_instructions, "E … × %x", repeats);
		repeats = 0;
		Trace(
		    trace_ioc_instructions,
		    "E %08x %04x %08x: %02x %-20s: %s",
		    pc,
		    m68k_get_reg(NULL, M68K_REG_SR),
		    m68k_get_reg(NULL, M68K_REG_A7),
		    *peg,
		    buff2,
		    buff
		);
		last_pc = pc;
	} else {
		repeats++;
	}
}

void
cpu_instr_callback(unsigned int pc)
{
	uint8_t *peg;

	do {
		pc = m68k_get_reg(NULL, M68K_REG_PC);
		if (pc == 0) {
			finish(4, "IOP PC==0");
		}
		peg = mem_find_peg(pc);
		if (peg == NULL) {
			fprintf(stderr, "No PEG at address 0x%08x\n", pc);
			AN(peg);
		}
		if (*peg & PEG_BREAKPOINT)
			ioc_breakpoint_check(pc);
	} while (pc != m68k_get_reg(NULL, M68K_REG_PC));

	ioc_pc = pc;

	if (trace_ioc_instructions)
		cpu_trace(pc, peg);
}

/* The main loop */
void *
main_ioc(void *priv)
{
	unsigned last_irq_level = 0;
	int i;
	unsigned u;
	nanosec ns;
	struct timespec ts;

	(void)priv;

	io_sreg8_space[3] = 0x7;

	AZ(pthread_mutex_lock(&ioc_cpu_mtx));
	while(1)
	{
		while (!ioc_cpu_quota) {
			if (ioc_cpu_running)
				AZ(pthread_cond_broadcast(&ioc_cpu_cond_state));
			ioc_cpu_running = 0;
			AZ(pthread_cond_wait(&ioc_cpu_cond, &ioc_cpu_mtx));
		}
		u = ioc_cpu_running;
		ioc_cpu_running = 1;
		if (!u)
			AZ(pthread_cond_broadcast(&ioc_cpu_cond_state));
		AZ(pthread_mutex_unlock(&ioc_cpu_mtx));

		if (irq_level != last_irq_level) {
			last_irq_level = irq_level;
			m68k_set_irq(last_irq_level);
			Trace(trace_ioc_interrupt,
			    "IRQ level 0x%x", last_irq_level);
			io_sreg8_space[3] &= ~7;
			io_sreg8_space[3] |= (~irq_level) & 7;
		}
		i = m68k_execute(1);
		simclock += 100ULL * i;

		if (i == 1) {
			ioc_t_stopped += 100ULL;
			iop_running = 0;
		} else {
			ioc_nins++;
			iop_running = 1;
		}

		if (ioc_maxins && ioc_nins > ioc_maxins)
			finish(4, "IOP maxins reached");
		ns = callout_poll();
		if (i == 1) {
			if (ns > 0) {
				ns -= simclock;
			} else {
				ns = 1000000;
			}
			AZ(clock_gettime(CLOCK_REALTIME, &ts));
			ts.tv_nsec += ns;
			while (ts.tv_nsec >= 1000000000) {
				ts.tv_nsec -= 1000000000;
				ts.tv_sec += 1;
			}
		} else {
			ns = 0;
		}
		AZ(pthread_mutex_lock(&ioc_cpu_mtx));
		if (ns > 0) {
			(void)pthread_cond_timedwait(&ioc_cpu_sleep, &ioc_cpu_mtx, &ts);
			// XXX: Correctly account for actual time slept
			simclock += ns;
			ioc_t_stopped += ns;
		}
		if (ioc_cpu_quota)
			ioc_cpu_quota--;
	}
}

void
ioc_init(void)
{

	m68k_init();
	m68k_set_cpu_type(IOC_CPU_TYPE);

	ioc_bus_xact_init();

	ioc_debug_init();

	ioc_console_init();
	ioc_duart_init();
	ioc_scsi_d_init();
	ioc_scsi_t_init();
	ioc_rtc_init();
	ioc_vme_init();

	AZ(pthread_create(&ioc_cpu, NULL, main_ioc, NULL));
}
