/*
 * CONSOLE UART - SCN2661 Enhanced Programmable communications interface
 * ---------------------------------------------------------------------
 *
 * Chip Select: 0xffff9xxx
 *
 * We implement 8 bytes because the DFS kernel does a 32bit read
 * at 0xffff9001.
 *
 */

#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <vis.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Infra/elastic.h"
#include "Iop/memspace.h"

#define REG_R_DATA	0
#define REG_R_STATUS	1
#define REG_R_MODE	2
#define REG_R_CMD	3

#define REG_W_DATA	0
#define REG_W_SYN_DLE	1
#define REG_W_MODE	2
#define REG_W_CMD	3

static pthread_mutex_t	uart_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t	cons_cond = PTHREAD_COND_INITIALIZER;
static pthread_t	cons_rx;

static struct cons {
	struct elastic	*ep;
	uint8_t		mode[2];
	int		mptr;
	uint8_t		cmd;
	uint8_t		status;
	uint8_t		rxhold;
	uint8_t		txhold;
	uint8_t		txshift;
	uint8_t		txshiftfull;
	int		txbreak;
	int		loopback;
	unsigned	updated;
} cons[1];


static void v_matchproto_(cli_func_f)
cli_ioc_console_break(struct cli *cli)
{
	if (cli->help) {
		Cli_Usage(cli, NULL, "Send BREAK");
		return;
	}
	irq_raise(&IRQ_CONSOLE_BREAK);
	Cli_Printf(cli, "Sending BREAK\n");
	callout_sleep(10000000);
	irq_lower(&IRQ_CONSOLE_BREAK);
	return;
}

void v_matchproto_(cli_func_f)
cli_ioc_console(struct cli *cli)
{

	Elastic_Cli(cons->ep, cli);
}

/**********************************************************************/

static void*
thr_console_rx(void *priv)
{
	uint8_t buf[1];
	ssize_t sz;
	char visbuf[16];

	(void)priv;
	while (1) {
		sz = elastic_get(cons->ep, buf, 1);
		assert(sz == 1);
		(void)vis(visbuf, buf[0], VIS_WHITE | VIS_CSTYLE, '0');
		Trace(trace_console, "CONSOLE RX %s", visbuf);
		AZ(pthread_mutex_lock(&uart_mtx));
		while (!(cons->cmd & 0x04) || (cons->status & 0x02))
			AZ(pthread_cond_wait(&cons_cond, &uart_mtx));
		cons->rxhold = buf[0];
		cons->status |= 0x02;
		uint8_t utrc[2];
		utrc[0] = UT_CONS_RX;
		utrc[1] = buf[0];
		microtrace(utrc, sizeof utrc);
		irq_raise(&IRQ_CONSOLE_RXRDY);
		AZ(pthread_mutex_unlock(&uart_mtx));
		callout_sleep((1000000000/19200) * 10);
	}
}

/**********************************************************************/

static void
cons_txshift_done(void * priv)
{
	(void)priv;
	char visbuf[16];

	AZ(pthread_mutex_lock(&uart_mtx));
	if (!(cons->cmd & 0x01)) {			// Tx disabled
		cons->status &= ~0x05;
		irq_lower(&IRQ_CONSOLE_TXRDY);
		cons->txshiftfull = 0;
	} else if (cons->loopback && cons->txbreak) {
		cons->status |= 0x22;		// Break detected
		irq_raise(&IRQ_CONSOLE_BREAK);
	} else {
		if (cons->loopback && !cons->txbreak && cons->txshiftfull) {
			cons->rxhold = cons->txshift;
			cons->status |= 0x02;
			irq_raise(&IRQ_CONSOLE_RXRDY);
		}
		cons->txshiftfull = 0;
		if (cons->status & 0x01) {		// txhold is empty
			cons->status |= 0x04;		// TxEmt
		} else {
			if (!cons->loopback) {
				(void)vis(visbuf, cons->txhold, VIS_WHITE | VIS_CSTYLE, '0');
				Trace(trace_console, "CONSOLE TX %s", visbuf);
				elastic_put(cons->ep, &cons->txhold, 1);
				uint8_t utrc[2];
				utrc[0] = UT_CONS_TX;
				utrc[1] = cons->txhold;
				microtrace(utrc, sizeof utrc);
			}
			cons->txshift = cons->txhold;
			cons->txshiftfull = 1;
			callout_callback(cons_txshift_done,
			    NULL, 1000, 0);
			cons->status |= 0x01;		// txhold is empty
			irq_raise(&IRQ_CONSOLE_TXRDY);
		}
	}
	AZ(pthread_mutex_unlock(&uart_mtx));
}

