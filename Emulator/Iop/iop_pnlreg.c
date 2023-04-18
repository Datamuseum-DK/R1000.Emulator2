/*
 * PNLREG - 4 bit LED control register
 * -----------------------------------
 *
 * Chip Select: 0xfffff2xx
 *
 */

#include "Infra/r1000.h"
#include "Infra/vend.h"
#include "Iop/memspace.h"

void v_matchproto_(mem_post_write)
pnlreg_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{
	if (space[adr])
		printf("PNLREG %x %x %x %x\n", debug, width, adr, space[adr]);
}

void v_matchproto_(mem_post_write)
dreg4_post_write(int debug, uint8_t *space, unsigned width, unsigned adr)
{

	(void)debug;
	(void)width;
	Trace(trace_diagbus, "DREG4 %d 0x%x 0x%x", width, adr, vbe32dec(space + adr));
}
