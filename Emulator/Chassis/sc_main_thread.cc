#include <stddef.h>
#include <stdint.h>

#include "Chassis/r1000sc.h"
#include "Chassis/r1000sc_priv.h"
#include "Chassis/r1000_arch.hh"

static uint64_t ucycle;

double
sc_now(void)
{
	return (ucycle * 200);
}

extern "C"
void *
sc_main_thread(void *priv)
{
	r1000_arch r1k;

	(void)sc_main_get_quota();
	while(1) {
		r1k.doit();
		ucycle += 1;
	}
	return(0);
}

double
sc_when(void)
{
	return (ucycle * 200e-9);
}
