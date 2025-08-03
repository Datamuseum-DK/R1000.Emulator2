/*
 * MODEM/DIAG DUART - SCN2681 Dual asynchronous receiver/transmitter
 * -----------------------------------------------------------------
 *
 * Chip Select: 0xffffaxxx
 *
 *	IP0	MODEM_CTS		OP0	MODEM_RTS
 * 	IP1	MODEM_DSR		OP1	MODEM_DTR
 * 	IP2	PITCLK			OP2	IOP.BLOOP~
 * 	IP3	MODEM_DCD		OP3	PITINT
 * 	IP4	n/c			OP4	MODEM.RXRDY
 * 	IP5	CLK			OP5	DIAGBUS.RXDRY
 * 	IP6	CLK			OP6	MODEM.TXRDY
 *					OP7	DIAGBUS.TXRDY
 *
 */

#include <fcntl.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Infra/elastic.h"
#include "Infra/vsb.h"
#include "Iop/memspace.h"
#include "Diag/diag.h"
#include "Chassis/r1000_arch.h"

#define IP0_CTS		0x01
#define IP1_DSR		0x02
#define IP3_DCD		0x08

static const char * const rd_reg[] = {
	"MODEM R MR1A_2A",
	"MODEM R SRA",
	"DUART R BRG_Test",
	"MODEM R RHRA",
	"DUART R IPCR",
	"DUART R ISR",
	"PIT R CTU",
	"PIT R CTL",
	"DIAGBUS R MR1B_2B",
	"DIAGBUS R SRB",
	"DUART R 1x/16x_Test",
	"DIAGBUS R RHRB",
	"DUART R Reserved",
	"DUART R Input_Port",
	"PIT R Start_Counter_Command",
	"PIT R Stop_Counter_Command",
};

static const char * const wr_reg[] = {
	"MODEM W MR1A_2A",
	"MODEM W CSRA",
	"MODEM W CRA",
	"MODEM W THRA",
	"DUART W ACR",
	"DUART W IMR",
	"PIT W CTUR",
	"PIT W CTLR",
	"DIAGBUS W MR1B_2B",
	"DIAGBUS W CSRB",
	"DIAGBUS W CRB",
	"DIAGBUS W THRB",
	"DUART W Reserved",
	"DUART W OPCR",
	"DUART W Set_Output_Port_Bits_Command",
	"DUART W Reset_Output_Port_Bits_Command",
};

#define REG_W_MRA	0
#define REG_W_CSRA	1
#define REG_W_CRA	2
#define REG_W_THRA	3
#define REG_W_ACR	4
#define REG_W_IMR	5
#define REG_W_CTUR	6
#define REG_W_CTLR	7
#define REG_W_MRB	8
#define REG_W_CSRB	9
#define REG_W_CRB	10
#define REG_W_THRB	11
#define REG_W_OPCR	13
#define REG_W_SET_BITS	14
#define REG_W_CLR_BITS	15

#define REG_R_MRA	0
#define REG_R_SRA	1
#define REG_R_BRG_TEST	2
#define REG_R_RHRA	3
#define REG_R_IPCR	4
#define REG_R_ISR	5
#define REG_R_CTU	6
#define REG_R_CTL	7
#define REG_R_MRB	8
#define REG_R_SRB	9
#define REG_R_1_16_TEST	10
#define REG_R_RHRB	11
#define REG_R_INPUT	13
#define REG_R_START_PIT	14
#define REG_R_STOP_PIT	15

struct chan {
	struct elastic		*ep;
	const char		*name;
	int			is_diagbus;
	uint8_t			mode[2];
	uint8_t			rxhold;
	uint8_t			txshift[2];
	int			txshift_valid;
	int			mrptr;
	int			sr;
	int			rxwaitforit;
	int			txon;
	int			rxon;
	uint8_t			tx_isr_bit;
	struct irq_vector	*rx_irq;
	struct irq_vector	*tx_irq;
	int			inflight;
	struct vsb		*vsb;
	pthread_cond_t		*cond;
};

static struct ioc_duart {
	struct chan		chan[2];
	uint8_t			opr;
	uint16_t		counter;
	uint8_t			acr;
	uint8_t			imr;
	uint8_t			isr;
	uint8_t			ipcr, prev_ipcr;
	int			pit_running;
	int			pit_intr;
} ioc_duart[1];

