:

sed '
/ FIRMWARE /d
/ DIAGBUS [RT]X /d
/[.]DI*PROC Exec /d
/ Breakpoint /d
/ Timeout_Stop_PIT/d
/ Timeout_Start_PIT/d
/ Timeout_Arm/d
/ Timeout_Cancel/d
/ Await_Interrupt/d
/ FillString/d
/ `Free2/d
/ `FileReadLine/d
/ `StringCat/d
/ `Malloc1/d
/ `NewString/d
/ `FreeString/d
/ `Lba2Chs/d
/ `AppendChar/d
/ `KC02_Start_Disk_IO/d
/ `KC03_Wait_Disk_IO/d
/mul[su]_d3_d4/d
/div[su]_d3_d4/d

/SCCALL.*Is_fc07_one_or_three/,/SCEXIT.*Is_fc07_one_or_three/d


/SCCALL.*WriteWords/,/SCEXIT.*WriteWords/{
  /RW_Sectors/d
}

/SCCALL.*ReadWords/,/SCEXIT.*ReadWords/{
  /RW_Sectors/d
}

/SCCALL.*WriteConsoleStringCrLf/,/SCEXIT.*WriteConsoleStringCrLf/{
  /`WriteConsoleString[(]/d
  / WriteConsole/d
}

/SCCALL.*WriteConsoleString/,/SCEXIT.*WriteConsoleString/{
  / WriteConsole/d
}

/SCCALL.*WriteConsoleCrLf/,/SCEXIT.*WriteConsoleCrLf/{
  /`KC06_Write_Console_Char/d
}

/SCCALL.*MountDisk/,/SCEXIT.*MountDisk/{
  /`RW_Sectors/d
}

/SCCALL.*WriteConsoleChar/,/SCEXIT.*WriteConsoleChar/{
  /`KC06_Write_Console_Char/d
}

/SCCALL.*TimeStamp/,/SCEXIT.*TimeStamp/{
  /Calendar/d
}

/SCCALL.*Get_fc01/,/SCEXIT.*Get_fc01/{
  /KC1C_ProtCopy/d
}

/SCCALL.*Get_fc05/,/SCEXIT.*Get_fc05/{
  /KC1C_ProtCopy/d
}

/SCCALL.*DiProcPing/,/SCEXIT.*DiProcPing/{
  /DiagBus_Response/d
  /KC15/d
}

/SCCALL.*DiProcCmd/,/SCEXIT.*DiProcCmd/{
  /KC15_DiagBus/d
}


/SCCALL.*Read_fc0c/,/SCEXIT.*Read_fc0c/{
  /KC1C_ProtCopy/d
}

/SCCALL.*Read_fc00/,/SCEXIT.*Read_fc00/{
  /KC1C_ProtCopy/d
}

/SCCALL.*Set_fc04_to_01/,/SCEXIT.*Set_fc04_to_01/{
  /KC1C_ProtCopy/d
}

/SCCALL.*ReadConfig/,/SCEXIT.*ReadConfig/{
  /KC1C_ProtCopy/d
}



/SCCALL.*`AskConsoleString/,/SCEXIT.*`AskConsoleString/{
  /`ReadChar/d
  /`WriteConsole/d
  /`KC07_Read_Console_Char/d
}

/SCCALL.*`ReadChar/,/SCEXIT.*`ReadChar/{
  /`KC07_Read_Console_Char/d
}

/SCCALL.*`SyncFreeList/,/SCEXIT.*`SyncFreeList/{
  /`RW_Sectors/d
}

/SCCALL.*Quad2String/,/SCEXIT.*Quad2String/{
  /Long2Quad/d
  /Modulus/d
  /Divide/d
  /Multiply/d
  /Subtract/d
  /IsEqual/d
}

/SCCALL.*Modulus/,/SCEXIT.*Modulus/{
  /Divide/d
  /Multiply/d
  /Subtract/d
}

/SCCALL.*OpenFile/,/SCEXIT.*OpenFile/{
  /`RW_Sectors/d
}

/SCCALL.*ExpXmit/,/SCEXIT.*ExpXmit/{
  /`KC15_DiagBus/d
}

/SCCALL.*ExpRun/,/SCEXIT.*ExpRun/{
  /`KC12_Sleep/d
  /`DiProcPing/d
}

/SCCALL.*`ExpUpload/,/SCEXIT.*`ExpUpload/{
  /DiagBus_Response/d
  /`KC15_DiagBus/d
}

/SCCALL.*ExpLoad/,/SCEXIT.*ExpLoad/{
  /RW_Sectors/d
  /OpenFile/d
  /ReadWords/d
  /ReadFile/d
  /CloseFile/d
}

/SCCALL.*IPC_..tBool/,/SCEIIT.*IPC_..tBool/{
  /`CopyBytes/d
  /MEMTRACE/d
}

/SCCALL.*IPC_..tString/,/SCEIIT.*IPC_..tString/{
  /`CopyBytes/d
  /MEMTRACE/d
}

/SCCALL.*IPC_..tEnd/,/SCEIIT.*IPC_..tEnd/{
  /`CopyBytes/d
  /MEMTRACE/d
}

/SCCALL.*SC=0x00010568/,/SCEXIT.*SC=0x00010568/{
  /GetConsoleConfig/d
}

/SCCALL.*ReadClusterNo/,/SCEXIT.*ReadClusterNo/{
  /`ReadConfig/d
}

s/PC=.*//

'
