/*
 * VME slot interface
 * ------------------
 *
 */

#include <fcntl.h>
#include <string.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Infra/vend.h"
#include "Infra/context.h"
#include "Iop/iop.h"
#include "Iop/memspace.h"

static uint8_t *enp100ram;

/**********************************************************************/

void v_matchproto_(mem_pre_read)
vme_window_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{

	uint32_t map, data;

	// assert(width == 2);
	map = vbe16dec(resha_misc_space + 0xa) & 0x7ff;
	data = vbe16dec(enp100ram + (map<<10) + adr);
	vbe16enc(space + adr, data);
	Trace(1, "VME RD %d %08x %08x %04x", width, map, adr, data);

	(void)debug;
	(void)space;
	(void)width;
	(void)adr;
}

/**********************************************************************/

void v_matchproto_(mem_post_write)
vme_window_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{

	uint32_t map, data;

	// assert(width == 2);
	map = vbe16dec(resha_misc_space + 0xa) & 0x7ff;
	data = vbe16dec(space + adr);
	Trace(1, "VME WR %d %08x %08x %04x", width, map, adr, data);
	vbe16enc(enp100ram + adr + (map<<10), data);

	(void)debug;
	(void)space;
	(void)width;
	(void)adr;
}

void
ioc_vme_init(void)
{

	enp100ram = CTX_GetRaw("ENP100.ram", (1 << 21));
	assert(enp100ram != NULL);
}


void v_matchproto_(mem_pre_read)
resha_wildcard_pre_read(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	(void)debug;
	(void)space;
	printf("RESHA_WILDCARD READ @0x%x width=0x%x\n", adr, width);
}

void v_matchproto_(mem_post_write)
resha_wildcard_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	(void)debug;
	printf("RESHA_WILDCARD WRITE @0x%x =0x%x width=0x%x\n", adr, vbe32dec(space + adr), width);
}
