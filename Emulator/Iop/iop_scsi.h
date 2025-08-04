
#include "Iop/iop_scsi_cmds.h"

struct scsi_dev;
struct scsi;

typedef int scsi_func_f(struct scsi_dev *, uint8_t *cdb);
#define IOC_SCSI_OK		0
#define IOC_SCSI_ERROR		-1

struct scsi_dev {
	scsi_func_f		* const * funcs;
	struct scsi		*ctl;
	int			scsi_id;
	int			is_tape;
	uint8_t			req_sense[26];
	uint8_t			sense_3[36];
	uint8_t			sense_4[32];
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
};

void trace_scsi_dev(struct scsi_dev *dev, const char *cmt);
void trace_scsi_dev_tape(struct scsi_dev *dev, const char *cmt);
void scsi_to_target(struct scsi_dev *, void *ptr, unsigned len);
void scsi_fm_target(struct scsi_dev *, void *ptr, unsigned len);
extern struct scsi scsi_t[1];
extern struct scsi scsi_d[1];

#define SCSI_CMD(name, number) SCSI_##name = number,
enum SCSI_COMMANDS {
SCSI_CMD_TABLE
};
#undef SCSI_CMD
