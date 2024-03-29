/* Machine-generated, see /critter/R1K/R2_WIP/Emulator/Iop/make_pascal_syscalls.py */
	{ 0x10200, "`KC00_GetBootDev",
	    "'!' sp+4 @L 'a=' @B .B , '!' sp+2 @L 'b=' @W .W",
	    "sp+2 @L 'a=' @B .B , sp+0 @L 'b=' @W .W",
	},
	{ 0x10204, "`KC02_Start_Disk_IO",
	    "sp+5 'desc=' Pointer , sp+3 'dst=' Pointer , sp+2 'c=' @W .W",
	    "",
	},
	{ 0x10206, "`KC03_Wait_Disk_IO",
	    "sp+4 'a=' @W .W , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x1020a, "`KC05_PortWriteString",
	    "sp+4 'port=' @W .W , sp+2 'str=' String",
	    "",
	},
	{ 0x1020c, "`KC06_PortPutChar",
	    "sp+3 'port=' @W .W , sp+2 'b=' @B .B",
	    "",
	},
	{ 0x1020e, "`KC07_PortGetChar",
	    "sp+4 'port=' @W .W , '!' sp+2 @L 'ret=' @W .W",
	    "sp+0 @L 'ret=' @W .W",
	},
	{ 0x10210, "`KC08_PortSomething",
	    "sp+3 'port=' @W .W , sp+2 'b=' @B .B",
	    "",
	},
	{ 0x10212, "`KC09_PortStatus",
	    "sp+4 'Port=' @W .W , '!' sp+2 @L 'b=' @B .B",
	    "sp+0 @L 'b=' @B .B",
	},
	{ 0x10214, "`KC0a",
	    "sp+4 'a=' @W .W , sp+2 'b=' String",
	    "",
	},
	{ 0x10218, "`KC0c_Write_Modem_Char",
	    "sp+4 'a=' @W .W , sp+3 'b=' @W .W , sp+2 'c=' @B .B",
	    "",
	},
	{ 0x10220, "`KC10_Panic",
	    "sp+2 'code=' @L .L",
	    "",
	},
	{ 0x10222, "`KC11_Live",
	    "",
	    "",
	},
	{ 0x10224, "`KC12_Sleep",
	    "sp+2 'dur=' @L .L",
	    "",
	},
	{ 0x1022a, "`KC15_DiagBus",
	    "sp+4 'a=' @W .W , sp+2 'b=' @L .L",
	    "'>' sp+3 @B .B",
	},
	{ 0x10238, "`KC1c_ProtCopy",
	    "sp+5 'src=' Pointer , sp+3 'dst=' Pointer , sp+2 'len=' @W .W",
	    "",
	},
	{ 0x1023a, "`KC1d_BusCopy",
	    "sp+7 'src=' Pointer , sp+6 'sfc=' @W .W , sp+4 'dst=' Pointer , sp+3 'dfc=' @W .W , sp+2 'len=' @W .W",
	    "",
	},
	{ 0x1023c, "`KC1e_Fifo_Tx_Response",
	    "sp+3 'ptr=' Pointer , sp+2 'chan=' @W .W",
	    "",
	},
	{ 0x1023e, "`KC1f_Fifo_Rx_Request",
	    "sp+5 'ptr=' Pointer , sp+4 'chan=' @W .W , '!' sp+2 @L 'flag=' @B .B",
	    "sp+0 @L 'flag=' @B .B",
	},
	{ 0x10240, "`KC20_Estop",
	    "",
	    "",
	},
	{ 0x1029c, "`Malloc1",
	    "sp+2 'length=' @L .L",
	    "'>' sp+2 Pointer",
	},
	{ 0x102a0, "`Malloc2",
	    "'!' sp+3 @L 'dst=' Pointer , sp+2 'length=' @W .W",
	    "sp+1 @L 'dst=' Pointer",
	},
	{ 0x102a4, "`Free1",
	    "sp+4 'a=' Pointer , sp+2 'b=' @L .L",
	    "",
	},
	{ 0x102a8, "`Free2",
	    "sp+4 'a=' Pointer , sp+2 'b=' @L .L",
	    "",
	},
	{ 0x102b8, "`NewString",
	    "'!' sp+2 @L 'a=' String",
	    "sp+0 @L 'a=' String",
	},
	{ 0x102bc, "`FreeString",
	    "'!' sp+2 @L 'a=' String",
	    "sp+0 @L 'a=' String",
	},
	{ 0x102c0, "`AppendChar",
	    "sp+3 'b=' String , sp+2 'a=' @B .B",
	    "sp+1 'b=' String",
	},
	{ 0x102c4, "`StringLit",
	    "sp+4 'Src=' Pointer , sp+3 'Offset=' @W .W , sp+2 'Len=' @W .W",
	    "'>' sp+4 String",
	},
	{ 0x102c8, "`StringEqual",
	    "sp+4 'a=' String , sp+2 'b=' String",
	    "'>' sp+4 @B .B",
	},
	{ 0x102cc, "`StringDup",
	    "sp+2 'a=' String",
	    "'>' sp+2 String",
	},
	{ 0x102d0, "`StringCat2",
	    "sp+4 'a=' String , sp+2 'b=' String",
	    "'>' sp+4 String",
	},
	{ 0x102d4, "`StringCat3",
	    "sp+6 'a=' String , sp+4 'b=' String , sp+2 'c=' String",
	    "'>' sp+6 String",
	},
	{ 0x102d8, "`StringCat4",
	    "sp+8 'a=' String , sp+6 'b=' String , sp+4 'c=' String , sp+2 'd=' String",
	    "'>' sp+8 String",
	},
	{ 0x102dc, "`StringCat5",
	    "sp+10 'a=' String , sp+8 'b=' String , sp+6 'c=' String , sp+4 'd=' String , sp+2 'e=' String",
	    "'>' sp+10 String",
	},
	{ 0x102e0, "`StringCat6",
	    "sp+12 'a=' String , sp+10 'b=' String , sp+8 'c=' String , sp+6 'd=' String , sp+4 'e=' String , sp+2 'f=' String",
	    "'>' sp+12 String",
	},
	{ 0x102e4, "`Long2String",
	    "sp+2 'a=' @L .L",
	    "'>' sp+2 String",
	},
	{ 0x102e8, "`Long2HexString",
	    "sp+4 'val=' @L .L , sp+2 'ndig=' @L .L",
	    "'>' sp+4 String",
	},
	{ 0x102ec, "`String2Long",
	    "sp+6 'src=' String , '!' sp+4 @L 'status=' @B .B , '!' sp+2 @L 'retval=' @L .L",
	    "sp+2 @L 'status=' @B .B , sp+0 @L 'retval=' @L .L",
	},
	{ 0x102f0, "`ToUpper",
	    "sp+2 'a=' String",
	    "'>' sp+2 String",
	},
	{ 0x102f4, "`RightPad",
	    "sp+4 'a=' String , sp+2 'b=' @L .L",
	    "'>' sp+4 String",
	},
	{ 0x102f8, "`LeftPad",
	    "sp+4 'a=' String , sp+2 'b=' @L .L",
	    "'>' sp+4 String",
	},
	{ 0x102fc, "`FirstField",
	    "sp+6 'input=' String , sp+4 'output=' String , '!' sp+2 @L 'c=' @B .B",
	    "sp+4 'input=' String , sp+2 'output=' String , sp+0 @L 'c=' @B .B",
	},
	{ 0x10304, "`GetRtc",
	    "",
	    "'>' sp+0 TimeStamp",
	},
	{ 0x1030c, "`SetRtc",
	    "sp+2 'a=' TimeStamp",
	    "",
	},
	{ 0x10310, "`ConvertTimestamp",
	    "sp+6 'input=' String , sp+4 'b=' @L .L , '!' sp+2 @L 'status=' @B .B",
	    "sp+4 'input=' String , sp+0 @L 'status=' @B .B",
	},
	{ 0x10314, "`Add",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x10318, "`Subtract",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x1031c, "`Multiply",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x10320, "`Divide",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x10324, "`IsGreater",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @B .B",
	},
	{ 0x10328, "`IsSmaller",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @B .B",
	},
	{ 0x1032c, "`IsEqual",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @B .B",
	},
	{ 0x10330, "`BitAnd",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x10334, "`BitOr",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x10338, "`BitNot",
	    "sp+2 'a=' @Q .Q",
	    "'>' sp+4 @Q .Q",
	},
	{ 0x1033c, "`Negate",
	    "sp+2 'a=' @Q .Q",
	    "'>' sp+4 @Q .Q",
	},
	{ 0x10340, "`BitXor",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x10344, "`BitShift",
	    "sp+4 'a=' @Q .Q , sp+2 'howmuch=' @L .L",
	    "'>' sp+6 @Q .Q",
	},
	{ 0x10350, "`Quad2Long",
	    "sp+2 'a=' @Q .Q",
	    "'>' sp+4 @L .L",
	},
	{ 0x10354, "`Long2Quad",
	    "sp+2 'a=' @L .L",
	    "'>' sp+2 @Q .Q",
	},
	{ 0x10358, "`Modulus",
	    "sp+6 'a=' @Q .Q , sp+2 'b=' @Q .Q",
	    "'>' sp+8 @Q .Q",
	},
	{ 0x1035c, "`Quad2String",
	    "sp+4 'a=' @Q .Q , sp+2 'radix=' @L .L",
	    "'>' sp+6 String",
	},
	{ 0x10368, "`Lba2Chs",
	    "sp+6 'lba=' @W .W , '!' sp+4 @L 'cyl=' @W .W , '!' sp+2 @L 'hd_sec=' @W .W",
	    "sp+2 @L 'cyl=' @W .W , sp+0 @L 'hd_sec=' @W .W",
	},
	{ 0x1036c, "`RW_Sectors",
	    "sp+9 'oper=' @B .B , sp+8 'lba=' @W .W , sp+6 'cnt=' @L .L , sp+4 'ptr=' Pointer , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x10370, "`ReadWords",
	    "sp+8 'lba=' @W .W , sp+7 'offset=' @W .W , sp+5 'ptr=' @L .L , sp+4 'nwords=' @W .W , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x10374, "`WriteWords",
	    "sp+8 'lba=' @W .W , sp+7 'offset=' @W .W , sp+5 'ptr=' @L .L , sp+4 'nwords=' @W .W , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x10378, "`FS10378",
	    "sp+5 'a=' Dirent , sp+4 'b=' @B .B , '!' sp+2 @L 'c=' @B .B",
	    "sp+3 'a=' Dirent , sp+0 @L 'c=' @B .B",
	},
	{ 0x1037c, "`FS1037c",
	    "sp+2 'a=' Dirent",
	    "sp+0 'a=' Dirent",
	},
	{ 0x10380, "`OpenFile",
	    "sp+10 'name=' String , sp+9 'a=' @W .W , sp+8 'b=' @B .B , sp+6 'c=' @L .L , '!' sp+4 @L 'status=' @B .B , '!' sp+2 @L 'file=' Dirent",
	    "sp+2 @L 'status=' @B .B , sp+0 @L 'file=' Dirent",
	},
	{ 0x10384, "`ReadFile",
	    "sp+10 'file=' Dirent , sp+9 'w=' @W .W , sp+8 'x=' @W .W , sp+7 'a=' @W .W , sp+6 'b=' @B .B , sp+4 'c=' @L .L , sp+2 'd=' @L .L",
	    "",
	},
	{ 0x10388, "`WriteFile",
	    "sp+10 'file=' Dirent , sp+9 'y=' @W .W , sp+8 'x=' @W .W , sp+7 'a=' @W .W , sp+6 'b=' @B .B , sp+4 'c=' @L .L , sp+2 'd=' @L .L",
	    "",
	},
	{ 0x1038c, "`CloseFile",
	    "sp+6 'a=' @L .L , '!' sp+4 @L 'status=' @B .B , '!' sp+2 @L 'file=' Dirent",
	    "sp+2 @L 'status=' @B .B , sp+0 @L 'file=' Dirent",
	},
	{ 0x10390, "`WriteFreeList",
	    "",
	    "",
	},
	{ 0x10394, "`MountDisk",
	    "sp+4 'drive=' @W .W , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x1039c, "`InitProg",
	    "",
	    "",
	},
	{ 0x103a0, "`FsErrMsgStr",
	    "sp+2 'err=' @B .B",
	    "'>' sp+1 String",
	},
	{ 0x103a4, "`Open_ERROR_LOG",
	    "",
	    "",
	},
	{ 0x103a8, "`Write_ERROR_LOG",
	    "'!' sp+4 @L 'a=' @B .B , sp+2 'b=' Pointer",
	    "sp+2 @L 'a=' @B .B , sp+0 'b=' Pointer",
	},
	{ 0x103ac, "`Set_is_open_ERROR_LOG",
	    "sp+2 'a=' @B .B",
	    "",
	},
	{ 0x103b0, "`PushProgram",
	    "sp+7 'a=' String , sp+5 'b=' String , sp+4 'c=' @B .B , '!' sp+2 @L 'd=' @B .B",
	    "sp+2 'c=' @B .B , sp+0 @L 'd=' @B .B",
	},
	{ 0x103b4, "`WriteProgToSwapFile",
	    "sp+4 'prog=' String , sp+2 'args=' String",
	    "",
	},
	{ 0x103b8, "`PopProgram",
	    "sp+4 'status=' @B .B , sp+2 'msg=' String",
	    "",
	},
	{ 0x103bc, "`?FS103bc",
	    "sp+4 'a=' String , '!' sp+2 @L 'b=' @B .B",
	    "'>' sp+4 @B .B , sp+2 'a=' String , sp+0 @L 'b=' @B .B",
	},
	{ 0x103c0, "`ExpErrMsg",
	    "sp+2 'a=' @B .B",
	    "'>' sp+1 String",
	},
	{ 0x103c4, "`GetArgv",
	    "",
	    "'>' sp+0 String",
	},
	{ 0x103cc, "`GetPushLevel",
	    "",
	    "'>' sp+0 @L .L",
	},
	{ 0x103d0, "`WriteConsoleChar",
	    "sp+2 'chr=' @B .B",
	    "",
	},
	{ 0x103d4, "`ReadChar",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x103d8, "`WriteConsoleString",
	    "sp+2 'str=' String",
	    "",
	},
	{ 0x103dc, "`WriteConsoleCrLf",
	    "",
	    "",
	},
	{ 0x103e0, "`WriteConsoleStringCrLf",
	    "sp+2 'str=' String",
	    "",
	},
	{ 0x103e4, "`AskConsoleString",
	    "sp+2 'prompt=' String",
	    "'>' sp+2 String",
	},
	{ 0x103e8, "`AskOnConsoleInt",
	    "sp+2 'prompt=' String",
	    "'>' sp+2 @L .L",
	},
	{ 0x103ec, "`AskOnConsoleIntRange",
	    "sp+6 'prompt=' String , sp+4 'low=' @L .L , sp+2 'High=' @L .L",
	    "'>' sp+6 @L .L",
	},
	{ 0x103f0, "`AskOnConsoleYesNo",
	    "sp+3 'prompt=' String , sp+2 'default=' @B .B",
	    "'>' sp+3 @B .B",
	},
	{ 0x103f4, "`SetConsoleConfig",
	    "sp+2 'a=' @L .L",
	    "",
	},
	{ 0x103f8, "`GetConsoleConfig",
	    "",
	    "'>' sp+0 @L .L",
	},
	{ 0x103fc, "`SetConsolePrinter",
	    "sp+4 'a=' @B .B , sp+3 'b=' @W .W , sp+2 'c=' @W .W",
	    "",
	},
	{ 0x10404, "`SetSomeKindOfFlag",
	    "sp+2 'a=' @B .B",
	    "",
	},
	{ 0x10424, "`TapeErrorMsg",
	    "sp+2 'a=' @B .B",
	    "'>' sp+1 String",
	},
	{ 0x1043c, "`FileReadLine",
	    "sp+6 'file=' Dirent , '!' sp+4 @L 'a=' String , '!' sp+2 @L 'b=' @B .B",
	    "sp+2 @L 'a=' String , sp+0 @L 'b=' @B .B",
	},
	{ 0x1044c, "`WriteErrorMessage",
	    "sp+6 'file=' String , sp+4 'txt=' String , sp+2 'number=' @L .L",
	    "'>' sp+6 @B .B",
	},
	{ 0x10454, "`Glob",
	    "sp+4 'input=' String , sp+2 'pattern=' String",
	    "'>' sp+4 @B .B",
	},
	{ 0x10458, "`DirFirst",
	    "sp+6 'c=' @B .B , sp+4 'a=' String , '!' sp+2 @L 'b=' Dirent",
	    "sp+4 'c=' @B .B , sp+0 @L 'b=' Dirent",
	},
	{ 0x1045c, "`DirNext",
	    "sp+4 'a=' @B .B , '!' sp+2 @L 'b=' Dirent",
	    "sp+2 'a=' @B .B , sp+0 @L 'b=' Dirent",
	},
	{ 0x10460, "`ExpLoad",
	    "sp+4 'a=' String , sp+2 'b=' Pointer",
	    "",
	},
	{ 0x10466, "`ExpInputParam",
	    "sp+6 'exp=' Pointer , sp+4 'ptr=' Pointer , sp+2 'len=' @L .L",
	    "",
	},
	{ 0x1046c, "`ExpInputFlag",
	    "sp+3 'exp=' Pointer , sp+2 'val=' @W .W",
	    "",
	},
	{ 0x10472, "`ExpOutputParam",
	    "sp+8 'exp=' Pointer , sp+6 'b=' Pointer , sp+4 'c=' @L .L , sp+2 'd=' @L .L",
	    "",
	},
	{ 0x10478, "`ExpOutputFlag",
	    "sp+4 'exp=' Pointer , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x1047e, "`ExpXmit",
	    "sp+4 'adr=' @B .B , sp+2 'b=' Pointer",
	    "",
	},
	{ 0x10484, "`DiProcPing",
	    "sp+8 'adr=' @B .B , '!' sp+6 @L 'status=' @B .B , '!' sp+4 @L 'b80=' @B .B , '!' sp+2 @L 'b40=' @B .B",
	    "sp+4 @L 'status=' @B .B , sp+2 @L 'b80=' @B .B , sp+0 @L 'b40=' @B .B",
	},
	{ 0x1048a, "`DiProcCmd",
	    "sp+3 'board=' @B .B , sp+2 'cmd=' @B .B",
	    "",
	},
	{ 0x10490, "`ExpUpload",
	    "sp+6 'adr=' @B .B , sp+4 'ptr=' Pointer , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x10496, "`ExpClose",
	    "sp+2 'exp=' Pointer",
	    "",
	},
	{ 0x1049c, "`BoardName",
	    "sp+2 'address=' @B .B",
	    "'>' sp+1 String",
	},
	{ 0x104a8, "`?FS104a8",
	    "sp+12 'VAR=' Pointer , sp+10 'b=' @L .L , sp+8 'c=' @L .L , sp+6 'VAR=' Pointer , sp+4 'e=' @L .L , sp+2 'f=' @L .L",
	    "'>' sp+12 @B .B",
	},
	{ 0x104b4, "`?FS104b4",
	    "'!' sp+8 @L 'a=' @L .L , sp+6 'b=' @L .L , sp+4 'c=' @L .L , '!' sp+2 @L 'd=' @Q .Q",
	    "sp+6 @L 'a=' @L .L , sp+2 'c=' @L .L , sp+0 @L 'd=' @Q .Q",
	},
	{ 0x104ba, "`ExpRun",
	    "sp+5 'a=' @B .B , sp+4 'adr=' @B .B , sp+2 'b=' Pointer",
	    "",
	},
	{ 0x104c0, "`HasBoard",
	    "sp+2 'diproc_addr=' @B .B",
	    "'>' sp+1 @B .B",
	},
	{ 0x104c6, "`EQ_1c218",
	    "sp+2 'a=' @B .B",
	    "'>' sp+1 @B .B",
	},
	{ 0x104cc, "`MemOnly2MB",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x104d2, "`SetExpInitDone",
	    "sp+2 'a=' @B .B",
	    "",
	},
	{ 0x104d8, "`ExpInit",
	    "sp+2 'a=' @L .L",
	    "",
	},
	{ 0x104de, "`Get20028",
	    "",
	    "'>' sp+0 @L .L",
	},
	{ 0x104e4, "`FindWord",
	    "sp+4 'src=' Pointer , sp+3 'x=' @W .W , sp+2 'length=' @W .W",
	    "'>' sp+4 @B .B",
	},
	{ 0x104ea, "`FillWords",
	    "sp+4 'dst=' Pointer , sp+3 'x=' @W .W , sp+2 'length=' @W .W",
	    "",
	},
	{ 0x104f0, "`SwapBytes",
	    "sp+5 'src=' Pointer , sp+3 'dst=' Pointer , sp+2 'words=' @W .W",
	    "",
	},
	{ 0x104f6, "`CopyBytes",
	    "sp+5 'src=' Pointer , sp+3 'dst=' Pointer , sp+2 'bytes=' @W .W",
	    "",
	},
	{ 0x104fc, "`IPC_PutVar",
	    "sp+6 'src=' Pointer , sp+4 'length=' @L .L , sp+2 'type=' @L .L",
	    "",
	},
	{ 0x10502, "`IPC_PutBool",
	    "sp+2 'a=' @B .B",
	    "",
	},
	{ 0x10508, "`IPC_PutString",
	    "sp+2 'a=' String",
	    "",
	},
	{ 0x1050e, "`IPC_PutLong",
	    "sp+2 'a=' @L .L",
	    "",
	},
	{ 0x10514, "`IPC_PutEnd",
	    "",
	    "",
	},
	{ 0x1051a, "`IPC_GetEnd",
	    "",
	    "",
	},
	{ 0x10520, "`IPC_GetVar",
	    "sp+6 'dst=' Pointer , sp+4 'length=' @L .L , sp+2 'type=' @L .L",
	    "sp+4 'dst=' Pointer",
	},
	{ 0x10526, "`IPC_GetBool",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x1052c, "`IPC_GetString",
	    "'!' sp+2 @L 'retval=' String",
	    "sp+0 @L 'retval=' String",
	},
	{ 0x10532, "`IPC_GetLong",
	    "",
	    "'>' sp+0 @L .L",
	},
	{ 0x10538, "`IPC_Init",
	    "",
	    "",
	},
	{ 0x10544, "`IPC_InitGetTwoBools",
	    "'!' sp+4 @L 'a=' @B .B , '!' sp+2 @L 'b=' @B .B",
	    "sp+2 @L 'a=' @B .B , sp+0 @L 'b=' @B .B",
	},
	{ 0x1054a, "`?IPC_Puts",
	    "sp+11 'a=' @B .B , sp+9 'b=' String , sp+7 'c=' String , sp+6 'd=' @B .B , sp+4 'e=' @L .L , sp+2 'f=' @L .L",
	    "",
	},
	{ 0x10550, "`?ExecFRU",
	    "'!' sp+10 @L 'a=' @L .L , '!' sp+8 @L 'b=' @W .W , '!' sp+6 @L 'c=' @L .L , '!' sp+4 @L 'd=' @L .L , '!' sp+2 @L 'e=' @B .B",
	    "sp+8 @L 'a=' @L .L , sp+6 @L 'b=' @W .W , sp+4 @L 'c=' @L .L , sp+2 @L 'd=' @L .L , sp+0 @L 'e=' @B .B",
	},
	{ 0x10556, "`?IPC_GetStd",
	    "sp+6 'a=' Pointer , '!' sp+4 @L 'b=' @B .B , '!' sp+2 @L 'c=' @B .B",
	    "sp+4 'a=' Pointer , sp+2 @L 'b=' @B .B , sp+0 @L 'c=' @B .B",
	},
	{ 0x10562, "`?IPC_GetVar4xBool",
	    "'!' sp+10 @L 'a=' Pointer , '!' sp+8 @L 'b=' @B .B , '!' sp+6 @L 'c=' @B .B , '!' sp+4 @L 'd=' @B .B , '!' sp+2 @L 'e=' @B .B",
	    "sp+8 @L 'a=' Pointer , sp+6 @L 'b=' @B .B , sp+4 @L 'c=' @B .B , sp+2 @L 'd=' @B .B , sp+0 @L 'e=' @B .B",
	},
	{ 0x1056e, "`Read_ConfigFile",
	    "sp+8 'name=' String , sp+6 'version=' @L .L , sp+4 'dst=' Pointer , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x10574, "`Write_ConfigFile",
	    "sp+4 'name=' String , sp+2 'dst=' Pointer",
	    "",
	},
	{ 0x1057a, "`Read_HARDWARE.M200_CONFIG",
	    "sp+4 'a=' Pointer , '!' sp+2 @L 'status=' @B .B",
	    "sp+0 @L 'status=' @B .B",
	},
	{ 0x10580, "`Write_HARDWARE.M200_CONFIG",
	    "sp+2 'a=' Pointer",
	    "",
	},
	{ 0x10586, "`Config_Entry_Name",
	    "sp+2 'a=' @B .B",
	    "'>' sp+1 String",
	},
	{ 0x10592, "`ReadConfig",
	    "sp+2 'where=' @L .L",
	    "'>' sp+2 @W .W",
	},
	{ 0x10598, "`WriteConfig",
	    "sp+4 'what=' @W .W , sp+2 'where=' @L .L",
	    "",
	},
	{ 0x1059e, "`ReadClusterNo",
	    "'!' sp+2 @L 'a=' @L .L",
	    "sp+0 @L 'a=' @L .L",
	},
	{ 0x105a4, "`Read_fc0c",
	    "",
	    "'>' sp+0 @W .W",
	},
	{ 0x105aa, "`Read_fc00",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x105b0, "`FifoInit",
	    "",
	    "",
	},
	{ 0x105b6, "`R1000_Reset_L",
	    "",
	    "",
	},
	{ 0x105bc, "`R1000_Reset_H",
	    "",
	    "",
	},
	{ 0x105c2, "`Or_fc0c_80",
	    "",
	    "",
	},
	{ 0x105c8, "`And_fc0c_7f",
	    "",
	    "",
	},
	{ 0x105ce, "`ReadKeySwitch",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x105d4, "`Update_fc0c",
	    "sp+2 'new=' @B .B",
	    "",
	},
	{ 0x105da, "`Set_fc01",
	    "sp+2 'a=' @B .B",
	    "",
	},
	{ 0x105e0, "`Get_fc01",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x105e6, "`Set_fc04_to_01",
	    "",
	    "",
	},
	{ 0x105ec, "`Get_fc05",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x105f2, "`Get_fc02",
	    "",
	    "'>' sp+0 @W .W",
	},
	{ 0x105f8, "`Is_fc07_one",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x105fe, "`Is_fc07_two",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x10604, "`Is_fc07_three",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x1060a, "`Is_fc07_four",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x10610, "`Is_fc07_one_or_three",
	    "",
	    "'>' sp+0 @B .B",
	},
	{ 0x10616, "`Is_fc07_two_or_four",
	    "",
	    "'>' sp+0 @B .B",
	},
