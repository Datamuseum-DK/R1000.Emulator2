
#define TRACERS								\
	TRACER(console, "Console characters")				\
	TRACER(ioc_instructions, "IOC CPU instruction execution")	\
	TRACER(ioc_interrupt, "IOC interrupts")				\
	TRACER(ioc_dma, "IOC DMA")					\
	TRACER(ioc_io, "IOC IO")					\
	TRACER(ioc_pit, "IOC PIT timer")				\
	TRACER(ioc_sc, "IOC SystemC cycles")				\
	TRACER(ioc_modem, "IOC Internal Modem")				\
	TRACER(diagbus, "All bytes transmitted on DiagBus")		\
	TRACER(disk_data, "Data to/from disk(s)")			\
	TRACER(tape_data, "Data to/from tape(s)")			\
	TRACER(scsi_cmd, "SCSI commands, both busses")			\
	TRACER(scsi_data, "SCSI data, both busses")			\
	TRACER(systemc, "SystemC model")
