
#ifndef R1000SC_H
#define R1000SC_H

extern int sc_started;

void load_programmable(const char *who,
    void *dst, size_t size, const char *spec);

void pit_clock(void);

#include "Infra/microtrace.h"

extern uint16_t mp_refresh_count;
extern uint16_t mp_cur_uadr;
extern unsigned mp_fiu_freeze;
extern unsigned mp_fiu_unfreeze;
extern unsigned mp_ioc_trace;
extern unsigned mp_nua_bus;
extern unsigned mp_seq_prepped;
extern unsigned mp_seq_halted;

double sc_now(void);
#endif /* R1000SC_H */
