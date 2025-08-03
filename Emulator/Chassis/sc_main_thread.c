#include <stddef.h>
#include <stdint.h>

#include "Infra/r1000.h"
#include "Chassis/r1000sc.h"
#include "Chassis/r1000sc_priv.h"
#include "Chassis/r1000_arch.h"

static uint64_t ucycle;

double
sc_now(void)
{
	return (ucycle * 200);
}

void *
sc_main_thread(void *priv)
{
	struct r1000_arch_state *state = r1000_arch_new();

	(void)priv;
	(void)sc_main_get_quota();
	while(1) {
		r1000_arch_micro_cycle(state);
		ucycle += 1;
	}
	return(0);
}

double
sc_when(void)
{
	return (ucycle * 200e-9);
}
