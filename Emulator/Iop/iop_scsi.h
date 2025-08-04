
/*
 * This table is based on FreeBSD (src/sys/cam/scsi/scsi_all.h), which
 * again comes from code from 386BSD, which again was written by
 * Julian Elischer (julian@tfs.com) of TRW Financial Systems, which
 * again worked with Carnegie Mellon University about something.
 */

#define SCSI_CMD_TABLE(MACRO)			\
	MACRO(TEST_UNIT_READY,		0x00)	\
	MACRO(REWIND,			0x01)	\
	MACRO(REQUEST_SENSE,		0x03)	\
	MACRO(FORMAT_UNIT,		0x04)	\
	MACRO(READ_6,			0x08)	\
	MACRO(WRITE_6,			0x0A)	\
	MACRO(SEEK,			0x0B)	\
	MACRO(WRITE_FILEMARKS,		0x10)	\
	MACRO(SPACE,			0x11)	\
	MACRO(INQUIRY,			0x12)	\
	MACRO(MODE_SELECT_6,		0x15)	\
	MACRO(MODE_SENSE_6,		0x1A)	\
	MACRO(UNLOAD,			0x1B)	\
	MACRO(READ_10,			0x28)	\
	MACRO(READ_DEFECT_DATA_10,	0x37)	\

struct scsi_dev;
struct scsi;

typedef int scsi_func_f(struct scsi_dev *, uint8_t *cdb);
#define IOC_SCSI_OK		0
#define IOC_SCSI_ERROR		-1

struct scsi_dev {
	scsi_func_f		*funcs[256];
	struct scsi		*ctl;
	int			scsi_id;
	int			is_tape;
	uint8_t			req_sense[26];
	uint8_t			sense_3[36];
	uint8_t			sense_4[32];
	char			msg[256];

	int			fd;
	uint8_t			*map;
	size_t			map_size;

	unsigned		tape_fileno;
	unsigned		tape_recno;
	size_t			tape_head;
};

struct scsi {
	const char		*name;
	struct irq_vector	*irq_vector;
	pthread_mutex_t		mtx;
	pthread_cond_t		cond;
	pthread_t		thr;
	uint8_t			regs[32];
	unsigned int		dma_seg;
	unsigned int		dma_adr;
	struct scsi_dev		*dev[7];
	unsigned		reset;
	int			*tracer;
};

void trace_scsi_dev(struct scsi_dev *dev, const char *cmt);
void trace_scsi_dev_tape(struct scsi_dev *dev, const char *cmt);
void scsi_to_target(struct scsi_dev *, void *ptr, unsigned len);
void scsi_fm_target(struct scsi_dev *, void *ptr, unsigned len);

void *scsi_disk_pointer_to_sector(unsigned unit, unsigned lba);

struct scsi_dev* get_scsi_dev(int tape, unsigned unit, int create);

enum SCSI_COMMANDS {
	#define M_ENUM(name, number) SCSI_##name = number,
	SCSI_CMD_TABLE(M_ENUM)
	#undef M_ENUM
};

scsi_func_f scsi_00_test_unit_ready;
scsi_func_f scsi_03_request_sense;

int cli_scsi_dev_map_file(struct cli *cli, struct scsi_dev *dev, const char *fn);

