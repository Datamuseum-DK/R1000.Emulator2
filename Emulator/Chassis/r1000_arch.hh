#ifndef R1000_ARCH
#define R1000_ARCH

struct r1000_arch_state;

class r1000_arch {
	public:
	r1000_arch(void);
	void doit(void);

	private:
	struct r1000_arch_state *state;

};

#endif /* R1000_ARCH */
