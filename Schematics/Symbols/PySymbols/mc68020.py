#!/usr/bin/env python3

''' MC68020 - 32-bit Microprocessor '''

from chip import Chip

class MC68020(Chip):

    ''' MC68020 - 32-bit Microprocessor '''

    symbol_name = "68020"

    checked = "IOC 0011"

    symbol = '''
   +---------------------------+
   |                           |B2
   |                        BG o-->
 C2|                           |F13
-->+ CLK                 IPEND o-->
 C1|                           |M1
-->o RESET                  DS o-->
 K2|                           |G3
oooo HALT                 DBEN o-->
 H1|                           |E2
-->o CDIS                  RMC o-->
 B3|                           |G1
-->o BR                    ECS o-->
 A1|                           |E13
-->o BGACK                 OCS o-->
J12|                           |L1
-->o IPL0                   AS o-->
J13|                           |L2
-->o IPL1                   WR o-->
H12|                           |F1
-->o IPL2                 SIZ0 +-->
 H2|                           |G2
-->o AVEC                 SIZ1 +-->
 H3|                           |E1
-->o DSACK0                FC0 +-->
 J1|                           |F3
-->o DSACK1                FC1 +-->
 J2|                           |F2
-->o BERR                  FC2 +-->
K13|                           |C4
<->+ D00                   A00 +-->
K12|                           |A2
<->+ D01                   A01 +-->
L13|                           |E12
<->+ D02                   A02 +-->
L12|                           |D13
<->+ D03                   A03 +-->
M13|                           |D12
<->+ D04                   A04 +-->
M12|                           |C13
<->+ D05                   A05 +-->
M11|                           |B13
<->+ D06                   A06 +-->
L10|                           |C12
<->+ D07                   A07 +-->
N12|                           |A13
<->+ D08                   A08 +-->
N11|                           |C11
<->+ D09                   A09 +-->
M10|                           |B12
<->+ D10                   A10 +-->
 L9|                           |A12
<->+ D11                   A11 +-->
N10|                           |C10
<->+ D12                   A12 +-->
 M9|                           |B11
<->+ D13                   A13 +-->
 N9|                           |A19
<->+ D14                   A14 +-->
 L8|                           |B10
<->+ D15                   A15 +-->
 M7|                           |C9
<->+ D16                   A16 +-->
 N6|                           |C8
<->+ D17                   A17 +-->
 M6|                           |B8
<->+ D18                   A18 +-->
 L6|                           |A8
<->+ D19                   A19 +-->
 N5|                           |B7
<->+ D20                   A20 +-->
 M5|                           |C7
<->+ D21                   A21 +-->
 N4|                           |A7
<->+ D22                   A22 +-->
 L5|                           |A6
<->+ D23                   A23 +-->
 M4|                           |B6
<->+ D24                   A24 +-->
 N3|                           |C6
<->+ D25                   A25 +-->
 M3|                           |A5
<->+ D26                   A26 +-->
 L4|                           |B5
<->+ D27                   A27 +-->
 N2|                           |A4
<->+ D28                   A28 +-->
 M2|                           |C5
<->+ D29                   A29 +-->
 L3|                           |B4
<->+ D30        xnn        A30 +-->
 N1|                           |A3
<->+ D31       _           A31 +-->
   |                           |
   +---------------------------+
'''

def register():
    yield MC68020(__file__)