/**********************************************************************/

void v_matchproto_(mem_pre_read)
io_uart_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	if (debug) return;
	assert (width == 1);
	assert (adr < 8);
	AZ(pthread_mutex_lock(&uart_mtx));
	switch(adr) {
	case REG_R_DATA:
		space[adr] = cons->rxhold;
		cons->status &= ~2;		// rx-hold empty
		irq_lower(&IRQ_CONSOLE_RXRDY);
		break;
	case REG_R_STATUS:
		space[adr] = cons->status;
		break;
	case REG_R_MODE:
		space[adr] = cons->mode[cons->mptr];
		cons->mptr ^= 1;
		break;
	case REG_R_CMD:
		space[adr] = cons->cmd;
		break;
	default:
		break;
	}
	AZ(pthread_mutex_unlock(&uart_mtx));
}

/**********************************************************************/

void v_matchproto_(mem_post_write)
io_uart_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	unsigned chg;

	if (debug) return;
	assert (width == 1);
	assert (adr < 8);
	AZ(pthread_mutex_lock(&uart_mtx));
	switch (adr) {
	case REG_W_DATA:
		cons->txhold = space[adr];
		cons->status &= ~1;		// tx-hold busy
		cons->status &= ~4;		// tx-shift full
		irq_lower(&IRQ_CONSOLE_TXRDY);
		break;
	case REG_W_MODE:
		cons->mode[cons->mptr] = space[adr];
		cons->mptr ^= 1;
		break;
	case REG_W_CMD:
		chg = space[adr] ^ cons->cmd;

		if ((chg & 0x01) && !(cons->cmd & 0x01)) {
			cons->cmd |= 0x01;	// tx-enabled
			cons->status |= 0x01;	// tx-hold empty
			irq_raise(&IRQ_CONSOLE_TXRDY);
		} else if ((chg & 0x01) && (cons->cmd & 0x01)) {
			cons->cmd &= ~0x01;	// tx-disabled
			cons->status &= ~0x05;	// tx-hold empty
			irq_lower(&IRQ_CONSOLE_TXRDY);
		}

		if ((chg & 0x04) && !(cons->cmd & 0x04)) {
			cons->cmd |= 0x04;	// rx-enabled
			cons->status &= ~0x02;	// rx-hold empty
		} else if ((chg & 0x04) && (cons->cmd & 0x04)) {
			cons->cmd &= ~0x04;	// rx-disabled
			cons->status &= ~0x02;	// rx-hold empty
			irq_lower(&IRQ_CONSOLE_RXRDY);
		}

		if (space[adr] & 0x10) {
			cons->status &= ~0x38;
			irq_lower(&IRQ_CONSOLE_BREAK);
		}

		cons->cmd &= ~0xea;
		cons->cmd |= space[adr] & 0xea;

		if ((chg & 0x08) && !cons->txbreak) {
			cons->txbreak = 1;
			cons->status &= ~0x05;	// tx-hold empty
			irq_lower(&IRQ_CONSOLE_TXRDY);
		} else if ((chg & 0x08) && cons->txbreak) {
			cons->txbreak = 0;
			cons->status |= 0x01;	// tx-hold empty
			irq_raise(&IRQ_CONSOLE_TXRDY);
			irq_lower(&IRQ_CONSOLE_BREAK);
		}
		cons->loopback = (cons->cmd & 0xc0) == 0x80;
		break;
	default:
		break;
	}
	cons->updated = 1;
	AZ(pthread_cond_broadcast(&cons_cond));
	AZ(pthread_mutex_unlock(&uart_mtx));
	if (cons->txbreak && cons->loopback)
		callout_callback(cons_txshift_done, NULL, 1000, 0);
	else if (!(cons->status & 1) && !cons->txshiftfull)
		cons_txshift_done(NULL);
}

void
ioc_console_init(void)
{

	cons->ep = elastic_new(O_RDWR, "console");
	cons->ep->break_function = cli_ioc_console_break;
	AZ(pthread_create(&cons_rx, NULL, thr_console_rx, NULL));
}
