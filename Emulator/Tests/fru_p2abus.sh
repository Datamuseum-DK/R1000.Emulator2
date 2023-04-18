#!/bin/sh

make -j 3 && make -j 3

. Tests/subr_test.rc

sc_boards ioc fiu mem0 seq typ val

# cli 'trace +ioc_instructions'
cli "iop memtrace add 0x3fda0 0x3fda8"

cli 'sc trace DI*PROC 4'

# planes.DIAG_FREEZEnot and DIAG_SYNCnot
cli 'sc trace IOC.*IONAN3A 1'

# planes.DIAG_FREEZEnot
#cli 'sc trace IOC.*DPNAN0A 1'
#cli 'sc trace TYP.*TSOC1D 1'
#cli 'sc trace VAL.*TSOC1D 1'
#cli 'sc trace FIU.*DOCDRA 1'
#cli 'sc trace MEM.*SETOCDC 1'
#cli 'sc trace SEQ.*DOCDRA 1'


# DIAG_SYNCnot
#cli 'sc trace FIU.*DOCDRB 1'
#cli 'sc trace SEQ.*DOCDRB 1'

cli 'sc trace SEQ.*RDNAN0A 1'
cli 'sc trace SEQ.*CKNAN5A 1'
cli 'sc trace SEQ.*DG8NA 1'
# cli 'sc trace SEQ.*UDRV$ 1'

# 
#cli 'sc trace FIU.*MMPRM1 1'
#cli 'sc trace FIU.*MMPRM3 1'
#cli 'sc trace seq_41 1'
#cli 'sc trace fiu_63 1'
#cli 'sc trace fiu_41 1'
#cli 'sc trace fiu_56 1'

cli 'sc quota add 2000'
cli 'sc quota exit'
#cli 'sc trace mem32_23 1'
#cli 'sc trace mem32_24 1'
#cli 'sc trace mem32_31 1'

# 8 => Initialize processor state
# 3 => Execute diagnostics
# 4 => Run a specific test
# 10 => P2ABUS
fru_prompt 8 3 4 10

run
