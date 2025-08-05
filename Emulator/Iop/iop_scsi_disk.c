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

int
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

int v_matchproto_(scsi_func_f)
scsi_03_request_sense(struct scsi_dev *dev, uint8_t *cdb)
{

	assert(cdb[4] >= sizeof dev->req_sense);
	TraceDump(*dev->ctl->tracer,
	    dev->req_sense, sizeof dev->req_sense,
	    "%s %u REQUEST SENSE ",
	    dev->ctl->name, dev->scsi_id);
	scsi_fm_target(dev, dev->req_sense, sizeof dev->req_sense);
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_08_read_6_disk(struct scsi_dev *dev, uint8_t *cdb)
{
	size_t lba;
	size_t nsect;

	lba = vbe32dec(cdb) & 0x1fffff;
	nsect = cdb[0x04];
	sprintf(dev->msg, "lba=0x%zx n=0x%zx", lba, nsect);

	TraceDump(trace_disk_data,
	    dev->map + (lba << 10), nsect << 10,
	    "READ DISK ID=%d LBA=%08zx (@0x%08zx)\n",
	    dev->scsi_id, lba, lba << 10);

	scsi_fm_target(dev, dev->map + (lba<<10), nsect<<10);
	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_0a_write_6(struct scsi_dev *dev, uint8_t *cdb)
{
	size_t lba;
	size_t nsect;

	lba = vbe32dec(cdb) & 0x1fffff;
	nsect = cdb[0x04];
	sprintf(dev->msg, "lba=0x%zx n=0x%zx", lba, nsect);

	scsi_to_target(dev, dev->map + (lba<<10), nsect<<10);

	TraceDump(trace_disk_data,
	    dev->map + (lba << 10), nsect << 10,
	    "WRITE DISK ID=%d LBA=%08zx (@0x%08zx)\n",
	    dev->scsi_id, lba, lba << 10);

	return (IOC_SCSI_OK);
}

static int v_matchproto_(scsi_func_f)
scsi_15_mode_select_6(struct scsi_dev *dev, uint8_t *cdb)
{

	uint8_t buf[BUFSIZ];

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
scsi_28_read_10(struct scsi_dev *dev, uint8_t *cdb)
{
	size_t lba;
	size_t nsect;

	lba = vbe32dec(cdb + 0x02);

	nsect = cdb[0x07] << 8;
	nsect |= cdb[0x08];
	sprintf(dev->msg, "lba=0x%zx n=0x%zx", lba, nsect);

	scsi_fm_target(dev, dev->map + (lba<<10), nsect<<10);
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

	sd->funcs[SCSI_TEST_UNIT_READY] = scsi_xx_no_op;
	sd->funcs[SCSI_FORMAT_UNIT] = scsi_xx_no_op;
	sd->funcs[SCSI_READ_6] = scsi_08_read_6_disk;
	sd->funcs[SCSI_WRITE_6] = scsi_0a_write_6;
	sd->funcs[SCSI_SEEK] = scsi_xx_no_op;
	sd->funcs[SCSI_VENDOR_0D] = scsi_xx_no_op;
	sd->funcs[SCSI_MODE_SENSE_6] = scsi_1a_sense;
	sd->funcs[SCSI_READ_10] = scsi_28_read_10;
	sd->funcs[SCSI_MODE_SELECT_6] = scsi_15_mode_select_6;
	sd->funcs[SCSI_READ_DEFECT_DATA_10] = scsi_xx_no_op;

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
