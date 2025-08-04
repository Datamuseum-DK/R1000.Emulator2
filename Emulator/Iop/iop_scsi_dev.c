#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"
#include "Iop/iop_scsi.h"
#include "Infra/vend.h"

/**********************************************************************/

#ifndef MAP_NOSYNC
#    define MAP_NOSYNC 0
#endif

static int
cli_scsi_dev_map_file(struct cli *cli, struct scsi_dev *dev, const char *fn)
{
	struct stat st[1];
	void *ptr;

	AN(cli);
	AN(dev);
	AN(fn);

	int rw = *fn == '+';
	if (rw) {
		fn++;
	}

	dev->fd = open(fn, rw ? O_RDWR : O_RDONLY);
	if (dev->fd < 0) {
		Cli_Error(cli, "Cannot open %s: (%s)\n", fn, strerror(errno));
		return (-1);
	}
	AZ(fstat(dev->fd, st));
	if (!S_ISREG(st->st_mode)) {
		Cli_Error(cli, "Not a regular file: %s\n", fn);
		AZ(close(dev->fd));
		dev->fd = -1;
		return (-1);
	}
	dev->map_size = st->st_size;
	ptr = mmap(
	    NULL,
	    dev->map_size,
	    PROT_READ|PROT_WRITE,
	    rw ? (MAP_SHARED | MAP_NOSYNC) : (MAP_PRIVATE | MAP_NOSYNC),
	    dev->fd,
	    0
	);
	if (ptr == MAP_FAILED) {
		Cli_Error(cli,
		    "Could not mmap(2): %s (%s)\n", fn, strerror(errno));
		AZ(close(dev->fd));
		dev->fd = -1;
		return (-1);
	}
	dev->map = ptr;
	return (0);
}

/**********************************************************************/

