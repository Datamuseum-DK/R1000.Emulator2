#!/usr/bin/env python3

'''  Zero count register '''

from chip import Chip

class XZCNT(Chip):

    ''' 8x8 parity generator '''

    symbol_name = "XZCNT"

    symbol = '''
   +-----------+
  %|           |%
-->+CLK      OEo<--
   |           |
  %|           |%
-->+I0       Z0o===
  %|           |%
-->+I1       Z1o===
  %|           |%
-->+I2       Z2p===
  %|           |%
-->+I3       Z3o===
  %|           |%
-->+I4       Z4o===
  %|           |%
-->+I5       Z5o===
  %|           |%
-->+I6       Z6o===
  %|           |%
-->+I7       Z7o===
  %|           |%
-->+I8       Z8o===
  %|           |%
-->+I9       Z9o===
  %|           |%
-->+I10     Z10o===
  %|           |%
-->+I11     Z11o===
  %|           |%
-->+I12     Z12o===
  %|           |%
-->+I13     Z13o===
  %|           |%
-->+I14     Z14o===
  %|           |%
-->+I15     Z15o===
  %|           |%
-->+I16     Z16o===
  %|           |%
-->+I17     Z17o===
  %|           |%
-->+I18     Z18o===
  %|           |%
-->+I19     Z19o===
  %|           |%
-->+I20     Z20o===
  %|           |%
-->+I21     Z21o===
  %|           |%
-->+I22     Z22o===
  %|           |%
-->+I23     Z23o===
  %|           |%
-->+I24     Z24o===
  %|           |%
-->+I25     Z25o===
  %|           |%
-->+I26     Z26o===
  %|           |%
-->+I27     Z27o===
  %|           |%
-->+I28     Z28o===
  %|           |%
-->+I29     Z29o===
  %|           |%
-->+I30     Z30o===
  %|           |%
-->+I31     Z31o===
  %|           |%
-->+I32     Z32o===
  %|           |%
-->+I33     Z33o===
  %|           |%
-->+I34     Z34o===
  %|           |%
-->+I35     Z35o===
  %|           |%
-->+I36     Z36o===
  %|           |%
-->+I37     Z37o===
  %|           |%
-->+I38     Z38o===
  %|           |%
-->+I39     Z39o===
  %|           |%
-->+I40     Z40o===
  %|           |%
-->+I41     Z41o===
  %|           |%
-->+I42     Z42o===
  %|           |%
-->+I43     Z43o===
  %|           |%
-->+I44     Z44o===
  %|           |%
-->+I45     Z45o===
  %|           |%
-->+I46     Z46o===
  %|           |%
-->+I47     Z47o===
  %|           |%
-->+I48     Z48o===
  %|           |%
-->+I49     Z49o===
  %|           |%
-->+I50     Z50o===
  %|           |%
-->+I51     Z51o===
  %|           |%
-->+I52     Z52o===
  %|           |%
-->+I53     Z53o===
  %|           |%
-->+I54     Z54o===
  %|           |%
-->+I55     Z55o===
  %|           |%
-->+I56     Z56o===
  %|           |%
-->+I57     Z57o===
  %|           |%
-->+I58     Z58o===
  %|           |%
-->+I59     Z59o===
  %|           |%
-->+I60     Z60o===
  %|           |%
-->+I61     Z61o===
  %|           |%
-->+I62     Z62o===
  %|    xnn    |%
-->+I63     Z63o===
   |           |
   | _         |
   +-----------+
'''

def register():
    yield XZCNT()