static pthread_mutex_t duart_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t diagbus_cond = PTHREAD_COND_INITIALIZER;
static pthread_cond_t modem_cond = PTHREAD_COND_INITIALIZER;
static pthread_t diag_rx;
static pthread_t modem_rx;
static pthread_t modem_sim;

/**********************************************************************/

static void
ioc_duart_pit_tick(void)
{
	AZ(pthread_mutex_lock(&duart_mtx));
	Trace(trace_ioc_pit, "PIT tick 0x%04x", ioc_duart->counter);
	if (ioc_duart->pit_running == 1) {
		ioc_duart->pit_running = 2;
	} else if (ioc_duart->pit_running == 2) {
		if (!--ioc_duart->counter) {
			Trace(trace_ioc_pit, "PIT ZERO");
			io_duart_rd_space[REG_R_ISR] |= 0x8;
			if (ioc_duart->pit_intr) {
				irq_raise(&IRQ_PIT);
				ioc_duart->opr |= 0x08;
			}
		}
	}
	AZ(pthread_mutex_unlock(&duart_mtx));
}

static void
ioc_duart_pit_callback(void *priv)
{
	(void)priv;
	if (!systemc_clock)
		ioc_duart_pit_tick();
}

void
pit_clock(void)
{
	if (systemc_clock)
		ioc_duart_pit_tick();
}

/**********************************************************************/

static void*
thr_duart_rx(void *priv)
{
	uint8_t buf[1];
	struct chan *chp = priv;
	ssize_t sz;

	(void)priv;
	ioc_wait_cpu_running();		// Dont hog diagbus until IOC owns it
	while (1) {
		sz = elastic_get(chp->ep, buf, 1);
		assert(sz == 1);
		callout_sleep(chp->inflight);
		AZ(pthread_mutex_lock(&duart_mtx));
		while (!(chp->rxon) || (chp->sr & 1) || chp->rxwaitforit)
			AZ(pthread_cond_wait(chp->cond, &duart_mtx));
		chp->rxhold = buf[0];
		chp->sr |= 0x01;
		chp->rxwaitforit |= 0x01;
		irq_raise(chp->rx_irq);
		AZ(pthread_mutex_unlock(&duart_mtx));
	}
}

static void
io_duart_rx_readh_cb(void *priv)
{
	struct chan *chp = priv;

	AZ(pthread_mutex_lock(&duart_mtx));
	chp->rxwaitforit = 0;
	AZ(pthread_cond_signal(chp->cond));
	AZ(pthread_mutex_unlock(&duart_mtx));
}

static void
ioc_duart_pace_downloads(struct chan *chp)
{
	/*
	 * Bulk downloads of ucode and regfile are not flow-controlled,
	 * because the DIPROCs can keep pace with the IOP+DISK+DIAGBUS.
	 * Our speed-mix is different, so hold downloads back if the
	 * DIPROC is still in state running
	 */
	uint8_t adr, cmd;

	cmd = chp->txshift[1] & 0xe0;
	if (cmd == 0x00) {
		// STATUS
		usleep(50000);
	} else if (cmd == 0xa0) {
		// DOWNLOAD
		(void)elastic_drain(chp->ep);
		adr = chp->txshift[1] & 0x1f;
		while ((diprocs[adr].status & 0x0f) == (int)DIPROC_RESPONSE_RUNNING) {
			Trace(
			    trace_diagbus,
			    "%s Holding Download (0x%x%02x)",
			    chp->name,
			    chp->txshift[0],
			    chp->txshift[1]
			);
			usleep(10000);
		}
	}
}

static void
ioc_duart_tx_callback(void *priv)
{
	struct chan *chp = priv;
	uint8_t adr, cmd;

	if (chp->is_diagbus) {
		assert (chp->txshift_valid == 2);
		VSB_clear(chp->vsb);
		VSB_cat(chp->vsb, "IOP TX ");
		DiagBus_Explain_Cmd(chp->vsb, chp->txshift);
		AZ(VSB_finish(chp->vsb));
		Trace(trace_diagbus, "%s", VSB_data(chp->vsb));
		if (chp->txshift[0])
			ioc_duart_pace_downloads(chp);
		elastic_put(chp->ep, chp->txshift, chp->txshift_valid);
		if (chp->txshift[0]) {
			cmd = chp->txshift[1] & 0xe0;
			adr = chp->txshift[1] & 0x1f;
			if (cmd == 0x80 && adr != 5) {
				(void)elastic_drain(chp->ep);
				usleep(100000);
				Trace(
				    trace_diagbus,
				    "%s Post Reset (0x%x%02x)",
					    chp->name,
					    chp->txshift[0],
					    chp->txshift[1]
				);
			}
		}
	} else {
		Trace(trace_ioc_modem, "MODEM TX %02x %02x %02x", chp->txshift[0], chp->txshift[1], chp->txshift_valid);
		elastic_put(chp->ep, chp->txshift, chp->txshift_valid);
	}
	chp->txshift_valid = 0;
	chp->sr |= 4;
	chp->sr |= 8;
	if (chp->txon)
		irq_raise(chp->tx_irq);
}

