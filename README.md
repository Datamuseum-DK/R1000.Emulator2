# R1000.Emulator

This is an emulator for the Rational R1000/400 computer, it is not done yet,
but it gets very far in the boot process … very, very slowly.

If you have never heard about the Rational R1000 computer before:

https://datamuseum.dk/wiki/Rational/R1000s400

0. This is known to run under FreeBSD and OS/X 

1. Install KiCad (>7), python3 and SystemC

2. run `(cd Schematics/Symbols && python3 build_symbols.py)`

This produces the symbolfiles for KiCad.

3. run `(cd Schematics && make)`

This produces netlists from the schematics

4. run `(cd Emulator && make setup)`

This clones the Musashi 68k emulator into the tree.

5. Create a `Emulator/Makefile.local`:

   # Which schematics, "Hw" or "Optimized" ?
   SCHEM=Hw
   SCHEM=Optimized
   WORKDIR = ../_work/${SCHEM}
   NETLISTS += ../Schematics/${SCHEM}/*/*.net
   
   DISK0_IMAGE = "${WORKDIR}/../DiskImages/20230105_snap08.0.bin"
   DISK1_IMAGE = "${WORKDIR}/../DiskImages/20230105_snap08.1.bin"

6. Download diskimages, they are 1GB each, so they are not checked in.
   Ask phk@freebsd.org where to find them.

7. run `(cd Emulator && make [-j N])`

There is quite a bit to compile, expect this some part of an hour.

8. run `(cd Emulator && sh Tests/expmon_test_ioc.sh --quick)`

This should take a minute or two and produces a file named
`_work/Optimized/_expmon_test_ioc.console` where the last couple
of lines should be:

   […]
   TRACE RAM CELL TEST                                        PASSED
   
   END OF IOC BOARD TESTING
   
   IOC BOARD                                                  PASSED

NB: This file contains ANSI escape-sequences.

# THINGS YOU CAN DO

NB: The indicated durations depend a LOT on your machine.

1. Run the microcode diagnostics: `(cd Emulator && sh Tests/run_udiag.sh)`

This takes roughly a day.

2. Run the FRU diagnostics: `(cd Emulator && sh Tests/fru_phase3.sh)`

This takes a couple of days.

3. Start booting system: `(cd Emulator && sh Tests/boot_env.sh --background run0)`

This takes weeks.

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

# Useful stuff:

Disassembly of the IOC EEPROM: http://datamuseum.dk/aa/r1k_dfs/be/bed92cf60.html

Disassembly of the RESHA EEPROM: http://datamuseum.dk/aa/r1k_dfs/f3/f3d8d4065.html

Disassembly of the sector0 bootstrap: http://datamuseum.dk/aa/r1k_dfs/82/82a46de15.html

Disassembly of the loaded KERNEL.0: http://datamuseum.dk/aa/r1k_dfs/77/77d6c3277.html

Disassembly of the loaded FS.0: http://datamuseum.dk/aa/r1k_dfs/61/6176fa9c7.html

Disassembly of the loaded PROGRAM.0: http://datamuseum.dk/aa/r1k_dfs/f1/f15447000.html

Hat-Tip to @kstenerud: The 68k20 IOC is emulated with his https://github.com/kstenerud/Musashi

*end*
