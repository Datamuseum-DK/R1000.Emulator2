#ifndef R1000_ARCH
#define R1000_ARCH

struct r1000_arch_state;

class r1000_arch {
	public:
	r1000_arch(void);
	void doit(void);

	private:
	struct r1000_arch_state *state;

// -------------------- MEM --------------------

	unsigned find_set(unsigned cmd);
	bool is_hit(unsigned adr, unsigned eadr, unsigned set);
	void load_mar(void);
	void mem_h1(void);
	void mem_q4(void);

// -------------------- FIU --------------------

	uint64_t read_fiu_bus(unsigned line);
	void do_tivi(void);
	void rotator(bool sclk);
	void fiu_conditions(void);
	uint64_t frame(void);
	void tcsa(bool clock);
	void fiu_q1(void);
	void fiu_q2(void);
	void fiu_q4(void);

// -------------------- SEQ --------------------

	void int_reads(void);
	unsigned group_sel(void);
	unsigned late_macro_pending(void);
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
	void seq_q2(void);
	void seq_q3(void);
	void seq_q4(void);

// -------------------- TYP --------------------

	bool bin_op_pass(void);
	bool priv_path_eq(void);
	bool a_op_pass(void);
	bool b_op_pass(void);
	bool clev(void);
	void typ_cond(unsigned condsel, unsigned when);
	void cond_a(bool val);
	void cond_b(bool val);
	void cond_c(bool val);
	void cond_d(bool val);
	void cond_e(bool val);
	void typ_find_a(void);
	void typ_find_b(void);
	void typ_h1(void);
	void typ_q2(void);
	void typ_q4(void);

// -------------------- VAL --------------------

	bool ovrsgn(void);
	void val_cond(void);
	bool fiu_cond(void);
	void val_find_a(void);
	void val_find_b(void);
	void val_h1(void);
	void val_q2(void);
	void val_q4(void);

// -------------------- IOC --------------------

	void ioc_do_xact(void);
	void ioc_cond(void);
	void ioc_h1(void);
	void ioc_q2(void);
	void ioc_q4(void);
};

#endif /* R1000_ARCH */
