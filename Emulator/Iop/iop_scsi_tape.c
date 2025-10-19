
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Iop/iop_scsi.h"
#include "Infra/vend.h"
#include "Infra/vqueue.h"

/**********************************************************************
 * SIMH-TAPFILE index structures
 */

VTAILQ_HEAD(tape_recs_head, tape_recs);
VTAILQ_HEAD(tape_file_head, tape_file);

struct tape_recs {
	VTAILQ_ENTRY(tape_recs)		next;
	off_t				offset;
	uint32_t			reclen;
	uint32_t			n_rec;
};

struct tape_file {
	VTAILQ_ENTRY(tape_file)		next;
	off_t				offset;
	uint32_t			n_rec;
	struct tape_recs_head		list;
};

struct tape {
	struct tape_file_head		list;
	off_t				extent;
};

static struct tape_recs *
tape_recs_new(void)
{
	struct tape_recs *retval;

	retval = calloc(sizeof *retval, 1);
	return (retval);
}

static struct tape_file *
tape_file_new(void)
{
	struct tape_file *retval;

	retval = calloc(sizeof *retval, 1);
	AN(retval);
	VTAILQ_INIT(&retval->list);
	struct tape_recs *tr = tape_recs_new();
	VTAILQ_INSERT_TAIL(&retval->list, tr, next);
	return (retval);
}

static struct tape *
tape_new(void)
{
	struct tape *retval;

	retval = calloc(sizeof *retval, 1);
	AN(retval);
	VTAILQ_INIT(&retval->list);
	struct tape_file *tf = tape_file_new();
	VTAILQ_INSERT_TAIL(&retval->list, tf, next);
	return (retval);
}

static void
tape_add_tape_mark(struct tape *tp, off_t off)
{
	if (off <= tp->extent)
		return;
	tp->extent = off;
	struct tape_file *tf = tape_file_new();
	tf->offset = off;
	VTAILQ_INSERT_TAIL(&tp->list, tf, next);
}

static void
tape_add_record(struct tape *tp, uint32_t len, off_t off)
{
	if (off <= tp->extent)
		return;
	tp->extent = off;
	struct tape_file *tf = VTAILQ_LAST(&tp->list, tape_file_head);
	tf->n_rec++;
	struct tape_recs *tr = VTAILQ_LAST(&tf->list, tape_recs_head);
	if (tr->n_rec > 0 && len != tr->reclen) {
		tr = tape_recs_new();
		VTAILQ_INSERT_TAIL(&tf->list, tr, next);
	}
	if (tr->n_rec == 0) {
		tr->reclen = len;
		tr->offset = off;
	}
	tr->n_rec++;
}

static void v_matchproto_(cli_func_f)
cli_scsi_tape_layout(struct cli *cli)
{
	struct scsi_dev *sd;

	if (cli->help) {
		Cli_Usage(cli, "",
		    "Print file/record layout of mounted tape");
		return;
	}

	sd = get_scsi_dev(1, 0, 0);
	AN(sd);

	struct tape *tp = sd->tape;
	AN(tp);

	Cli_Printf(cli, "TP extent=0x%08jx\n", (uintmax_t)tp->extent);

	struct tape_file *tf;
	VTAILQ_FOREACH(tf, &tp->list, next) {
		Cli_Printf(cli, "TF off=0x%08jx n_rec=0x%08x\n",
                    (uintmax_t)tf->offset, tf->n_rec);
		if (!tf->n_rec)
			continue;
		struct tape_recs *tr;
		VTAILQ_FOREACH(tr, &tf->list, next) {
			Cli_Printf(cli,
			    "TR off=0x%08jx reclen=0x%08x n_rec=0x%08x\n",
			    (uintmax_t)tr->offset, tr->reclen, tr->n_rec);
		}
	}
}

/**********************************************************************/

#define MSG_FMT "0x%x:0x%x @0x%zx "
#define MSG_ARG dev->tape_fileno, dev->tape_recno, dev->tape_head

static int v_matchproto_(scsi_func_f)
scsi_00_test_unit_ready(struct scsi_dev *dev, uint8_t *cdb)
{
	
	(void)cdb;
	bprintf(dev->msg, MSG_FMT, MSG_ARG);
	if (dev->fd < 0) {
		dev->req_sense[2] |= 0x02; // Not Ready
		dev->req_sense[12] = 0x04; // ASQ = LU Not Ready
		dev->req_sense[13] = 0x00; // ASQQ = Volume not mounted
		dev->req_sense[19] |= 0x02; // Tape Not Present
		return (IOC_SCSI_OK);
	} else {
		return (IOC_SCSI_OK);
	}
}

