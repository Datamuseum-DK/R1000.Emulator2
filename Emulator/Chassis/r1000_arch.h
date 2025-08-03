#ifndef R1000_ARCH
#define R1000_ARCH

struct r1000_arch_state;

struct r1000_arch_state * r1000_arch_new(void);
void r1000_arch_micro_cycle(struct r1000_arch_state *state);

#endif /* R1000_ARCH */
