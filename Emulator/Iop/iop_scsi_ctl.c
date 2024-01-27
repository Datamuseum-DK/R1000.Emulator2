#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Iop/memspace.h"
#include "Iop/iop_scsi.h"
#include "Infra/vend.h"

struct scsi scsi_t[1];
struct scsi scsi_d[1];

/**********************************************************************/

static const char * const scsi_cmd_name[256] = {
#define SCSI_CMD(name, number) [number] = #name,
SCSI_CMD_TABLE
};

static const char * const scsi_reg[] = {
	"00_OWN_ID_CDB_SIZE",
	"01_CONTROL",
	"02_TIMEOUT_PERIOD",
	"03_CDB1",
	"04_CDB2",
	"05_CDB3",
	"06_CDB4",
	"07_CDB5",
	"08_CDB6",
	"09_CDB7",
	"0a_CDB8",
	"0b_CDB9",
	"0c_CDB10",
	"0d_CDB11",
	"0e_CDB12",
	"0f_LUN",
	"10_CMD_PHASE",
	"11_SYNC_XFER",
	"12_COUNT2",
	"13_COUNT1",
	"14_COUNT0",
	"15_DEST_ID",
	"16_SRC_ID",
	"17_SCSI_STATUS",
	"18_CMD",
	"19_DATA",
	"1a_unknown",
	"1b_unknown",
	"1c_unknown",
	"1d_unknown",
	"1e_unknown",
	"1f_AUX_STATUS",
};

static void
trace_scsi_ctl(struct scsi *sp, const char *cmt)
{

	Trace(
	    trace_scsi_cmd,
	    "%s CMD=%02x ID=%x"
	    " CDB=[%02x %02x %02x %02x %02x %02x|%02x %02x %02x %02x]"
	    " LEN=[%02x %02x %02x]"
	    " %s",
	    sp->name,
	    sp->regs[0x18],
	    sp->regs[0x15] & 7,
	    sp->regs[0x03],
	    sp->regs[0x04],
	    sp->regs[0x05],
	    sp->regs[0x06],
	    sp->regs[0x07],
	    sp->regs[0x08],
	    sp->regs[0x09],
	    sp->regs[0x0a],
	    sp->regs[0x0b],
	    sp->regs[0x0c],
	    sp->regs[0x12],
	    sp->regs[0x13],
	    sp->regs[0x14],
	    cmt
	);
}

void
trace_scsi_dev(struct scsi_dev *dev, const char *cmt)
{
	trace_scsi_ctl(dev->ctl, cmt);
}

void
scsi_to_target(struct scsi_dev *sd, void *ptr, unsigned len)
{
	unsigned xlen;
	uint8_t *pp = ptr;

	assert(!(sd->ctl->regs[0x15] & 0x40));
	xlen = vbe32dec(sd->ctl->regs + 0x11) & 0xffffff;
	assert(len <= xlen);
	for (xlen = 0; xlen < len; xlen += (1<<10)) {
		dma_read(sd->ctl->dma_seg, sd->ctl->dma_adr + xlen, pp + xlen, 1<<10);
	}
	Trace(trace_scsi_cmd, "%s T %p <- R [%x]", sd->ctl->name, ptr, len);
}

void
scsi_fm_target(struct scsi_dev *sd, void *ptr, unsigned len)
{
	unsigned xlen;
	uint8_t *pp = ptr;

	assert((sd->ctl->regs[0x15] & 0x40));
	xlen = vbe32dec(sd->ctl->regs + 0x11) & 0xffffff;
	assert(len <= xlen);
	for (xlen = 0; xlen < len; xlen += (1<<10)) {
		dma_write(sd->ctl->dma_seg, sd->ctl->dma_adr + xlen, pp + xlen, 1<<10);
	}
	Trace(trace_scsi_cmd, "%s T %p -> R [%x]", sd->ctl->name, ptr, len);
}

