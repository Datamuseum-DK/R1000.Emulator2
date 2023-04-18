# R1000.Emulator

This is an emulator for the Rational R1000/400 computer, it is not done yet, but it gets
very far in the boot process … very, very slowly.

https://datamuseum.dk/wiki/Rational/R1000s400

0. This is known to run under FreeBSD and OS/X 

1. Install python3 and SystemC

2. Run `make setup`, this clones the Musashi 68k emulator and downloads the firmware images.

3. Create a `Makefile.local`:

	BRANCH ?= whatever
	WORKDIR = /some_GB_free_for_transient_stuff/${BRANCH}
	NETLISTS += ${WORKDIR}/*.net
	DISK0_IMAGE = "${WORKDIR}/../DiskImages/20230105_snap08.0.bin"
	DISK1_IMAGE = "${WORKDIR}/../DiskImages/20230105_snap08.1.bin"

4. Download diskimages and KiCad net-lists.  These are huge and change a lot, so they are
   not checked in yet.  Ask phk@freebsd.org where to find them.
   The `*.net` netlist files go in `${WORKDIR}`.
   The `*.bin` diskimages go in `${WORKDIR}/../DiskImages`

5. `make [-j N] all`  This takes some minutes.

6. In a separate window start: `cu -l /dev/nmdm0A`  (You may need: `sudo kldload nmdm`)

7. Run `sh Tests/cli_only.sh` and in the other window you should end up seeing:

```
    […]
    CLI/CRASH MENU - options are:
      1 => enter CLI
      2 => make a CRASHDUMP tape
      3 => display CRASH INFO
      4 => Boot DDC configuration
      5 => Boot EEDB configuration
      6 => Boot STANDARD configuration
    Enter option [enter CLI] : 1
    CLI>

```

The `CLI>` is the prompt of the DFS command line interpreter, try typing `DIR`

The first window has the emulator CLI, which allows you to do all sorts of things,
try typing `help`.

8. Stop the emulator with CTRL-C (or the `exit` CLI command)

9. Run the complete `FRU` diagnostic: `sh Tests/fru_phase3.sh`

This takes about a day.  You can monitor progress with `tail -F ${WORKDIR}/_fru_phase3.console`

10. Finally, boot the system:  `sh Tests/boot_env.sh`

This takes weeks.  You can monitor progress with `tail -F ${WORKDIR}/boot/_.console`

# OVERALL STRUCTURE

The R1000 Emulator is a bit of an agglomerate, or if you will, a Frankenstein monster.

The `r1000sim` program consists of:

* Musashi 68K20 emulator
* IOC memory and peripherals for the 68K20 (UARTs, RTC, SCSI, disks, tape)
* CLI interface
* Configurable trace facility
* 68K20 spelunking, tracing and debugging facility
* Small RPN interpreter for above.
* i8052 emulator
* DIPROC "adapter" between SystemC model of i8052 and i8052 emulator
* Stand alone DIPROC `experiment` excution
* Generic "elastic buffer" facility for byte-channels (TCP/nullmodem/files/send-expect)

The SystemC emulation of the actual hardware is "bolted on" via the following
shared libraries:

## libcomponents

Contains SystemC objects for chips used in R1000.

These are, in principle hand-written.

## libplanes

The front- and back-planes of the computer.

This holds the `sc_main` function, and SystemC modules which
drive the `RESET`, `POWER_FAIL` and similar signals.

We also drive the back-plane clocks from here, instead of
from the IOC, in order to not waste effort to simulate
the 20 MHz components on the IOC.

## lib{fiu|ioc|mem32|seq|typ|val}

Each board, one shlib.

The `NetList/process_kicad_netlists.py` script reads KiCad
netlists and produces C++/SystemC source files to build
these shlibs and their source-files are not checked in.


# Useful stuff:

Disassembly of the IOC EEPROM: http://datamuseum.dk/aa/r1k_dfs/be/bed92cf60.html

Disassembly of the RESHA EEPROM: http://datamuseum.dk/aa/r1k_dfs/f3/f3d8d4065.html

Disassembly of the sector0 bootstrap: http://datamuseum.dk/aa/r1k_dfs/82/82a46de15.html

Disassembly of the loaded KERNEL.0: http://datamuseum.dk/aa/r1k_dfs/77/77d6c3277.html

Disassembly of the loaded FS.0: http://datamuseum.dk/aa/r1k_dfs/61/6176fa9c7.html

Disassembly of the loaded PROGRAM.0: http://datamuseum.dk/aa/r1k_dfs/f1/f15447000.html

Hat-Tip to @kstenerud: The 68k20 IOC is emulated with his https://github.com/kstenerud/Musashi

# TODO

Add a cli commands:

* `breakpoint address` -- Stop emulation and dump 68K registers.  Leave CPU stopped.

* `examine address` -- Dump 256 bytes of memory.

* `deposit {address|register} data` -- Change state	

* `coredump` -- Drop copy of IOC-RAM to file

*end*
