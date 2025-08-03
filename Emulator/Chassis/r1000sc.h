
#ifndef R1000SC_H
#define R1000SC_H

extern int sc_started;

void load_programmable(const char *who,
    void *dst, size_t size, const char *spec);

void pit_clock(void);

#include "Infra/microtrace.h"

double sc_now(void);

#define UEV_MEMEX	(1<<(15-0))
#define UEV_ECC		(1<<(15-1))
#define UEV_BKPT	(1<<(15-2))
#define UEV_CK_EXIT	(1<<(15-3))
#define UEV_FLD_ERR	(1<<(15-4))
#define UEV_CLASS	(1<<(15-5))
#define UEV_BIN_EQ	(1<<(15-6))
#define UEV_BIN_OP	(1<<(15-7))
#define UEV_TOS_OP	(1<<(15-8))
#define UEV_TOS1_OP	(1<<(15-9))
#define UEV_PAGE_X	(1<<(15-10))
#define UEV_CHK_SYS	(1<<(15-11))
#define UEV_NEW_PAK	(1<<(15-12))
#define UEV_NEW_STS	(1<<(15-13))
#define UEV_XFER_CP	(1<<(15-14))

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
	macro(unsigned, seq_uev, 0) \
	macro(unsigned, fiu_freeze, 0) \
	macro(unsigned, fiu_unfreeze, 0) \
	macro(unsigned, key_switch, 1) \
	macro(unsigned, csa_this_offs, 0) \
	macro(unsigned, csa_nve, 0) \
	macro(unsigned, csa_hit, 0) \
	macro(unsigned, csa_wr, 0) \
	macro(unsigned, load_top, 0) \
	macro(unsigned, load_bot, 0) \
	macro(unsigned, pop_down, 0) \
	macro(unsigned, load_wdr, 0) \
	macro(unsigned, mem_ctl, 0) \
	macro(unsigned, mem_continue, 0) \
	macro(unsigned, macro_event, 0) \
	macro(unsigned, uevent_enable, 0) \
	macro(unsigned, mem_set, 0) \
	macro(unsigned, mem_hit, 0) \
	macro(unsigned, dummy_next, 0) \
	macro(unsigned, restore_rdr, 0) \
	macro(unsigned, mem_cond, 0) \
	macro(unsigned, mem_cond_pol, 0) \
	macro(unsigned, mem_abort_e, 0) \
	macro(unsigned, mem_abort_el, 0) \
	macro(unsigned, mem_abort_l, 0) \
	macro(unsigned, clock_stop_0, 0) \
	macro(unsigned, clock_stop_3, 0) \
	macro(unsigned, clock_stop_4, 0) \
	macro(unsigned, clock_stop_6, 0) \
	macro(unsigned, clock_stop_7, 0) \
	macro(unsigned, sf_stop, 0) \
	macro(unsigned, freeze, 0) \
	macro(unsigned, clock_stop, 0) \
	macro(unsigned, ram_stop, 0) \
	macro(unsigned, state_clk_stop, 0) \
	macro(unsigned, state_clk_en, 0) \
	macro(unsigned, below_tcp, 0) \
	macro(unsigned, sync_freeze, 0) \
	macro(uint16_t, refresh_count, 0) \
	macro(uint16_t, cur_uadr, 0) \

#define MIDSTATE(macro) \
	macro(unsigned, cond_sel, 0) \
	macro(unsigned, csa_cntl, 0) \
	macro(unsigned, mar_cntl, 0) \
	macro(unsigned, adr_oe, 0) \
	macro(unsigned, fiu_oe, 0) \
	macro(unsigned, tv_oe, 0) \
	macro(unsigned, q_bit, 0) \
	macro(unsigned, csa_write_enable, 0) \
	macro(unsigned, csa_offset, 0) \

#define DMACRO(typ, nam, val) extern volatile typ mp_##nam;
MIDPLANE(DMACRO)
#undef DMACRO

#define DMACRO(typ, nam, val) extern volatile typ mp_##nam;
MIDSTATE(DMACRO)
#undef DMACRO

#define DMACRO(typ, nam, val) extern volatile typ mp_nxt_##nam;
MIDSTATE(DMACRO)
#undef DMACRO

#define UADR_MASK 0x3fff
#define UADR_WIDTH 14

#define BUS64_LSB(lsb) (63 - (lsb))

#endif /* R1000SC_H */
