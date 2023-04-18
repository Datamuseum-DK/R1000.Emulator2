import sys

sys.path.append("/root/PyReveng3")
sys.path.append("/root/R1000.Disassembly/EXP")
sys.path.append("/home/phk/Proj/R1000.Disassembly/EXP")
sys.path.append("/root/R1000.Disassembly/UCODE")
sys.path.append("/home/phk/Proj/R1000.Disassembly/UCODE")

from pyreveng import mem, assy, data, listing
from exp_disass import R1kExp

from board import Board
from ioc import IOC_Board
from fiu import FIU_Board
from typ import TYP_Board
from mem import MEM_Board
from val import VAL_Board
from seq import SEQ_Board

class Main():
    def __init__(self):

        fn = sys.argv[1]
        self.boards = {
            "IOC": IOC_Board(),
            "FIU": FIU_Board(),
            "TYP": TYP_Board(),
            "VAL": VAL_Board(),
            "SEQ": SEQ_Board(),
            "MEM0": MEM_Board(0),
            "MEM2": MEM_Board(2),
        }
        self.consume(fn)

    def consume(self, fn):
        for i in open(fn):
            j = i.split()
            if j[1] != "SC":
                continue
            j = j[2:]
            k = j[1].split(".")
            brd = self.boards.get(k[0])
            if brd:
                brd.consume(j)
            elif j[1] not in ("Breakpoint", "DIAGBUS"):
                print("?", j)
        for brd in self.boards.values():
            brd.finish()

if __name__ == "__main__":
    Main()
