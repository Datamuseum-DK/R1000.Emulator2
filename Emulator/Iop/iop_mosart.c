/*
 * XECOM XE1201 "MOSART™" internal modem
 * -------------------------------------
 *
 * Chip Select: 0xffffbxxx
 *
 */

#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Iop/memspace.h"

static const char MS_RESET[] = "Reset";
static const char MS_INIT[] = "Init";
// static const char MS_FUNCTION[] = "Function";

static struct {
	const char	*state;
	uint8_t		mode;
	uint8_t		cmd;
	uint8_t		status;
	const char	*resp;
} mosart = {
	MS_RESET,
	0,
	0,
	0,
	NULL,
};

static const char *
io_mosart_show_state(void)
{
	static char buf[80];

	bprintf(buf,
	    "<mode=0x%02x status=0x%02x cmd=0x%02x %s resp='%s'>",
	    mosart.mode,
	    mosart.status,
	    mosart.cmd,
	    mosart.state,
	    mosart.resp
	);
	return (buf);
}

void v_matchproto_(mem_pre_read)
io_mosart_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	(void)debug;
	if (adr == 3) {
		if (mosart.resp == NULL) {
			mosart.status &= ~0x02;
		} else {
			mosart.status |= 0x02;
		}
		if (mosart.cmd & 1)
			mosart.status |= 0x05;
		else
			mosart.status &= ~0x05;
		space[adr] = mosart.status;
	} else if (adr == 2) {
		if (mosart.resp != NULL) {
			space[adr] = *mosart.resp++;
			if (*mosart.resp == '\0') {
				mosart.resp = NULL;
				mosart.status &= ~0x02;
			}
		} else {
			space[adr] = 0x00;
		}
	}
	Trace(trace_ioc_modem,
	    "MOSART R [%x] -> %02x (w%d) %s", adr, space[adr], width,
	    io_mosart_show_state()
	);
	if (mosart.status & 1)
		irq_raise(&IRQ_MOSART_TXRDY);
	else
		irq_lower(&IRQ_MOSART_TXRDY);
}

void v_matchproto_(mem_post_write)
io_mosart_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	uint8_t data = space[adr];

	(void)debug;
	if (adr == 3) {
		if (mosart.state == MS_RESET) {
			mosart.mode = data;
			mosart.state = MS_INIT;
			mosart.cmd = 5;
			mosart.status = 5;
		} else if (mosart.state == MS_INIT) {
			if (data & 0x40) {
				mosart.state = MS_RESET;
				mosart.cmd = 5;
				mosart.status = 5;
			} else {
				mosart.cmd = data;
				mosart.status &= ~0x05;
				mosart.status |= data & 0x05;
			}
		}
	} else if (adr == 2) {
		if (data == 'I') {
			mosart.resp = "K";
			mosart.status |= 0x02;
		}
	}
	if (mosart.status & 1)
		irq_raise(&IRQ_MOSART_TXRDY);
	else
		irq_lower(&IRQ_MOSART_TXRDY);
	Trace(trace_ioc_modem,
	    "MOSART W [%x] <- %02x (w%d) %s", adr, data, width,
	    io_mosart_show_state()
	);
}
