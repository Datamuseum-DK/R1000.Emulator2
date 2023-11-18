/*
 * RTC - MM58167B Microprocesor Real Time Clock
 * --------------------------------------------
 *
 * Chip Select: 0xffff8xxx
 *
 */

#include <pthread.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Iop/memspace.h"

static pthread_mutex_t rtc_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t rtc_cond = PTHREAD_COND_INITIALIZER;
static pthread_t rtc_thr;

static const uint8_t last_day_of_month[256] = {
	[0x01] = 0x31,
	[0x02] = 0x28,
	[0x03] = 0x31,
	[0x04] = 0x30,
	[0x05] = 0x31,
	[0x06] = 0x30,
	[0x07] = 0x31,
	[0x08] = 0x31,
	[0x09] = 0x30,
	[0x10] = 0x31,
	[0x11] = 0x30,
	[0x12] = 0x31
};

static uint8_t rtcregs[32] = {
	0x00,	// Counter - Milliseconds
	0x00,	// Counter - Hundredths and Tenths of Seconds
	0x00,	// Counter - Seconds
	0x00,	// Counter - Minutes

	0x00,	// Counter - Hours
	0x00,	// Counter - Day of Week
	0x00,	// Counter - Day of Month
	0x00,	// Counter - Month

	0x00,	// NVRAM - Milliseconds
	98,	// NVRAM - (Year - 1)
	0x00,	// NVRAM - Seconds
	0x00,	// NVRAM - Minutes

	0x00,	// NVRAM - Hours
	0x00,	// NVRAM - Day of Week
	0x00,	// NVRAM - Day of Month
	0x00,	// NVRAM - Month

	0x00,	// Interrupt Status Register
	0x00,	// Interrupt Control Register
	0x00,	// Counters Reset
	0x00,	// RAM Reset

	0x00,	// Status Bit
	0x00,	// GO Command
	0x00,	// STANDBY INTERRUPT~
	0x00,	// Undefined

	0x00,	// Undefined
	0x00,	// Undefined
	0x00,	// Undefined
	0x00,	// Undefined

	0x00,	// Undefined
	0x00,	// Undefined
	0x00,	// Undefined
	0x00,	// Test Mode
};

static void
ioc_rtc_setclock(void)
{
	struct timeval tv;
	struct tm *tm;

	AZ(gettimeofday(&tv, NULL));
	rtcregs[0] = ((tv.tv_usec / 1000) % 10) * 16;
	rtcregs[1] = (tv.tv_usec / 10000) % 10;
	rtcregs[1] |= ((tv.tv_usec / 100000) % 10) * 16;
	tm = gmtime(&tv.tv_sec);

	rtcregs[2] = (tm->tm_sec % 10);
	rtcregs[2] |= (tm->tm_sec / 10) * 16;
	rtcregs[3] = (tm->tm_min % 10);
	rtcregs[3] |= (tm->tm_min / 10) * 16;
	rtcregs[4] = (tm->tm_hour % 10);
	rtcregs[4] |= (tm->tm_hour / 10) * 16;
	rtcregs[5] = tm->tm_wday + 1;
	rtcregs[6] = ((tm->tm_mday) % 10);
	rtcregs[6] |= ((tm->tm_mday) / 10) * 16;
	rtcregs[7] = ((tm->tm_mon+1) % 10);
	rtcregs[7] |= ((tm->tm_mon+1) / 10) * 16;
}

static unsigned
ioc_rtc_bcd_increment(int idx)
{
	rtcregs[idx] += 1;
	if ((rtcregs[idx] & 0xf) > 9)
		rtcregs[idx] += 6;
	return (rtcregs[idx]);
}