static int v_matchproto_(scsi_func_f)
scsi_00_test_unit_ready(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	trace_scsi_dev(dev, "TEST_UNIT_READY");
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_03_request_sense(struct scsi_dev *dev, uint8_t *cdb)
{

	trace_scsi_dev(dev, "REQUEST_SENSE");
	assert(cdb[4] >= sizeof dev->req_sense);
	TraceDump(*dev->ctl->tracer,
	    dev->req_sense, sizeof dev->req_sense,
	    "%s %u REQUEST SENSE ",
	    dev->ctl->name, dev->scsi_id);
	scsi_fm_target(dev, dev->req_sense, sizeof dev->req_sense);
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_04_format_unit(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	trace_scsi_dev(dev, "FORMAT_UNIT");
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_08_read_6_disk(struct scsi_dev *dev, uint8_t *cdb)
{
	size_t lba;
	size_t nsect;

	trace_scsi_dev(dev, "READ_6(DISK)");

	lba = vbe32dec(cdb) & 0x1fffff;
	nsect = cdb[0x04];

	TraceDump(trace_disk_data,
	    dev->map + (lba << 10), nsect << 10,
	    "READ DISK ID=%d LBA=%08zx (@0x%08zx)\n",
	    dev->scsi_id, lba, lba << 10);

	scsi_fm_target(dev, dev->map + (lba<<10), nsect<<10);
	Trace(trace_scsi_data, "SCSI_D READ6 %zx (%08zx)", lba, lba << 10);
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_0a_write_6(struct scsi_dev *dev, uint8_t *cdb)
{
	size_t lba;
	size_t nsect;

	trace_scsi_dev(dev, "WRITE_6");

	lba = vbe32dec(cdb) & 0x1fffff;
	nsect = cdb[0x04];

	scsi_to_target(dev, dev->map + (lba<<10), nsect<<10);

	TraceDump(trace_disk_data,
	    dev->map + (lba << 10), nsect << 10,
	    "WRITE DISK ID=%d LBA=%08zx (@0x%08zx)\n",
	    dev->scsi_id, lba, lba << 10);

	Trace(trace_scsi_data, "SCSI_D WRITE6 %zx", lba);
	return (IOC_SCSI_OK);
}


static int v_matchproto_(scsi_func_f)
scsi_0b_seek(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	trace_scsi_dev(dev, "SEEK");

	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_0d_vendor(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	trace_scsi_dev(dev, "VENDOR");
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_15_mode_select_6(struct scsi_dev *dev, uint8_t *cdb)
{

	uint8_t buf[BUFSIZ];

	trace_scsi_dev(dev, "MODE_SELECT_6");
	assert(cdb[0x01] == 0x11);
	assert(cdb[0x02] == 0x00);
	assert(cdb[0x03] == 0x00);

	scsi_to_target(dev, buf, cdb[0x04]);

	dev->req_sense[2] = 0;
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_1a_sense(struct scsi_dev *dev, uint8_t *cdb)
{

	trace_scsi_dev(dev, "MODE SENSE");

	switch(cdb[0x02]) {
	case 0x03:
		scsi_fm_target(dev, dev->sense_3, sizeof dev->sense_3);
		break;
	case 0x04:
		scsi_fm_target(dev, dev->sense_4, sizeof dev->sense_4);
		break;
	default:
		Trace(trace_scsi_data, "MODE_SENSE page 0x%d unknown", cdb[0x02]);
		return (IOC_SCSI_ERROR);
	}
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_1b_unload_tape(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	trace_scsi_dev_tape(dev, "UNLOAD(TAPE)");
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_28_read_10(struct scsi_dev *dev, uint8_t *cdb)
{
	size_t lba;
	unsigned nsect;

	trace_scsi_dev(dev, "READ_10");

	lba = vbe32dec(cdb + 0x02);

	nsect = cdb[0x07] << 8;
	nsect |= cdb[0x08];

	scsi_fm_target(dev, dev->map + (lba<<10), nsect<<10);
	Trace(trace_scsi_data, "SCSI_D READ10 %zx", lba);
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_37_read_defect_data_10(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	trace_scsi_dev(dev, "READ_DEFECT_DATA_10");

	// scsi_fm_target(dev, dev->map + (lba<<10), nsect<<10);
	return (IOC_SCSI_OK);
}

/**********************************************************************/

static struct scsi_dev *
cli_scsi_get_disk(struct cli *cli, int create)
{
	struct scsi_dev *sd;
	unsigned unit;

	unit = atoi(cli->av[0]);
	cli->ac--;
	cli->av++;
	if (unit > 3) {
		Cli_Error(cli, "Only disks 0-3 supported\n");
		return(NULL);
	}
	sd = get_scsi_dev(0, unit, create);

	if (!create) {
		if (sd == NULL)
			Cli_Error(cli, "Disks not mounted\n");
		return(sd);
	}

	sd->req_sense[0] = 0x80;
	sd->req_sense[7] = 0x12;

	sd->funcs[SCSI_TEST_UNIT_READY] = scsi_00_test_unit_ready;
	sd->funcs[SCSI_FORMAT_UNIT] = scsi_04_format_unit;
	sd->funcs[SCSI_READ_6] = scsi_08_read_6_disk;
	sd->funcs[SCSI_WRITE_6] = scsi_0a_write_6;
	sd->funcs[SCSI_SEEK] = scsi_0b_seek;
	sd->funcs[0x0d] = scsi_0d_vendor;
	sd->funcs[SCSI_MODE_SENSE_6] = scsi_1a_sense;
	sd->funcs[SCSI_READ_10] = scsi_28_read_10;
	sd->funcs[SCSI_MODE_SELECT_6] = scsi_15_mode_select_6;
	sd->funcs[SCSI_READ_DEFECT_DATA_10] = scsi_37_read_defect_data_10;

	return (sd);
}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_scsi_disk_mount(struct cli *cli)
{
	struct scsi_dev *sd;

	if (cli->help || cli->ac != 3) {
		Cli_Usage(cli, "<unit> <filename>",
		    "Load filename in SCSI disk unit.");
		return;
	}
	cli->ac--;
	cli->av++;

	sd = cli_scsi_get_disk(cli, 1);
	AN(sd);

	if (cli_scsi_dev_map_file(cli, sd, cli->av[0]) < 0)
		return;

	vbe16enc(sd->sense_3 + 0x0c, 0x8316);
	vbe16enc(sd->sense_4 + 0x0c, 0x8412);

	if (sd->map_size == 1143936000UL || sd->map_size == 1146009600UL) {
		// FUJITSU M2266
		vbe16enc(sd->sense_3 + 0x0e, 15);	// tracks/zone
		vbe16enc(sd->sense_3 + 0x14, 45);	// alt sec/lu
		vbe16enc(sd->sense_3 + 0x16, 45);	// sec/track
		vbe16enc(sd->sense_3 + 0x18, 1 << 10);	// sector size
		vbe16enc(sd->sense_3 + 0x1a, 1);	// interleave
		vbe16enc(sd->sense_3 + 0x1c, 5);	// track skew
		vbe16enc(sd->sense_3 + 0x1e, 11);	// cyl skew
		sd->sense_3[0x20] = 0x40;		// flags: HSEC

		vbe16enc(sd->sense_4 + 0x0f, 1658);	// cyl
		sd->sense_4[0x11] = 0x0f;		// nheads
	} else if (sd->map_size == 1115258880UL) {
		// SEAGATE ST41200 "WREN VII"
		vbe16enc(sd->sense_3 + 0x0e, 15);	// tracks/zone
		vbe16enc(sd->sense_3 + 0x14, 45);	// alt sec/lu
		vbe16enc(sd->sense_3 + 0x16, 38);	// sec/track
		vbe16enc(sd->sense_3 + 0x18, 1 << 10);	// sector size
		vbe16enc(sd->sense_3 + 0x1a, 1);	// interleave
		vbe16enc(sd->sense_3 + 0x1c, 3);	// track skew
		vbe16enc(sd->sense_3 + 0x1e, 12);	// cyl skew
		sd->sense_3[0x20] = 0x40;		// flags: HSEC

		vbe16enc(sd->sense_4 + 0x0f, 1931);	// cyl
		sd->sense_4[0x11] = 0x0f;		// nheads
	} else {
		Cli_Error(cli, "Unknown disk geometry\n");
		return;
	}

	cli->ac--;
	cli->av++;
}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_scsi_disk_patch(struct cli *cli)
{
	unsigned offset, val;
	struct scsi_dev *sd;
	int i;
	char *err;

	if (cli->help || cli->ac != 3) {
		Cli_Usage(cli, "<unit> <offset> <byte>…",
		    "Patch bytes in disk-image");
		return;
	}
	cli->ac--;
	cli->av++;

	sd = cli_scsi_get_disk(cli, 0);
	if (sd == NULL)
		return;

	err = NULL;
	offset = strtoul(cli->av[0], &err, 0);
	if (err != NULL && *err != '\0') {
		Cli_Error(cli, "Cannot grog <offset>");
		return;
	}

	for (i = 1; cli->av[i] != NULL; i++) {
		if (offset >= sd->map_size) {
			Cli_Error(cli, "<offset> past end of disk-image.");
			return;
		}
		err = NULL;
		val = strtoul(cli->av[i], &err, 0);
		if ((err != NULL && *err != '\0') || val > 255) {
			Cli_Error(cli, "Cannot grog <byte> (%s)", cli->av[i]);
			return;
		}
		sd->map[offset++] = val;
	}
}


static const struct cli_cmds cli_scsi_disk_cmds[] = {
	{ "mount",		cli_scsi_disk_mount },
	{ "patch",		cli_scsi_disk_patch },
	{ NULL,			NULL },
};

void v_matchproto_(cli_func_f)
cli_scsi_disk(struct cli *cli)
{
	Cli_Dispatch(cli, cli_scsi_disk_cmds);
}

/**********************************************************************/

#define MSG_FMT "0x%x:0x%x @0x%zx "
#define MSG_ARG dev->tape_fileno, dev->tape_recno, dev->tape_head

static int v_matchproto_(scsi_func_f)
scsi_01_rewind(struct scsi_dev *dev, uint8_t *cdb)
{

	(void)cdb;
	bprintf(dev->msg, MSG_FMT, MSG_ARG);
	trace_scsi_dev_tape(dev, "REWIND");
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
		strcat(dev->msg, " TAPE-MARK");
		dev->tape_head += 4;
		dev->req_sense[2] = 0x80;
		dev->req_sense[3] = xfer_length >> 8;
		dev->req_sense[4] = xfer_length & 0xff;
		dev->tape_recno = 0;
		dev->tape_fileno++;
		return (-1);
	}
	if (tape_length == 0xffffffff) {
		strcat(dev->msg, " EOT");
		dev->req_sense[2] = 0x40;
		return (-1);
	}
	dev->req_sense[2] = 0;
	assert(tape_length < 65535);
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
	if (tape_length < xfer_length)
		return (xfer_length - tape_length);

	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_0a_write_6_tape(struct scsi_dev *dev, uint8_t *cdb)
{
	unsigned xfer_length;

	if (!(dev->ctl->regs[0x12] + dev->ctl->regs[0x13] + dev->ctl->regs[0x14]))
		return (IOC_SCSI_OK);

	xfer_length = vbe32dec(cdb + 1) & 0xffffff;
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

	trace_scsi_dev_tape(dev, "WRITE_FILEMARK(TAPE)");

	if (!(dev->ctl->regs[0x12] + dev->ctl->regs[0x13] + dev->ctl->regs[0x14]))
		return (IOC_SCSI_OK);

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

	xfer_length = vbe32dec(cdb + 1) & 0xffffff;
	if (xfer_length & 0x800000)
		xfer_length -= 0x1000000;

	bprintf(dev->msg, MSG_FMT "m=%d x=%d", MSG_ARG, cdb[0x01], xfer_length);

	trace_scsi_dev_tape(dev, "SPACE(TAPE)");

	if (cdb[0x01] == 0 && xfer_length < 0) {
		while (xfer_length < 0) {
			tape_length = vle32dec(dev->map + dev->tape_head - 4);
			assert(tape_length > 0 && tape_length < 0xff000000);
			tape_space_block_backward(dev);
			xfer_length++;
		}
	} else if (cdb[0x01] == 0 && xfer_length > 0) {
		while (xfer_length > 0) {
			tape_length = vle32dec(dev->map + dev->tape_head);
			assert(tape_length > 0 && tape_length < 0xff000000);
			tape_space_block_forward(dev);
			xfer_length--;
		}
	} else if (cdb[0x01] == 1 && xfer_length < 0) {
		printf("BSF %d\n", xfer_length);
		if (0 && xfer_length == -49) {
			//xfer_length = -38;	/* 0:0 */
			// xfer_length = -37;	/* 1:0 (tape_length <= xfer_length) */
			// xfer_length = -36;	/* 2:0 */

			xfer_length = -35;	/* 3:0 */
			// xfer_length = -34;	/* 4:0 (tape_length <= xfer_length) */
			// xfer_length = -33;	/* 5:0 */

			//xfer_length = -32;	/* 6:0 */

			// xfer_length = -29;	/* 9:0 */

			// xfer_length = -26;	/* 12:0 */
		}
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
		if (dev->tape_head > 0) {
			//dev->tape_head += 4;
			//dev->tape_fileno++;
		} else {
			if (dev->tape_fileno)
				printf("TAPE: Wrong fileno after space BOT %d\n", dev->tape_fileno);
			dev->tape_head = 0;
			dev->tape_fileno = 0;
		}
		dev->tape_recno = 0;
	} else if (cdb[0x01] == 1 && xfer_length > 0) {
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
	} else {
		printf("BAD TAPE SPACE 0x%x %d\n", cdb[0x01], xfer_length);
		assert(0);
	}
	xfer_length = vbe32dec(cdb + 1) & 0xffffff;
	if (xfer_length & 0x800000)
		xfer_length -= 0x1000000;

printf("POST SPACE 0x%x/%d 0x%x:0x%x @0x%zx\n", cdb[0x01], xfer_length, dev->tape_fileno, dev->tape_recno, dev->tape_head);

	dev->req_sense[2] = 0;
	return (IOC_SCSI_OK);
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

	sd = get_scsi_dev(1, 0, 1);

	sd->req_sense[0] = 0xf0;
	sd->req_sense[7] = 0x12;

	sd->funcs[SCSI_TEST_UNIT_READY] = scsi_00_test_unit_ready;
	sd->funcs[SCSI_REWIND] = scsi_01_rewind;
	sd->funcs[SCSI_REQUEST_SENSE] = scsi_03_request_sense;
	sd->funcs[SCSI_READ_6] = scsi_08_read_6_tape;
	sd->funcs[SCSI_WRITE_6] = scsi_0a_write_6_tape;
	sd->funcs[SCSI_WRITE_FILEMARKS] = scsi_10_write_filemarks_tape;
	sd->funcs[SCSI_UNLOAD] = scsi_1b_unload_tape;
	sd->funcs[SCSI_SPACE] = scsi_11_space;

	sd->is_tape = 1;

	if (cli_scsi_dev_map_file(cli, sd, cli->av[0]) < 0)
		return;

	cli->ac--;
	cli->av++;
}

static const struct cli_cmds cli_scsi_tape_cmds[] = {
	{ "mount",		cli_scsi_tape_mount },
	{ NULL,			NULL },
};

void v_matchproto_(cli_func_f)
cli_scsi_tape(struct cli *cli)
{
	Cli_Dispatch(cli, cli_scsi_tape_cmds);
}