/*********************************************************************/

static void
io_duart_dschg(void)
{
	uint8_t events, event_mask;

	Trace(trace_ioc_duart, "MODEM dschg IMR=%02x ISR=%02x ACR=%02x IPCR=%02x/%02x OP=%02x",
	    ioc_duart->imr,
	    ioc_duart->isr,
	    ioc_duart->acr,
	    ioc_duart->ipcr,
	    ioc_duart->prev_ipcr,
	    ioc_duart->opr
	);

	event_mask = ioc_duart->acr & 0xf;
	events = (ioc_duart->ipcr ^ ioc_duart->prev_ipcr) & 0xf;
	ioc_duart->prev_ipcr = ioc_duart->ipcr;

	ioc_duart->ipcr |= events << 4;
	Trace(trace_ioc_duart, "MODEM IPCR=%02x", ioc_duart->ipcr);
	if ((ioc_duart->ipcr >> 4) & event_mask) {
		ioc_duart->isr |= 0x80;
		Trace(trace_ioc_duart, "MODEM ISR=%02x", ioc_duart->isr);
	}
	if (ioc_duart->isr & ioc_duart->imr) {
		irq_raise(&IRQ_MODEM_DSCHG);
	} else if (!(ioc_duart->isr & ioc_duart->imr)) {
		irq_lower(&IRQ_MODEM_DSCHG);
	}
}

static void*
thr_modem_sim(void *priv)
{
	struct chan *chp = priv;
	int state = 0;

	// ioc_wait_cpu_running();		// Dont hog diagbus until IOC owns it
	while (1) {
		AZ(pthread_mutex_lock(&duart_mtx));
		switch (state) {
		case 0:
			AZ(pthread_cond_wait(&modem_cond, &duart_mtx));
			if ((ioc_duart->ipcr & 3) == (ioc_duart->opr & 3)) {
				break;
			}
			AZ(pthread_mutex_unlock(&duart_mtx));
			callout_sleep(1000000); 
			AZ(pthread_mutex_lock(&duart_mtx));
			ioc_duart->ipcr &= ~0xb;
			ioc_duart->ipcr |= ioc_duart->opr & 0x3;
			Trace(trace_ioc_duart,
			    "MODEM SIG CHG IPCR=%02x", ioc_duart->ipcr);
			io_duart_dschg();
			if (ioc_duart->ipcr & 3)
				state = 1;
			break;
		case 1:
#define SIMTX(str) \
	do { \
		AZ(pthread_mutex_unlock(&duart_mtx)); \
		callout_sleep(100000); \
		AZ(pthread_mutex_lock(&duart_mtx)); \
		elastic_inject(chp->ep, str, -1); \
	} while (0)
			SIMTX("S");
			SIMTX("E");
			SIMTX("R");
			SIMTX("V");
			SIMTX("I");
			SIMTX("C");
			SIMTX("E");
			SIMTX(":");
			SIMTX("\r");
			SIMTX("\n");
			state = 0;
			break;
		}
		AZ(pthread_mutex_unlock(&duart_mtx));
	}
}

// void elastic_inject(struct elastic *ep, const void *ptr, ssize_t len);


/**********************************************************************/

