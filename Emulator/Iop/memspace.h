
struct memdesc;

typedef int mem_event_f(void *priv, const struct memdesc *, const char *what,
    unsigned adr, unsigned val, unsigned width, unsigned peg);

struct memevent;

struct memdesc {
	const char		*name;
	uint32_t		lo;
	uint64_t		hi;
	uint32_t		mask;
	uint8_t			*pegs;
	size_t			space_length;
	size_t			pegs_length;
	VTAILQ_HEAD(,memevent)	events;
};

extern const char * const mem_op_read;
extern const char * const mem_op_debug_read;
extern const char * const mem_op_write;
extern const char * const mem_op_debug_write;

#define PEG_CHECK	(1<<7)
#define PEG_NOTRACE	(1<<6)
#define PEG_BREAKPOINT	(1<<5)

void mem_peg_check(const char *, struct memdesc *,
    unsigned, unsigned, unsigned, unsigned);
uint8_t * mem_find_peg(unsigned address);
void mem_peg_reset(unsigned lo, unsigned hi, unsigned pegval);
void mem_peg_set(unsigned lo, unsigned hi, unsigned pegval);

void mem_peg_register(unsigned lo, unsigned hi, mem_event_f *func, void *priv);
void mem_peg_expunge(const void *priv);

void mem_fail(const char *, unsigned, unsigned, unsigned);
extern const char *mem_error_cause;

typedef void mem_pre_read(int, uint8_t *, unsigned, unsigned);
typedef void mem_post_write(int, uint8_t *, unsigned, unsigned);

extern struct memdesc *memdesc[];
extern const unsigned n_memdesc;

void m68k_write_memory_8(unsigned, unsigned);
unsigned m68k_read_memory_8(unsigned);
void m68k_debug_write_memory_8(unsigned, unsigned);
unsigned m68k_debug_read_memory_8(unsigned);
void m68k_write_memory_16(unsigned, unsigned);
unsigned m68k_read_memory_16(unsigned);
void m68k_debug_write_memory_16(unsigned, unsigned);
unsigned m68k_debug_read_memory_16(unsigned);
void m68k_write_memory_32(unsigned, unsigned);
unsigned m68k_read_memory_32(unsigned);
void m68k_debug_write_memory_32(unsigned, unsigned);
unsigned m68k_debug_read_memory_32(unsigned);

#include "Iop/_memcfg.h"
