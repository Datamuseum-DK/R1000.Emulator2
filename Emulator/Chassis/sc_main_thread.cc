#include <stdio.h>
#include <systemc.h>

#include "Chassis/r1000sc.h"
#include "Chassis/r1000sc_priv.h"


double
sc_now(void)
{
	return (sc_time_stamp().to_double());
}

#include "planes_pub.hh"
#include "planes.hh"

#include "emu_pub.hh"

extern "C"
void *
sc_main_thread(void *priv)
{
	int argc = 0;
	char **argv = NULL;
	int retval;

	(void)priv;

	retval = sc_core::sc_elab_and_sim( argc, argv);
	fprintf(stderr, "HERE %s %d: retval %d\n", __func__, __LINE__, retval);
	return (NULL);
}

int
sc_main(int argc, char *argv[])
{
	emu *emu;
	planes *planes;

	(void)argc;
	(void)argv;

	planes = make_planes("PLANES");
	//planes->tf = sc_create_vcd_trace_file(tracepath);

	emu = make_emu("EMU", planes);

	planes->PD = false;
	planes->PU = true;
	// planes->CLAMPnot = false;

	sc_set_time_resolution(1, sc_core::SC_NS);

	cout << sc_get_time_resolution() <<  " Resolution\n";

	sc_start(SC_ZERO_TIME);
	while(1) {
		double dt = sc_main_get_quota();
		sc_start(dt * 1e6, SC_US);
		cout << "@" << sc_time_stamp() << " DONE\n";
		// sc_close_vcd_trace_file(planes->tf);
	}

	return(0);
}

double
sc_when(void)
{
	return (sc_time_stamp().to_seconds());
}