void v_matchproto_(mem_pre_read)
io_duart_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	struct chan *chp;

	if (debug) return;
	assert (width == 1);
	assert (adr < 16);

	AZ(pthread_mutex_lock(&duart_mtx));
	chp = &ioc_duart->chan[adr>>3];
	switch(adr) {
	case REG_R_ISR:
		space[adr] = ioc_duart->isr;
		break;
	case REG_R_IPCR:
		space[adr] = ioc_duart->ipcr;
		ioc_duart->ipcr &= 0xf;
		ioc_duart->isr &= 0x7f;
		if (!(ioc_duart->isr & ioc_duart->imr)) {
			irq_lower(&IRQ_MODEM_DSCHG);
		}
		break;
	case REG_R_INPUT:
		space[adr] = ioc_duart->ipcr & 0xf;
		break;
	case REG_R_SRA:
	case REG_R_SRB:
		space[adr] = chp->sr;
		break;
	case REG_R_RHRA:
	case REG_R_RHRB:
		space[adr] = chp->rxhold;
		chp->sr &= ~1;
		irq_lower(chp->rx_irq);
		/*
		 * The KERNEL (0x0000371c) does multiple reads of the
		 * RX holding register.  To avoid the race we hold back
		 * the thr_duart_rx() thread back a little bit.
		 */
		callout_callback(io_duart_rx_readh_cb, chp, 100000, 0);
		break;
	case REG_R_CTU:
	case REG_R_CTL:
		io_duart_rd_space[REG_R_CTU] = ioc_duart->counter >> 8;
		io_duart_rd_space[REG_R_CTL] = ioc_duart->counter;
		break;
	case REG_R_START_PIT:
		ioc_duart->counter = io_duart_wr_space[REG_W_CTLR];
		ioc_duart->counter |= io_duart_wr_space[REG_W_CTUR] << 8;
		ioc_duart->pit_running = 1;
		Trace(trace_ioc_pit, "PIT START 0x%04x", ioc_duart->counter);
		break;
	case REG_R_STOP_PIT:
		Trace(trace_ioc_pit, "PIT STOP");
		ioc_duart->pit_running = 0;
		io_duart_rd_space[REG_R_ISR] &= ~0x8;
		irq_lower(&IRQ_PIT);
		if (ioc_duart->pit_intr)
			ioc_duart->opr &= ~0x08;
		break;
	default:
		break;
	}
	AZ(pthread_mutex_unlock(&duart_mtx));
	Trace(trace_ioc_duart, "%s [%x] -> %x", rd_reg[adr], adr, space[adr]);
}

/**********************************************************************/

void v_matchproto_(mem_post_write)
io_duart_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	struct chan *chp;

	if (debug) return;
	assert (width == 1);
	assert (adr < 16);
	Trace(trace_ioc_duart, "%s [%x] <- %x", wr_reg[adr], adr, space[adr]);
	AZ(pthread_mutex_lock(&duart_mtx));
	chp = &ioc_duart->chan[adr>>3];
	switch(adr) {
	case REG_W_MRA:
	case REG_W_MRB:
		chp->mode[chp->mrptr] = space[adr];
		chp->mrptr ^= 1;
		break;
	case REG_W_CRA:
	case REG_W_CRB:
		switch ((space[adr] >> 4) & 0x7) {
		case 0x1:
			chp->mrptr = 0;
			break;
		case 0x2:
			break;
		case 0x3:
			chp->txon = 0;
			ioc_duart->isr &= ~chp->tx_isr_bit;
			chp->sr &= ~4;
			irq_lower(chp->tx_irq);
			break;
		case 0x4:
			chp->mrptr = 0;
			break;
		default:
			break;
		}
		if (space[adr] & 1) {
			chp->rxon = 1;
		}
		if (space[adr] & 2) {
			chp->rxon = 0;
		}
		if (space[adr] & 4) {
			if (!chp->txon) {
				chp->txon = 1;
				ioc_duart->isr |= chp->tx_isr_bit;
				chp->sr |= 4;
				chp->sr |= 8;
				irq_raise(chp->tx_irq);
			}
		}
		if (space[adr] & 8) {
			chp->txon = 0;
			ioc_duart->isr &= ~chp->tx_isr_bit;
			chp->sr &= ~4;
			chp->sr |= 8;
			irq_lower(chp->tx_irq);
		}
		break;
	case REG_W_IMR:
		ioc_duart->imr = space[adr];
		io_duart_dschg();
		if (!(ioc_duart->isr & ioc_duart->imr)) {
			irq_lower(&IRQ_MODEM_DSCHG);
		}
		break;
	case REG_W_ACR:
		ioc_duart->acr = space[adr];
		ioc_duart->prev_ipcr = 0;
		io_duart_dschg();
		break;
	case REG_W_THRA:
	case REG_W_THRB:
		if (chp->is_diagbus && ioc_duart->opr & 4) {
			// IOP.DLOOP~ on p21
			chp->rxhold = space[adr];
			chp->sr |= 1;
		} else if (chp->mode[1] & 0x80) {
			// Internal Local Loop
			chp->rxhold = space[adr];
			chp->sr |= 1;
		} else {
			if (adr == REG_W_THRB) {
				chp->txshift[0] = (chp->mode[0] >> 2) & 1;
				chp->txshift[1] = space[adr];
				chp->txshift_valid = 2;
			} else {
				chp->txshift[0] = space[adr];
				chp->txshift_valid = 1;
			}
			chp->sr &= ~4;
			chp->sr &= ~8;
			irq_lower(chp->tx_irq);
			callout_callback(ioc_duart_tx_callback,
			    chp, chp->inflight, 0);
		}
		break;
	case REG_W_OPCR:
		ioc_duart->pit_intr = (space[adr] & 0x0c) == 0x04;
		break;
	case REG_W_SET_BITS:
		ioc_duart->opr |= space[adr];
		if (ioc_duart->opr & 0x10)
			irq_raise(&IRQ_MODEM_RXRDY);
		if (ioc_duart->opr & 0x20)
			irq_raise(&IRQ_DIAG_BUS_RXRDY);
		if (ioc_duart->opr & 0x80)
			irq_raise(&IRQ_DIAG_BUS_TXRDY);

		AZ(pthread_cond_signal(&modem_cond));
		break;
	case REG_W_CLR_BITS:
		ioc_duart->opr &= ~space[adr];
		if (!(ioc_duart->opr & 0x10))
			irq_lower(&IRQ_MODEM_RXRDY);
		if (!(ioc_duart->opr & 0x10))
			irq_lower(&IRQ_DIAG_BUS_RXRDY);
		if (!(ioc_duart->opr & 0x80))
			irq_lower(&IRQ_DIAG_BUS_TXRDY);

		AZ(pthread_cond_signal(&modem_cond));
		break;
	default:
		break;
	}
	AZ(pthread_mutex_unlock(&duart_mtx));
}

