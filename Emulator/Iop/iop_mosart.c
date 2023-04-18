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
static const char MS_FUNCTION[] = "Function";

static struct {
	const char	*state;
	uint8_t		mode;
	uint8_t		cmd;
	const char	*resp;
} mosart = {
	MS_RESET,
	0,
	0,
	"",
};

static const char *
io_mosart_show_state(void)
{
	static char buf[80];

	bprintf(buf,
	    "<%s mode=0x%02x cmd=0x%02x resp='%s'>",
	    mosart.state,
	    mosart.mode,
	    mosart.cmd,
	    mosart.resp
	);
	return (buf);
}

void v_matchproto_(mem_pre_read)
io_mosart_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	uint8_t data;

	if (debug) return;
	if (adr) {
		data = 0;
		if (mosart.cmd & 1)
			data |= 0x5;
		if ((mosart.cmd & 4) && *mosart.resp)
			data |= 0x2;
		space[adr] = data;
	} else {
		if (*mosart.resp) {
			space[adr] = *mosart.resp++;
			if (!*mosart.resp)
				mosart.resp = "";
		}
	}
	Trace(trace_ioc_modem,
	    "MOSART R [%x] -> %02x (w%d) %s", adr, space[adr], width,
	    io_mosart_show_state()
	);
}

void v_matchproto_(mem_post_write)
io_mosart_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	uint8_t data = space[adr];

	if (debug) return;
	if (adr) {
		if (mosart.state == MS_RESET) {
			mosart.mode = data;
			mosart.state = MS_FUNCTION;
		} else if (data & 0x40) {
			mosart.state = MS_RESET;
		} else {
			mosart.cmd = data;
		}
	} else {
		if (mosart.state == MS_FUNCTION) {
			if (data == 'I')
				mosart.resp = "A";
		}
	}
	Trace(trace_ioc_modem,
	    "MOSART W [%x] <- %02x (w%d) %s", adr, data, width,
	    io_mosart_show_state()
	);
	if (mosart.cmd & 1) {
		irq_raise(&IRQ_MOSART_TXRDY);
	} else {
		irq_lower(&IRQ_MOSART_TXRDY);
	}
	if ((mosart.cmd & 4) && *mosart.resp) {
		irq_raise(&IRQ_MOSART_RXRDY);
	} else {
		irq_lower(&IRQ_MOSART_RXRDY);
	}
}
