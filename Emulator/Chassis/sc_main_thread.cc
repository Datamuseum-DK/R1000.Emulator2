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
#include "fiu_pub.hh"
#include "ioc_pub.hh"
#include "mem32_pub.hh"
#include "seq_pub.hh"
#include "typ_pub.hh"
#include "val_pub.hh"


SC_MODULE(PowerSequencer)
{
	sc_out <bool> clamp;	// CLAMP
	//sc_out <sc_logic> reset;	// RESET
	uint32_t do_trace = 0;

	SC_CTOR(PowerSequencer)
	{
		SC_THREAD(thread);
	}

	void thread()
	{
		clamp = false;
		//reset = sc_logic_0;
		wait(100, sc_core::SC_NS);
		clamp = true;
#if 0
		wait(200, sc_core::SC_NS);
		/*
		 * When running IOC experiments without the IOP we need
		 * to force the reset signal high because DREG4 pulls it
		 * low on IOC_RESET and the IOP will not be releasing it.
		 * (1+0 = 'X' but that is good enough for now.)
		 */
		if (sc_forced_reset)
			reset = sc_logic_1;
		else
			reset = sc_logic_Z;
#endif
	}
};

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
	mem32 *mem32_0;
	mem32 *mem32_2;
	seq *seq;
	typ *typ;
	val *val;
	fiu *fiu;
	ioc *ioc;
	emu *emu;
	planes *planes;

	(void)argc;
	(void)argv;

	planes = make_planes("PLANES");
	//planes->tf = sc_create_vcd_trace_file(tracepath);

	// Order as seen from front L…R
	if (sc_boards & R1K_BOARD_MEM32_2)
		mem32_2 = make_mem32("MEM2", planes);
	if (sc_boards & R1K_BOARD_MEM32_0)
		mem32_0 = make_mem32("MEM0", planes);
	if (sc_boards & R1K_BOARD_SEQ)
		seq = make_seq("SEQ", planes);
	if (sc_boards & R1K_BOARD_TYP)
		typ = make_typ("TYP", planes);
	if (sc_boards & R1K_BOARD_VAL)
		val = make_val("VAL", planes);
	if (sc_boards & R1K_BOARD_FIU)
		fiu = make_fiu("FIU", planes);
	if (sc_boards & R1K_BOARD_IOC)
		ioc = make_ioc("IOC", planes);

	emu = make_emu("EMU", planes);

	planes->PD = false;
	planes->PU = true;

	PowerSequencer powseq("UNCLAMP");
	powseq.clamp(planes->CLAMPnot);	// CLAMP
	// powseq.reset(planes->RESETnot);

#if 0
	planes->EXT_ID0 = false;
	planes->EXT_ID1 = true;
	planes->EXT_ID2 = false;
#endif

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
