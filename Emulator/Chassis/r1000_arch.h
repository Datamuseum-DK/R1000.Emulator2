#ifndef R1000_ARCH
#define R1000_ARCH

struct r1000_arch_state;

struct r1000_arch_state * r1000_arch_new(void);
void r1000_arch_micro_cycle(struct r1000_arch_state *state);

extern int sc_started;

void pit_clock(void);

extern uint16_t mp_refresh_count;
extern uint16_t mp_cur_uadr;
extern unsigned mp_fiu_freeze;
extern unsigned mp_fiu_unfreeze;
extern unsigned mp_ioc_trace;
extern unsigned mp_nua_bus;
extern unsigned mp_seq_prepped;
extern unsigned mp_seq_halted;

double sc_now(void);

void *sc_main_thread(void *priv);

double sc_main_get_quota(void);

double sc_when(void);

extern const char *tracepath;

extern int sc_forced_reset;
extern struct timespec sc_t0;

cli_func_f cli_sc_watchdog;

#endif /* R1000_ARCH */
