#ifndef R1000SC_PRIV_H
#define R1000SC_PRIV_H

#ifdef __cplusplus
extern "C" {
#endif

#define R1K_BOARD_MEM32_0	(1<<0)
#define R1K_BOARD_MEM32_2	(1<<1)
#define R1K_BOARD_FIU		(1<<2)
#define R1K_BOARD_SEQ		(1<<3)
#define R1K_BOARD_TYP		(1<<4)
#define R1K_BOARD_VAL		(1<<5)
#define R1K_BOARD_IOC		(1<<6)
#define R1K_BOARD_ALL (R1K_BOARD_MEM32_0|R1K_BOARD_FIU|R1K_BOARD_SEQ| \
		       R1K_BOARD_TYP|R1K_BOARD_VAL|R1K_BOARD_IOC)

void *sc_main_thread(void *priv);

double sc_main_get_quota(void);

double sc_when(void);

extern int sc_boards;
extern const char *tracepath;

extern int sc_forced_reset;
extern struct timespec sc_t0;

#ifndef __cplusplus
cli_func_f cli_sc_watchdog;
#endif

#ifdef __cplusplus
}
#endif

#endif /* R1000SC_PRIV_H */