/**********************************************************************/

void v_matchproto_(cli_func_f)
cli_ioc_modem(struct cli *cli)
{
	struct chan *chp = &ioc_duart->chan[0];

	Elastic_Cli(chp->ep, cli);
}

void
ioc_duart_init(void)
{

	ioc_duart->chan[0].ep = elastic_new(O_RDWR, "comm");
	ioc_duart->chan[0].rx_irq = &IRQ_MODEM_RXRDY;
	ioc_duart->chan[0].tx_irq = &IRQ_MODEM_TXRDY;
	ioc_duart->chan[0].name = "MODEM";
	ioc_duart->chan[0].inflight = 1041666;		// 9600
	ioc_duart->chan[0].tx_isr_bit = 0x01;
	ioc_duart->chan[0].cond = &modem_cond;

	AN(diag_elastic);
	ioc_duart->chan[1].ep = diag_elastic;
	ioc_duart->chan[1].ep->text = 0;
	ioc_duart->chan[1].rx_irq = &IRQ_DIAG_BUS_RXRDY;
	ioc_duart->chan[1].tx_irq = &IRQ_DIAG_BUS_TXRDY;
	ioc_duart->chan[1].name = "DIAGBUS";
	ioc_duart->chan[1].is_diagbus = 1;
	ioc_duart->chan[1].vsb = VSB_new_auto();
	ioc_duart->chan[1].tx_isr_bit = 0x10;
	ioc_duart->chan[1].cond = &diagbus_cond;
	AN(ioc_duart->chan[1].vsb);

	ioc_duart->ipcr = IP0_CTS | IP1_DSR | IP3_DCD;
	ioc_duart->ipcr = IP0_CTS | IP1_DSR;

	// 1/10_MHz * (64 * 11_bits) = 70400 nsec
	ioc_duart->chan[1].inflight = 70400;
	ioc_duart->chan[1].inflight /= 2;		// hack

	callout_callback(ioc_duart_pit_callback, NULL, 0, 25600);
	AZ(pthread_create(&diag_rx, NULL, thr_duart_rx, &ioc_duart->chan[1]));
	AZ(pthread_create(&modem_rx, NULL, thr_duart_rx, &ioc_duart->chan[0]));
	AZ(pthread_create(&modem_sim, NULL, thr_modem_sim, &ioc_duart->chan[0]));
}
