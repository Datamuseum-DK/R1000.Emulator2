# R1000.Emulator2

This is a software emulation of the Rational R1000/400 computer.

If you have never heard about the Rational R1000 computer before:

https://datamuseum.dk/wiki/Rational/R1000s400

The goal of this project is to preserve the R1000/400 machine,
and the unique Rational Environment in software, while working
hardware still exists.

The ``main`` branch of this repository is where development happens, when
events dictate it, we will make ``releaseN`` branches and list them here:

| Release  | Slowdown | Time to Idle | Comment |
| -------- | -------- | -------------| ---------------------------------------------- |
| release1 |     420x |         137h | First working version of the emulator          |
| release2 |      N/A |          N/A | HW-true schematics booted to login             |

As time permits, we will continue to work on this emulation, hoping
to make it at least as fast as the hardware, but for now the only
realistic way to experience the R1000 is to visit our museum in
Copenhagen and see the real thing.

# Getting Started

0. This is known to run under FreeBSD and OS/X

1. Install a C++ compiler, python3, SystemC and Kicad7 or later.

2. Check out this git repository

3. run `(cd Schematics && make)`

This produces netlists from the schematics

4. run `(cd Emulator && make setup)`

This clones the Musashi 68k emulator into the tree.

5. Create a `Emulator/Makefile.local` along these lines:

```
   # Which schematics, "Hw" or "Optimized" ?
   SCHEM=Hw
   SCHEM=Optimized
   WORKDIR = ../_work/${SCHEM}
   NETLISTS += ../Schematics/${SCHEM}/*/*.net

   DISK0_IMAGE = "${WORKDIR}/../DiskImages/20230105_snap08.0.bin"
   DISK1_IMAGE = "${WORKDIR}/../DiskImages/20230105_snap08.1.bin"
```

6. Download diskimages, they are 1GB each, so they are not checked in.

You can run with the original disk images: https://datamuseum.dk/wiki/Bits:Keyword/RATIONAL_1000/DISK

But they have a lot of stuff in them, so they take an entire
hour to boot on the real hardware, and more than a couple of
weeks for the emulator to chew through.

We have a set of brutally cleaned up disk images, which boot much
faster, send phk@datamuseum.dk email and he will make them available.

At some future date we hope to make available a more gently cleaned
and hopefully even faster booting set of disk images available.

7. run `(cd Emulator && make [-j N] bus)`

There is quite a bit to compile, expect this some fraction of an hour.

8. run `(cd Emulator && sh Tests/expmon_test_ioc.sh --quick)`

This should take a minute or two and produces a file named
`_work/Optimized/_expmon_test_ioc.console` where the last couple
of lines should be:
```
   […]
   TRACE RAM CELL TEST                                        PASSED

   END OF IOC BOARD TESTING

   IOC BOARD                                                  PASSED
```
NB: This file contains ANSI escape-sequences.

9. Run the microcode diagnostics: `(cd Emulator && sh Tests/run_udiag.sh)`

This takes a good bite of a day and does not emit much to the console while running.

10. Start the Rational Environment: `(cd Emulator && sh Tests/boot_env --background`

This takes several days.  With the cut down ``snap08`` diskimage, on a MacBook Pro M2
you can start to log after about four days, and the system is fully booted after 5½ day.

11. Follow the boot progress

Look for obvious catastrophic trouble in the operator console output which
lands in `_work/Optimized/boot/_.console`

12. Log in

Once the environment has booted, look near the top of the file
`_work/Optimized/boot/_r1000.log` and find these two lines:
```
    console listening on 0.0.0.0 <number1>
    comm listening on 0.0.0.0 <number2>
```
Telnet into the simulator using one of those port numbers,
depending on which "serial" port you want::
```
    telnet localhost <number>
```
Have fun … very, very slowly …  Remember that the emulator runs
hundreds of times slower than the real machine, just logging in
will take an hour or possibly more.

Your terminal program must emulate one of the very few supported
terminals types in the Rational Environment, we plan to make a
FACIT emulation available at some point, but for now you are on
your own.

# OVERALL STRUCTURE

The R1000 Emulator is a bit of an agglomerate, or if you will, a Frankenstein monster.

This software simulation consists of:

* Musashi 68K20 emulator
* Our own i8052 emulator
* The SystemC emulation library
* Python3 scripts to produce KiCad symbols
* R1000 Schematics drawn in KiCad
* Python3 scripts to turn KiCad netlists into C++/SystemC source code
* Emulation of IOC memory and peripherals (UARTs, RTC, SCSI, disks, tape)
* A CLI interface
* A Configurable trace facility
* A 68K20 spelunking, tracing and debugging facility
* A Small RPN interpreter for above.
* and much more…

# Useful information stuff:

Disassembly of the IOC EEPROM: http://datamuseum.dk/aa/r1k_dfs/be/bed92cf60.html

Disassembly of the RESHA EEPROM: http://datamuseum.dk/aa/r1k_dfs/f3/f3d8d4065.html

Disassembly of the sector0 bootstrap: http://datamuseum.dk/aa/r1k_dfs/82/82a46de15.html

Disassembly of the loaded KERNEL.0: http://datamuseum.dk/aa/r1k_dfs/77/77d6c3277.html

Disassembly of the loaded FS.0: http://datamuseum.dk/aa/r1k_dfs/61/6176fa9c7.html

Disassembly of the loaded PROGRAM.0: http://datamuseum.dk/aa/r1k_dfs/f1/f15447000.html

Hat-Tip to @kstenerud: The 68k20 IOC is emulated with his https://github.com/kstenerud/Musashi

*end*