static int v_matchproto_(scsi_func_f)
scsi_01_rewind(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	bprintf(dev->msg, MSG_FMT, MSG_ARG);
	dev->tape_head = 0;
	dev->tape_fileno = 0;
	dev->tape_recno = 0;
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_08_read_6_tape(struct scsi_dev *dev, uint8_t *cdb)
{
	unsigned tape_length, xfer_length;

	if (!(dev->ctl->regs[0x12] + dev->ctl->regs[0x13] + dev->ctl->regs[0x14]))
		return (IOC_SCSI_OK);
	xfer_length = vbe32dec(cdb + 1) & 0xffffff;
	tape_length = vle32dec(dev->map + dev->tape_head);
	bprintf(dev->msg, MSG_FMT "x=0x%x t=0x%x",
            MSG_ARG, xfer_length, tape_length);
	if (tape_length == 0) {
		tape_add_tape_mark(dev->tape, dev->tape_head);
		dev->ctl->regs[0x0f] |= 0x02;		// Check Condition
		strcat(dev->msg, " TAPE-MARK");
		dev->tape_head += 4;
		dev->req_sense[2] |= 0x80;
		vbe32enc(&dev->req_sense[3], xfer_length);
		dev->tape_recno = 0;
		dev->tape_fileno++;
		return (IOC_SCSI_OK);
	}
	if (tape_length == 0xffffffff) {
		strcat(dev->msg, " EOT");
		dev->req_sense[2] = 0x40;
		vbe32enc(&dev->req_sense[3], xfer_length);
		return (IOC_SCSI_ERROR);
	}
	assert(tape_length < 65535);

	tape_add_record(dev->tape, tape_length, dev->tape_head);

	assert(tape_length <= xfer_length);
	dev->tape_head += 4;

	scsi_fm_target(dev, dev->map + dev->tape_head, tape_length);

	TraceDump(trace_tape_data,
	    dev->map + dev->tape_head, tape_length,
	    "READ TAPE ID=%d [0x%x] (@0x%08zx)\n",
	    dev->scsi_id, tape_length, dev->tape_head);

	dev->tape_head += tape_length;
	if (tape_length & 1)
		dev->tape_head += 1;
	assert(tape_length == vle32dec(dev->map + dev->tape_head));
	dev->tape_head += 4;

	dev->tape_recno++;

	if (tape_length != xfer_length) {
		dev->ctl->regs[0x0f] |= 0x02;		// Check Condition
		dev->req_sense[2] = 0x20;		// ILI
		vbe32enc(&dev->req_sense[3], xfer_length - tape_length);
	}

	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_0a_write_6_tape(struct scsi_dev *dev, uint8_t *cdb)
{
	unsigned xfer_length;

	if (!(dev->ctl->regs[0x12] + dev->ctl->regs[0x13] + dev->ctl->regs[0x14]))
		return (IOC_SCSI_OK);

	xfer_length = vbe32dec(cdb + 1) & 0xffffff;
	tape_add_record(dev->tape, xfer_length, dev->tape_head);
	bprintf(dev->msg, MSG_FMT "x=0x%x",
            MSG_ARG, xfer_length);

	vle32enc(dev->map + dev->tape_head, xfer_length);
	dev->tape_head += 4;
	scsi_to_target(dev, dev->map + dev->tape_head, xfer_length);

	TraceDump(trace_tape_data,
	    dev->map + dev->tape_head, xfer_length,
	    "WRITE TAPE ID=%d BLKSZ=%08x (@0x%08zx)\n",
	    dev->scsi_id, xfer_length, dev->tape_head);

	dev->tape_head += xfer_length;
	if (xfer_length & 1)
		dev->tape_head += 1;
	vle32enc(dev->map + dev->tape_head, xfer_length);
	dev->tape_head += 4;

	/* Write a end of tape mark, but dont advance */
	vle32enc(dev->map + dev->tape_head, 0xffffffff);

	dev->tape_recno++;

	Trace(trace_scsi_data, "SCSI_T WRITE6 %x", xfer_length);
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_10_write_filemarks_tape(struct scsi_dev *dev, uint8_t *cdb)
{
	unsigned xfer_length;

	tape_add_tape_mark(dev->tape, dev->tape_head);
	xfer_length = vbe32dec(cdb + 1) & 0xffffff;

	bprintf(dev->msg, MSG_FMT "x=0x%x", MSG_ARG, xfer_length);

	vle32enc(dev->map + dev->tape_head, 0);
	dev->tape_head += 4;

	dev->tape_recno = 0;
	dev->tape_fileno++;

	/* Write a end of tape mark, but dont advance */
	vle32enc(dev->map + dev->tape_head, 0xffffffff);

	return (IOC_SCSI_OK);
}

static void
tape_space_block_forward(struct scsi_dev *dev)
{
	uint32_t tape_length, chk;

	tape_length = vle32dec(dev->map + dev->tape_head);
	assert(tape_length > 0 && tape_length < 0xff000000);
	dev->tape_head += 4;
	dev->tape_head += tape_length;
	if (tape_length & 1)
		dev->tape_head += 1;
	chk = vle32dec(dev->map + dev->tape_head);
	assert(tape_length == chk);
	dev->tape_head += 4;
	dev->tape_recno++;
}

static void
tape_space_block_backward(struct scsi_dev *dev)
{
	uint32_t tape_length, u;

	tape_length = vle32dec(dev->map + dev->tape_head - 4);
	assert(tape_length > 0);
	dev->tape_head -= 4;
	dev->tape_head -= tape_length;
	if (tape_length & 1)
		dev->tape_head -= 1;
	u = vle32dec(dev->map + dev->tape_head - 4);
	assert(tape_length == u);
	dev->tape_head -= 4;
	dev->tape_recno--;
}


static int v_matchproto_(scsi_func_f)
scsi_11_space(struct scsi_dev *dev, uint8_t *cdb)
{
	int32_t xfer_length;
	uint32_t tape_length;
	int retval = IOC_SCSI_OK;

	xfer_length = vbe32dec(cdb + 1) & 0xffffff;
	if (xfer_length & 0x800000)
		xfer_length -= 0x1000000;

        unsigned m = cdb[0x01] & 3;

	bprintf(dev->msg, MSG_FMT "m=%d x=%d", MSG_ARG, m, xfer_length);

	Trace(*dev->ctl->tracer, "SCSI_T_SPACE m=%u xfer_length=%d tape_head=0x%x P=%08x N=%08x\n", m, xfer_length, (int32_t)dev->tape_head, vle32dec(dev->map + dev->tape_head -4), vle32dec(dev->map + dev->tape_head));

	if (m == 0 && xfer_length < 0) {
		while (xfer_length < 0) {
			tape_length = vle32dec(dev->map + dev->tape_head - 4);
                        if (tape_length == 0)
				break;
			assert(tape_length > 0 && tape_length < 0xff000000);
			tape_space_block_backward(dev);
			xfer_length++;
		}
	} else if (m == 0 && xfer_length > 0) {
		while (xfer_length > 0) {
			tape_length = vle32dec(dev->map + dev->tape_head);
			assert(tape_length > 0 && tape_length < 0xff000000);
			tape_space_block_forward(dev);
			xfer_length--;
		}
	} else if (m == 1 && xfer_length < 0) {
		while (xfer_length < 0 && dev->tape_head > 0) {
			tape_length = vle32dec(dev->map + dev->tape_head - 4);
			assert(tape_length < 0xff000000);
			if (tape_length > 0) {
				tape_space_block_backward(dev);
				continue;
			}
			dev->tape_head -= 4;
			dev->tape_fileno--;
			xfer_length++;
		}
		if (xfer_length) {
			dev->req_sense[2] |= 0x40;		// EOM
			dev->req_sense[19] |= 0x01;		// LBOT
			dev->tape_fileno = 0;
			dev->tape_head = 0;
		}
		dev->tape_recno = 0;
	} else if (m == 1 && xfer_length > 0) {
		while (xfer_length > 0) {
			tape_length = vle32dec(dev->map + dev->tape_head);
			assert(tape_length < 0xff000000);
			if (tape_length > 0) {
				tape_space_block_forward(dev);
				continue;
			}
			dev->tape_head += 4;
			dev->tape_fileno++;
			dev->tape_recno = 0;
			xfer_length--;
		}
	} else if (m > 1) {
		printf("BAD TAPE SPACE 0x%x %d\n", cdb[0x01], xfer_length);
	}

	if (xfer_length) {
		sprintf(strchr(dev->msg, '\0'), " residual=%d", xfer_length);
		retval = IOC_SCSI_ERROR;
	}

	vbe32enc(&dev->req_sense[3], xfer_length);

	return (retval);
}

void
scsi_tape_configure(void)
{
	struct scsi_dev *sd;

	sd = get_scsi_dev(1, 0, 1);

	sd->funcs[SCSI_TEST_UNIT_READY] = scsi_00_test_unit_ready;
	sd->funcs[SCSI_REWIND] = scsi_01_rewind;
	sd->funcs[SCSI_REQUEST_SENSE] = scsi_03_request_sense;
	sd->funcs[SCSI_READ_6] = scsi_08_read_6_tape;
	sd->funcs[SCSI_WRITE_6] = scsi_0a_write_6_tape;
	sd->funcs[SCSI_WRITE_FILEMARKS] = scsi_10_write_filemarks_tape;
	sd->funcs[SCSI_UNLOAD] = scsi_xx_no_op;
	sd->funcs[SCSI_SPACE] = scsi_11_space;

	sd->is_tape = 1;
}

static void v_matchproto_(cli_func_f)
cli_scsi_tape_mount(struct cli *cli)
{
	struct scsi_dev *sd;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<filename>",
		    "Mount filename in SCSI tape drive.");
		return;
	}

	cli->ac--;
	cli->av++;

	sd = get_scsi_dev(1, 0, 0);
	AN(sd);

	if (cli_scsi_dev_map_file(cli, sd, cli->av[0]) < 0)
		return;

	sd->tape = tape_new();
	cli->ac--;
	cli->av++;
}

static const struct cli_cmds cli_scsi_tape_cmds[] = {
	{ "mount",		cli_scsi_tape_mount },
	{ "layout",		cli_scsi_tape_layout },
	{ NULL,			NULL },
};

void v_matchproto_(cli_func_f)
cli_scsi_tape(struct cli *cli)
{
	Cli_Dispatch(cli, cli_scsi_tape_cmds);
}
