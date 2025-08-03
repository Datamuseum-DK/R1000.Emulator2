
struct diagproc;

typedef int diagprocturbo_t(const struct diagproc *);

struct diagproc_context {
	uint64_t profile[8192];
	uint64_t instructions;
	uint64_t executions;
};

struct diagproc {

	const char *name;
	char *arg;
	unsigned mod;
	struct mcs51 *mcs51;
	int version;
	int ident;
	int idle;
	uint32_t *do_trace;
	struct elastic_subscriber *diag_bus;
	pthread_mutex_t mtx;
	int did_io;
	int longwait;
	struct vsb *vsb;

	int8_t pc0;
	unsigned flags[0x2000];
	uint8_t download_len;

	uint8_t dl_ptr;
	uint8_t dl_cnt;
	uint8_t dl_sum;
	uint64_t dl_hash;

	/* Actions to complete current instruction */
	int do_movx;		// MOVX movx_adr,movx_data cycle

	/* Preparations for next instruction */
	int next_needs_p1;	// Update p1val before next instruction
	int next_needs_p2;	// Update p2val before next instruction
	int next_needs_p3;	// Update p3val before next instruction

	/* Variables */
	int pin9_reset;
	unsigned p0val;
	unsigned p0mask;
	unsigned p1val;
	unsigned p1mask;
	unsigned p2val;
	unsigned p2mask;
	unsigned p3val;
	unsigned p3mask;
	int movx_adr;
	int movx_data;

	diagprocturbo_t *turbo;
	uint8_t *ram;
	uint8_t *ip;
};

struct diagproc *DiagProcCreate(const char *name, const char *arg,
    uint32_t *do_trace);
int DiagProcStep(struct diagproc *, struct diagproc_context *);

diagprocturbo_t diagproc_turbo_fiu;
diagprocturbo_t diagproc_turbo_ioc;
diagprocturbo_t diagproc_turbo_mem32;
diagprocturbo_t diagproc_turbo_seq;
diagprocturbo_t diagproc_turbo_typ;
diagprocturbo_t diagproc_turbo_val;

int diag_load_novram(const struct diagproc *dp, const char *novram_name, unsigned src, unsigned dst, unsigned len);

uint64_t diagbus_out_count(void);
