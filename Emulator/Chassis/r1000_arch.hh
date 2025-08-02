#ifndef R1000_ARCH
#define R1000_ARCH

struct r1000_arch_state;

class r1000_arch {
	public:
	r1000_arch(void);
	void doit(void);

	private:
	struct r1000_arch_state *state;

	void csa_q4(void);

// -------------------- FIU --------------------

	void do_tivi(void);
	void rotator(bool sclk);
	bool fiu_conditions(void);
	uint64_t frame(void);
	void fiu_q1(void);
	void fiu_q2(void);
	void fiu_q4(void);

// -------------------- SEQ --------------------

	void int_reads(void);
	bool seq_conda(unsigned condsel);
	bool seq_cond9(unsigned condsel);
	bool seq_cond8(unsigned condsel);
	void nxt_lex_valid(void);
	bool condition(void);
	unsigned branch_offset(void);
	void q3clockstop(void);
	void seq_p1(void);
	void seq_h1(void);
	void seq_q1(void);
	void seq_q3(void);
	void seq_q4(void);

};

#endif /* R1000_ARCH */
