#!/usr/bin/env python3

''' 16K x 64 SRAM '''

from chip import Chip, FChip, ChipSig

class XLRULOGIC(FChip):

    ''' LRU logic '''

    symbol_name = "XLRULOGIC"

    def __init__(self):
        super().__init__()
        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "HITQ"))
        self.sig_left(ChipSig("-->+", "LOGQ"))
        self.sig_left(ChipSig("-->+", "SOIL"))
        self.sig_left(ChipSig("-->+", "LPAR"))
        self.sig_left(ChipSig("-->+", "NMATCH"))
        self.sig_left(ChipSig("-->+", "OMATCH"))
        self.sig_left(ChipSig("-->+", "LRU_UPDATE"))
        self.sig_left(ChipSig("-->+", "MRUIS_F"))
        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "LHIT", 0, 3))
        self.sig_left(ChipSig("-->+", "ITAG", 56, 57))
        self.sig_left(ChipSig("-->+", "CMD", 0, 3))
        self.sig_left(ChipSig("-->+", "FORCE_HIT"))
        self.sig_left(ChipSig("-->+", "PHIT"))
        self.sig_left(ChipSig("-->+", "MCYC1"))
        self.sig_left(ChipSig("-->+", "LATE"))

        self.sig_right(ChipSig("o<->", "TAG", 0, 7))
        self.sig_right(ChipSig("+<->", "HITLRU", 0, 3))
        self.sig_right(ChipSig("o-->", "HIT"))

        self.sig_right(ChipSig("+-->", "TMP", 0, 7))
        self.finish(27)

class XTAGRAM(Chip):

    ''' 16K x 64 SRAM '''

    symbol_name = "XTAGRAM"

    symbol = '''
       |    |
       |    |
      1v   2v
   +---o----o---+
   |   WE   CS  |
   |            |
  3|            |17
-->+A0       IO0+<->
  4|            |18
-->+A1       IO1+<->
  5|            |19
-->+A2       IO2+<->
  6|            |20
-->+A3       IO3+<->
  7|            |21
-->+A4       IO4+<->
  8|            |22
-->+A5       IO5+<->
  9|            |23
-->+A6       IO6+<->
 10|            |24
-->+A7       IO7+<->
 11|            |25
-->+A8       IO8+<->
 12|            |26
-->+A9       IO9+<->
 13|            |27
-->+A10     IO10+<->
 14|            |28
-->+A11     IO11+<->
 15|            |29
-->+A12     IO12+<->
 16|            |30
-->+A13     IO13+<->
   |            |31
   |        IO14+<->
   |            |32
   |        IO15+<->
   |            |33
   |        IO16+<->
   |            |34
   |        IO17+<->
   |            |35
   |        IO18+<->
   |            |36
   |        IO19+<->
   |            |37
   |        IO20+<->
   |            |38
   |        IO21+<->
   |            |39
   |        IO22+<->
   |            |40
   |        IO23+<->
   |            |41
   |        IO24+<->
   |            |42
   |        IO25+<->
   |            |43
   |        IO26+<->
   |            |44
   |        IO27+<->
   |            |45
   |        IO28+<->
   |            |46
   |        IO29+<->
   |            |47
   |        IO30+<->
   |            |48
   |        IO31+<->
   |            |49
   |        IO32+<->
   |            |50
   |        IO33+<->
   |            |51
   |        IO34+<->
   |            |52
   |        IO35+<->
   |            |53
   |        IO36+<->
   |            |54
   |        IO37+<->
   |            |55
   |        IO38+<->
   |            |56
   |        IO39+<->
   |            |57
   |        IO40+<->
   |            |58
   |        IO41+<->
   |            |59
   |        IO42+<->
   |            |60
   |        IO43+<->
   |            |61
   |        IO44+<->
   |            |62
   |        IO45+<->
   |            |63
   |        IO46+<->
   |            |64
   |        IO47+<->
   |            |65
   |        IO48+<->
   |            |66
   |        IO49+<->
   |            |67
   |        IO50+<->
   |            |68
   |        IO51+<->
   |            |69
   |        IO52+<->
   |            |70
   |        IO53+<->
   |            |71
   |        IO54+<->
   |            |72
   |        IO55+<->
   |            |73
   |        IO56+<->
   |            |74
   |        IO57+<->
   |            |75
   |        IO58+<->
   |            |76
   |        IO59+<->
   |            |77
   |        IO60+<->
   |            |78
   |        IO61+<->
   |  xnn       |79
   |        IO62+<->
   |            |80
   |        IO63+<->
   |            |
   |  _         |
   +------------+
'''

def register():
    yield XTAGRAM()
    yield XLRULOGIC()