static void *
scsi_thread(void *priv)
{
	struct scsi *sp = priv;
	struct scsi_dev *sd = NULL;
	scsi_func_f *sf;
	unsigned id;
	const char *p;
	int i;

	AZ(pthread_mutex_lock(&sp->mtx));
	while (1) {
		AZ(pthread_cond_wait(&sp->cond, &sp->mtx));

		if (sp->regs[0x18] == 0) {		// RESET
			memset(sp->regs, 0, sizeof sp->regs);
			sp->regs[0x17] = 0x01;
			sp->regs[0x1f] |= 0x80;
			irq_raise(sp->irq_vector);
			continue;
		}

		if (sp->regs[0x18] != 8)
			WRONG();

		id = sp->regs[0x15] & 7;

		p = scsi_cmd_name[sp->regs[0x3]];
		if (p == NULL)
			p = "<unknown>";
		if (sp->regs[0x3] >> 5) {
			Trace(trace_scsi_cmd,
			    "SCSI_CMD %s ID=%u %s "
			    "[%02x %02x %02x %02x %02x "
			    "%02x %02x %02x %02x %02x]",
			    sp->name, id, p,
			    sp->regs[0x3], sp->regs[0x4], sp->regs[0x5],
			    sp->regs[0x6], sp->regs[0x7], sp->regs[0x8],
			    sp->regs[0x9], sp->regs[0xa], sp->regs[0xb],
			    sp->regs[0xc]
			);
		} else {
			Trace(trace_scsi_cmd,
			    "SCSI_CMD %s ID=%u %s "
			    "[%02x %02x %02x %02x %02x %02x]",
			    sp->name, id, p,
			    sp->regs[0x3], sp->regs[0x4], sp->regs[0x5],
			    sp->regs[0x6], sp->regs[0x7], sp->regs[0x8]
			);
		}

		sd = sp->dev[id];

		uint8_t utrc[10];
		utrc[0] = sp->utrace;
		utrc[1] = id;
		memcpy(utrc + 2, sp->regs + 3, 8);
		microtrace(utrc, sizeof utrc);

		if (sd == NULL) {
			trace_scsi_ctl(sp, "No Device at ID");
			sp->regs[0x17] = 0x42;
		} else if (sd->funcs[sp->regs[0x03]] == NULL) {
			trace_scsi_ctl(sp, "UNIMPL");
			sp->regs[0x17] = 0x42;
		} else {
			sf = sd->funcs[sp->regs[0x03]];
			AN(sf);
			i = sf(sd, sp->regs+0x03);
			if (i < 0) {
				sp->regs[0x14] = 0;
				sp->regs[0x13] = 0;
				sp->regs[0x12] = 0;
				sp->regs[0x17] = 0x42;
			} else {
				sp->regs[0x14] = i & 0xff;
				sp->regs[0x13] = ((unsigned)i>>8) & 0xff;
				sp->regs[0x12] = ((unsigned)i>>16) & 0xff;
				sp->regs[0x17] = 0x16;
			}
		}
		Trace(trace_scsi_cmd,
		    "SCSI_RSP %s ID=%u %02x", sp->name, id, sp->regs[0x17]);
		sp->regs[0x1f] |= 0x80;
		irq_raise(sp->irq_vector);
	}
}

static void
scsi_ctrl_post_write(struct scsi *sp, uint8_t *space, unsigned adr)
{
	assert (adr < 32);

	Trace(trace_ioc_io, "%s W %s [%x] <- %x",
	    sp->name, scsi_reg[adr], adr, space[adr]);
	AZ(pthread_mutex_lock(&sp->mtx));
	sp->regs[adr] = space[adr];
	if (adr == 0x18) {
		Trace(trace_scsi_cmd, "%s REGS"
		    " %02x %02x %02x"
		    " [%02x %02x %02x %02x"
		    " %02x %02x %02x %02x"
		    " %02x %02x %02x %02x]"
		    " %02x %02x %02x"
		    " [%02x %02x %02x]"
		    " %02x %02x %02x %02x %02x %02x",
		    sp->name, sp->regs[0x00], sp->regs[0x01], sp->regs[0x02],
		    sp->regs[0x03], sp->regs[0x04], sp->regs[0x05],
		    sp->regs[0x06], sp->regs[0x07], sp->regs[0x08],
		    sp->regs[0x09], sp->regs[0x0a], sp->regs[0x0b],
		    sp->regs[0x0c], sp->regs[0x0d], sp->regs[0x0e],
		    sp->regs[0x0f], sp->regs[0x10], sp->regs[0x11],
		    sp->regs[0x12], sp->regs[0x13], sp->regs[0x14],
		    sp->regs[0x15], sp->regs[0x16], sp->regs[0x17],
		    sp->regs[0x18], sp->regs[0x19], sp->regs[0x1f]
		);
		AZ(pthread_cond_signal(&sp->cond));
	}
	AZ(pthread_mutex_unlock(&sp->mtx));
}

static void
scsi_ctrl_pre_read(struct scsi *sp, uint8_t *space, unsigned adr)
{

	assert (adr < 32);
	AZ(pthread_mutex_lock(&sp->mtx));
	if (adr == 0x17) {
		sp->regs[0x1f] &= ~0x80;
		irq_lower(sp->irq_vector);
	}
	space[adr] = sp->regs[adr];
	AZ(pthread_mutex_unlock(&sp->mtx));
	Trace(trace_ioc_io, "%s R %s [%x] -> %x",
	    sp->name, scsi_reg[adr], adr, space[adr]);
}

