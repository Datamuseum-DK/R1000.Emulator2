#ifndef DIAG_DIAG_H
#define DIAG_DIAG_H

// See FS_0.M200 at 0x18479
#define BOARD_TABLE(macro) \
	macro(IOA, seq, 0) \
	macro(WIDGET, seq, 1) \
	macro(SEQ, seq, 2) \
	macro(FIU, fiu, 3) \
	macro(IOC, ioc, 4) \
	macro(ALL, any, 5) \
	macro(TYP, typ, 6) \
	macro(VAL, val, 7) \
	macro(ALLMEM, val, 8) \
	macro(FIUMEM, val, 9) \
	macro(TVSQ, val, 10) \
	macro(NOTMEM, val, 11) \
	macro(MEM0, mem0, 12) \
	macro(MEM1, mem1, 13) \
	macro(MEM2, mem2, 14) \
	macro(MEM3, mem3, 15)

// See FS_0.M200 at 0x18519
#define RESPONSE_TABLE(macro) \
	macro(1, DONE) \
	macro(2, LOOPING) \
	macro(3, PAUSED) \
	macro(4, ERROR) \
	macro(5, RESET) \
	macro(6, RUNNING) \
	macro(7, RESERVED1) \
	macro(8, RESERVED2) \
	macro(9, TIMEOUT)

#define CMD_TABLE(macro) \
	macro(STATUS, status, 0) \
	macro(UPLOAD, upload, 1) \
	macro(DISABLE, disable, 2) \
	macro(ENABLE, enable, 3) \
	macro(RESET, reset, 4) \
	macro(DOWNLOAD, download, 5) \
	macro(UNPAUSE, unpause, 6) \
	macro(UNLOOP, unloop, 7)

enum diproc_cmd {
#define MC_CMD(upper, lower, num) DIPROC_CMD_##upper = num,
CMD_TABLE(MC_CMD)
#undef MC_CMD
};

enum diproc_response {
#define MC_RESPONSE(num, name)	DIPROC_RESPONSE_##name = num,
RESPONSE_TABLE(MC_RESPONSE)
#undef MC_RESPONSE
};

struct elastic;
struct experiment;
extern struct elastic *diag_elastic;

struct diproc {
	const char		*upper;
	const char		*lower;
	int			address;
	volatile uint8_t	status;
	struct experiment	*experiment;
};

extern struct diproc diprocs[16];
void DiagBus_Send(const struct diproc *dp, unsigned u);
void DiagBus_Reply(const char *from, uint8_t msg);


struct diproc *diagbus_get_board(struct cli *cli, const char *);

struct experiment *Load_Experiment_File(struct cli *, const char *filename);

cli_func_f cli_diproc_experiment;
cli_func_f cli_diproc_status;
cli_func_f cli_diproc_dummy;
void cli_diproc_help_status(struct cli *cli);
void cli_diproc_help_board(struct cli *cli);

void diproc1_mod(uint8_t *firmware, unsigned mod);

struct diagproc_exp_priv;
void diagproc_exp_init(struct diagproc_exp_priv **, const char *name);
int diagproc_exp_download(struct diagproc_exp_priv *, uint8_t length, uint8_t *ram, uint8_t *ip);

void DiagBus_Explain_Cmd(struct vsb *vsb, const uint8_t serbuf[2]);

uint64_t diagbus_out_count(void);


#endif /* DIAG_DIAG_H */