static void *
ioc_rtc_thread(void *priv)
{

	(void)priv;
	AZ(pthread_mutex_lock(&rtc_mtx));
	callout_signal_cond(&rtc_cond, &rtc_mtx, 1000000, 1000000);
	while (1) {
		AZ(pthread_cond_wait(&rtc_cond, &rtc_mtx));
		Trace(trace_ioc_io, "RTC tick");

		rtcregs[0x0e] |= 0x01;

		// Increment BCD 1/1000ths of seconds
		rtcregs[0] += 0x10;
		if (rtcregs[0] <= 0x90)
			continue;
		rtcregs[0] = 0x00;

		// Increment BCD 1/100ths of seconds
		if (ioc_rtc_bcd_increment(1) <= 0x99)
			continue;
		rtcregs[1] = 0x00;

		// Increment BCD Seconds
		if (ioc_rtc_bcd_increment(2) <= 0x59)
			continue;
		rtcregs[2] = 0x00;

		// Increment BCD Minutes
		if (ioc_rtc_bcd_increment(3) <= 0x59)
			continue;
		rtcregs[3] = 0x00;

		// Increment BCD Hours
		if (ioc_rtc_bcd_increment(4) <= 0x23)
			continue;
		rtcregs[4] = 0x00;

		// Increment Wday
		if (ioc_rtc_bcd_increment(5) == 8)
			rtcregs[5] = 0x01;

		// Increment BCD Mday
		(void)ioc_rtc_bcd_increment(6);
		assert(last_day_of_month[rtcregs[7]] != 0);
		if (rtcregs[6] <= last_day_of_month[rtcregs[7]])
			continue;
		rtcregs[6] = 1;

		// Increment BCD Month
		if (ioc_rtc_bcd_increment(7) <= 0x12)
			continue;
		rtcregs[7] = 0x01;
	}
}

void v_matchproto_(mem_pre_read)
io_rtc_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{

	if (debug) return;
	assert (width == 1);
	assert (adr < 32);

	AZ(pthread_mutex_lock(&rtc_mtx));
	space[adr] = rtcregs[adr];
	AZ(pthread_mutex_unlock(&rtc_mtx));
	Trace(trace_ioc_io, "RTC R [%x] -> %x", adr, space[adr]);
	if (adr == 0x0e)
		space[0x0e] = 0;
}

void v_matchproto_(mem_post_write)
io_rtc_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{

	if (debug) return;
	assert (width == 1);
	assert (adr < 32);
	Trace(trace_ioc_io, "RTC W [%x] <- %x", adr, space[adr]);
	AZ(pthread_mutex_lock(&rtc_mtx));
	rtcregs[adr] = space[adr];
	AZ(pthread_mutex_unlock(&rtc_mtx));
}

void
ioc_rtc_init(void)
{

	ioc_rtc_setclock();
	AZ(pthread_create(&rtc_thr, NULL, ioc_rtc_thread, NULL));
}

static const char *configs[] = {
    "+modem-dialout",
    "-modem-dialout",
    "+modem-answer",
    "-modem-answer",
    "+iop-autoboot",
    "-iop-autoboot",
    "+r1000-autoboot",
    "-r1000-autoboot",
    "+auto-crash-recovery",
    "-auto-crash-recovery",
    "+console-break-key",
    "-console-break-key",
    NULL,
};

void v_matchproto_(cli_func_f)
cli_ioc_config(struct cli *cli)
{
	int i, j;

	if (cli->help || cli->ac > 2) {
		Cli_Usage(
		    cli,
		    "[-|+]option",
		    "Operator mode options:\n"
		    "\t    [+|-]modem_dialout\n"
		    "\t    [+|-]modem_answer\n"
		    "\t    [+|-]iop_autoboot\n"
		    "\t    [+|-]r1000_autoboot\n"
		    "\t    [+|-]auto_crash_recovery\n"
		    "\t    [+|-]console_break_key"
		);
		return;
	}
	for (i = 1; i < cli->ac; i++) {
		for (j = 0; configs[j] != NULL; j++) {
			if (!strcmp(cli->av[i], configs[j])) {
				if (j & 1) {
					rtcregs[0xa] &= ~(1 << (j >> 1));
				} else {
					rtcregs[0xa] |= (1 << (j >> 1));
				}
				break;
			}
			if (!strcmp(cli->av[i], configs[j] + 1)) {
				rtcregs[0xa] ^= (1 << (j >> 1));
				break;
			}
		}
		if (configs[j] == NULL)
			Cli_Error(cli, "Unknown flag '%s'\n", cli->av[i]);
	}
	Cli_Printf(cli, "Config is 0x%02x:\n", rtcregs[0xa]);
	for (j = 0; configs[j] != NULL; j += 2) {
		if (rtcregs[0xa] & (1 << (j >> 1)))
			Cli_Printf(cli, "    %s\n", configs[j]);
		else
			Cli_Printf(cli, "    %s\n", configs[j + 1]);
	}
}