static void
scsi_ctrl_reset(void *priv)
{
	struct scsi *sp = priv;
	int id;

	AZ(pthread_mutex_lock(&sp->mtx));
	// Rewind on reset
	for (id = 0; id < 7; id++) {
		if (sp->dev[id] != NULL) {
			sp->dev[id]->tape_head = 0;
			sp->dev[id]->tape_recno = 0;
		}
	}
	memset(sp->regs, 0, sizeof sp->regs);
	sp->regs[0x1f] |= 0x80;
	sp->regs[0x17] = 0x00;
	irq_raise(sp->irq_vector);
	AZ(pthread_mutex_unlock(&sp->mtx));
}

/**********************************************************************/

void v_matchproto_(mem_pre_read)
scsi_d_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	if (debug) return;
	assert(width == 1);
	scsi_ctrl_pre_read(scsi_d, space, adr);
}

void v_matchproto_(mem_post_write)
scsi_d_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	if (debug) return;
	assert(width == 1);
	scsi_ctrl_post_write(scsi_d, space, adr);
}

void
ioc_scsi_d_init(void)
{
	scsi_d->name = "SCSI_D";
	scsi_d->utrace = UT_SCSI_D;
	scsi_d->irq_vector = &IRQ_SCSI_D;
	AZ(pthread_mutex_init(&scsi_d->mtx, NULL));
	AZ(pthread_cond_init(&scsi_d->cond, NULL));
	AZ(pthread_create(&scsi_d->thr, NULL, scsi_thread, scsi_d));
}

/**********************************************************************/

void v_matchproto_(mem_pre_read)
scsi_t_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	if (debug) return;
	assert(width == 1);
	scsi_ctrl_pre_read(scsi_t, space, adr);
}

void v_matchproto_(mem_post_write)
scsi_t_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	if (debug) return;
	assert(width == 1);
	scsi_ctrl_post_write(scsi_t, space, adr);
}

void
ioc_scsi_t_init(void)
{
	scsi_t->name = "SCSI_T";
	scsi_t->utrace = UT_SCSI_T;
	scsi_t->irq_vector = &IRQ_SCSI_T;
	AZ(pthread_mutex_init(&scsi_t->mtx, NULL));
	AZ(pthread_cond_init(&scsi_t->cond, NULL));
	AZ(pthread_create(&scsi_t->thr, NULL, scsi_thread, scsi_t));
}

/**********************************************************************/

void v_matchproto_(mem_post_write)
resha_misc_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	unsigned u;

	if (debug) return;
	assert(width == 2);

	u = vbe16dec(space + adr);
	Trace(trace_ioc_io, "SCSI_DMA W [%x] <- %x/%d", adr, u, width);
	switch (adr) {
	case 0x0: scsi_d->dma_adr = u; break;
	case 0x4: scsi_t->dma_adr = u; break;
	case 0x8: scsi_d->dma_seg = u; break;
	case 0xc: scsi_t->dma_seg = u; break;
	default: break;
	}
}

void v_matchproto_(mem_post_write)
scsi_ctl_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	struct scsi *sp = NULL;

	if (debug) return;
	assert(width == 2);

	Trace(trace_ioc_io, "SCSI_CTL W [%x] <- %x/%d",
	    adr, vbe16dec(space+adr), width);

	if (adr == 0) {
		sp = scsi_d;
		if (sp->reset && !(space[adr + 1] & 0x1)) {
			Trace(trace_scsi_cmd, "SCSI_CTL %s RESET", sp->name);
			irq_lower(sp->irq_vector);
			callout_callback(scsi_ctrl_reset, sp, 5000, 0);
		}
		sp->reset = space[adr + 1] & 0x1;
	}
	if (adr == 8) {
		sp = scsi_t;
		if (sp->reset && !(space[adr + 1] & 0x10)) {
			Trace(trace_scsi_cmd, "SCSI_CTL %s RESET", sp->name);
			irq_lower(sp->irq_vector);
			callout_callback(scsi_ctrl_reset, sp, 5000, 0);
		}
		sp->reset = space[adr + 1] & 0x10;
	}
}

void v_matchproto_(mem_pre_read)
scsi_ctl_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	if (debug) return;

	space[1] |= 0x80;	// WRITE ENABLE SWITCH

	// This is not on RESHA schematics, but
	//    "RESHA TAPE SCSI sub-tests ..."
	// fails at 0x000713a8 without it
	space[1] &= 0x8f;
	space[1] |= space[9] & 0x70;

	Trace(trace_ioc_io, "SCSI_CTL R [%x] -> %x/%d",
	    adr, vbe16dec(space+adr), width);
}
