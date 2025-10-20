#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#include "Infra/r1000.h"
#include "Infra/vqueue.h"

#include "Iop/iop.h"

typedef void ioc_sc_bus_callback_f(uint32_t data);

struct bus_xact {
	struct ioc_sc_bus_xact	xact[1];
	ioc_sc_bus_callback_f	*cb_func;
	int			is_done;
	VTAILQ_ENTRY(bus_xact)	list;
};

static VTAILQ_HEAD(, bus_xact) bus_xact_head =
    VTAILQ_HEAD_INITIALIZER(bus_xact_head);

static struct bus_xact *in_progress = NULL;

static pthread_mutex_t bus_xact_mtx;
static pthread_cond_t bus_xact_cond;

void
ioc_bus_xact_init(void)
{
	AZ(pthread_mutex_init(&bus_xact_mtx, NULL));
	AZ(pthread_cond_init(&bus_xact_cond, NULL));
}

static uint32_t
ioc_bus_xact_schedule_cb(uint8_t fc, uint32_t adr, uint32_t data, int width,
    int is_write, ioc_sc_bus_callback_f *cb_func)
{
	struct bus_xact *bxp;

	Trace(trace_ioc_sc, "IOC_SC %08x %08x %x %d %p", adr, data, width, is_write, cb_func);

	bxp = calloc(sizeof *bxp, 1);
	AN(bxp);
	bxp->xact->fc = fc;
	bxp->xact->address = adr;
	bxp->xact->data = data;
	bxp->xact->width = width;
	bxp->xact->is_write = is_write;
	bxp->xact->sc_state = is_write ? 100 : 200;
	bxp->cb_func = cb_func;
	AZ(pthread_mutex_lock(&bus_xact_mtx));
	VTAILQ_INSERT_TAIL(&bus_xact_head, bxp, list);
	while (cb_func == NULL && !bxp->is_done)
		AZ(pthread_cond_wait(&bus_xact_cond, &bus_xact_mtx));
	AZ(pthread_mutex_unlock(&bus_xact_mtx));
	if (cb_func == NULL) {
		data = bxp->xact->data;
		switch(bxp->xact->width) {
		case 1: data &= 0xff; break;
		case 2: data &= 0xffff; break;
		case 4: break;
		default: WRONG();
		}
		free(bxp);
	}
	return (data);
}

uint32_t
ioc_bus_xact_schedule(uint8_t fc, uint32_t adr, uint32_t data, int width, int is_write)
{
	return (ioc_bus_xact_schedule_cb(fc, adr, data, width, is_write, NULL));
}

struct ioc_sc_bus_xact *
ioc_sc_bus_get_xact(void)
{

	if (VTAILQ_EMPTY(&bus_xact_head))
		return(NULL);
	AZ(pthread_mutex_lock(&bus_xact_mtx));
	assert(in_progress == NULL);
	in_progress = VTAILQ_FIRST(&bus_xact_head);
	if (in_progress != NULL)
		VTAILQ_REMOVE(&bus_xact_head, in_progress, list);
	AZ(pthread_mutex_unlock(&bus_xact_mtx));
	if (in_progress != NULL)
		return (in_progress->xact);
	return (NULL);
}

void
ioc_sc_bus_done(struct ioc_sc_bus_xact **bxpa)
{
	struct bus_xact *bxp = NULL;

	AN(bxpa);
	AZ(pthread_mutex_lock(&bus_xact_mtx));
	assert(in_progress != NULL);
	assert(in_progress->xact == *bxpa);
	*bxpa = NULL;
	in_progress->is_done = 1;
	if (in_progress->cb_func == NULL) {
		AZ(pthread_cond_signal(&bus_xact_cond));
	} else {
		in_progress->cb_func(in_progress->xact->data);
		bxp = in_progress;
	}
	in_progress = NULL;
	AZ(pthread_mutex_unlock(&bus_xact_mtx));
	if (bxp != NULL)
		free(bxp);
}

void
ioc_sc_bus_start_iack(unsigned ipl_pins)
{

	Trace(trace_ioc_interrupt, "SC-IPL pins=%x", ipl_pins);
	if (ipl_pins == 6)
		irq_raise(&IRQ_REQUEST_FIFO);
	else
		irq_lower(&IRQ_REQUEST_FIFO);
}
