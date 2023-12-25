
#ifndef R1000SC_H
#define R1000SC_H


#ifdef __cplusplus
extern "C" {
#endif

extern int sc_started;

void load_programmable(const char *who,
    void *dst, size_t size, const char *spec);

void should_i_trace(const char *me, uint32_t *);

void sysc_trace(const char *me, const char *fmt);
void sc_tracef(const char *me, const char *fmt, ...) __printflike(2, 3);

void pit_clock(void);

void microtrace(const void *p, size_t l);

double sc_now(void);

uint8_t odd_parity(uint8_t);
uint8_t even_parity(uint8_t);
uint8_t odd_parity64(uint64_t);
uint8_t offset_parity(uint64_t);

#ifdef __cplusplus
}
#endif

/**********************************************************************
 * C++ Only below this point
 */

#ifdef __cplusplus

#include <sstream>

#define TRACE( ...) \
	do { \
		if (state->ctx.do_trace & 1) { \
			char buf[4096]; \
			buf[0] = '\0'; \
			std::stringstream ss(buf); \
			ss << "" __VA_ARGS__ << (uint8_t)0; \
			sysc_trace(this->name(), ss.str().c_str()); \
		} \
	} while (0)

#define DEBUG TRACE

#define IS_H(cond) (!((cond) == sc_dt::sc_logic_0))
#define IS_L(cond) ((cond) == sc_dt::sc_logic_0)
#define AS(cond) ((cond) ? sc_dt::sc_logic_1 : sc_dt::sc_logic_0)

#endif /* __cplusplus */

#endif /* R1000SC_H */
