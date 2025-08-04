/*-
 * Largely written by Julian Elischer (julian@tfs.com)
 * for TRW Financial Systems.
 *
 * TRW Financial Systems, in accordance with their agreement with Carnegie
 * Mellon University, makes this software available to CMU to distribute
 * or use in any manner that they see fit as long as this message is kept with
 * the software. For this reason TFS also grants any other persons or
 * organisations permission to use or modify this software.
 *
 * TFS supplies this software to be publicly redistributed
 * on the understanding that TFS is not responsible for the correct
 * functioning of this software in any circumstances.
 *
 * Ported to run under 386BSD by Julian Elischer (julian@tfs.com) Sept 1992
 *
 * (Via FreeBSD's src/sys/cam/scsi/scsi_all.h)
 */

#define SCSI_CMD_TABLE \
	SCSI_CMD(TEST_UNIT_READY, 0x00) \
	SCSI_CMD(REWIND, 0x01) \
	SCSI_CMD(REQUEST_SENSE, 0x03) \
	SCSI_CMD(FORMAT_UNIT, 0x04) \
	SCSI_CMD(READ_6, 0x08) \
	SCSI_CMD(WRITE_6, 0x0A) \
	SCSI_CMD(SEEK, 0x0B) \
	SCSI_CMD(WRITE_FILEMARKS, 0x10) \
	SCSI_CMD(SPACE, 0x11) \
	SCSI_CMD(MODE_SELECT_6, 0x15) \
	SCSI_CMD(MODE_SENSE_6, 0x1A) \
	SCSI_CMD(UNLOAD, 0x1B) \
	SCSI_CMD(READ_10, 0x28) \
	SCSI_CMD(READ_DEFECT_DATA_10, 0x37) \
