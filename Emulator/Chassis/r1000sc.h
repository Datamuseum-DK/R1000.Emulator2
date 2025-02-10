
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

#include "Infra/microtrace.h"

double sc_now(void);

uint8_t odd_parity(uint8_t);
uint8_t even_parity(uint8_t);
uint8_t odd_parity64(uint64_t);
uint8_t offset_parity(uint64_t);

struct f181 {
	uint32_t	a, b, o;
	unsigned	ci, co;
	unsigned	ctl;	// mag[1], m[1], s[4]
};

void f181_alu(struct f181 *);

#define MIDPLANE(macro) \
	macro(uint64_t, adr_bus, -1) \
	macro(uint64_t, fiu_bus, -1) \
	macro(unsigned, ioc_trace, 0) \
	macro(unsigned, nua_bus, 0x3fff) \
	macro(uint64_t, spc_bus, -1) \
	macro(uint64_t, typ_bus, -1) \
	macro(uint64_t, val_bus, -1) \
	macro(unsigned, seq_prepped, 0) \
	macro(unsigned, seq_halted, 0) \
	macro(unsigned, seq_uev0_memex, 1) \
	macro(unsigned, seq_uev5_class, 1) \
	macro(unsigned, seq_uev6_bin_eq, 1) \
	macro(unsigned, seq_uev7_bin_op, 1) \
	macro(unsigned, seq_uev8_tos_op, 1) \
	macro(unsigned, seq_uev9_tos1_op, 1) \
	macro(unsigned, seq_uev10_page_x, 1) \
	macro(unsigned, seq_uev11_chk_sys, 1) \
	macro(unsigned, seq_uev12_new_pak, 1) 

#define DMACRO(typ, nam, val) extern volatile typ mp_##nam;
MIDPLANE(DMACRO)
#undef DMACRO

#define UADR_MASK 0x3fff
#define UADR_WIDTH 14

#ifdef __cplusplus
}
#endif

/**********************************************************************
 * C++ Only below this point
 */

#ifdef __cplusplus

#include <sstream>

#define ALWAYS_TRACE( ...) \
	do { \
		char buf[4096]; \
		buf[0] = '\0'; \
		std::stringstream ss(buf); \
		ss << "" __VA_ARGS__ << (uint8_t)0; \
		sysc_trace(this->name(), ss.str().c_str()); \
	} while (0)

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

#define BUS64_LSB(lsb) (63 - (lsb))

#endif /* __cplusplus */

#endif /* R1000SC_H */
