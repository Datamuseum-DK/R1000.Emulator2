#ifndef R1000SC_PRIV_H
#define R1000SC_PRIV_H

void *sc_main_thread(void *priv);

double sc_main_get_quota(void);

double sc_when(void);

extern const char *tracepath;

extern int sc_forced_reset;
extern struct timespec sc_t0;

cli_func_f cli_sc_watchdog;

#endif /* R1000SC_PRIV_H */
