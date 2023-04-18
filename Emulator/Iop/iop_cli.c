#include <fcntl.h>
#include <pthread.h>
#include <string.h>
#include <stdio.h>

#include "Infra/r1000.h"
#include "Iop/iop.h"

static const struct cli_cmds cli_ioc_cmds[] = {
	{ "breakpoint",		cli_ioc_breakpoint },
	{ "config",		cli_ioc_config },
	{ "dump",		cli_ioc_dump },
	{ "maxins",		cli_ioc_maxins },
	{ "memtrace",		cli_ioc_memtrace },
	{ "reset",		cli_ioc_reset },
	{ "syscall",		cli_ioc_syscall },
	{ "step",		cli_ioc_step },
	{ "stop",		cli_ioc_stop },
	{ "start",		cli_ioc_start },
	{ "switch",		cli_ioc_switch },
	{ NULL,			NULL },
};

void v_matchproto_(cli_func_f)
cli_ioc(struct cli *cli)
{

	Cli_Dispatch(cli, cli_ioc_cmds);
}
