
#ifdef __cplusplus
extern "C" {
#endif

struct diagproc_priv;

struct diagproc_context {
	uint64_t profile[8192];
	uint64_t instructions;
	uint64_t executions;
};

struct diagproc_ctrl {

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

	struct diagproc_priv *priv;
};

struct diagproc_ctrl *DiagProcCreate(const char *name, const char *arg,
    uint32_t *do_trace);
void DiagProcStep(struct diagproc_ctrl *, struct diagproc_context *);

#ifdef __cplusplus
}
#endif
