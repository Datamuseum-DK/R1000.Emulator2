/*-
 * Copyright (c) 2022 Poul-Henning Kamp
 * All rights reserved.
 *
 * Author: Poul-Henning Kamp <phk@phk.freebsd.dk>
 *
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 */

#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <fnmatch.h>
#include <unistd.h>

#include "Infra/r1000.h"
#include "Infra/vend.h"
#include "Iop/iop_scsi.h"

#define DFS_NAME_LEN 30
#define DFS_DIRENT_LEN 64

struct dfs_dirent {
	char		name[DFS_NAME_LEN + 1];
	uint16_t	hash;
	uint16_t	used_sec;
	uint16_t	alloc_sec;
	uint16_t	first_sec;
	uint16_t	time;
	uint16_t	date;
	uint16_t	flags;
	uint8_t		*ptr;
	unsigned	size;

	uint8_t		data[64];
};

#define N_DIR_STANZA 8

struct dfs_superblock {
	struct {
		uint16_t	magic;
		uint16_t	freeblk;
		uint16_t	dirstanza[N_DIR_STANZA];
	} sec4[1];
	unsigned next_sz;
	unsigned next_sec;
	unsigned next_de;
};

/**********************************************************************/

static const char * const month[16] = {
	"0x0", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
	"AUG", "SEP", "OCT", "NOV", "DEC", "0xd", "0xe", "0xf",
};

static void
dfs_render_dirent(struct cli *cli, struct dfs_dirent *de)
{
	unsigned dd, mm, yy;

	Cli_Printf(cli, "%-30.30s ", de->name);
	Cli_Printf(cli, "%04x ", de->hash);
	Cli_Printf(cli, "%04x ", de->used_sec);
	Cli_Printf(cli, "%04x ", de->alloc_sec);
	Cli_Printf(cli, "%04x ", de->first_sec);
	Cli_Printf(cli, "%02d:", (de->time<<1) / 3600);
	Cli_Printf(cli, "%02d:", ((de->time<<1) / 60) % 60);
	Cli_Printf(cli, "%02d ", (de->time<<1) % 60);

	// ((YYYY - 1901) << 9) | (MM << 5) | DD
	dd = de->date & 0x1f;
	mm = (de->date >> 5) & 0x0f;
	yy = (de->date >> 9) + 1;
	Cli_Printf(cli, "%02d-%s-%02d ", dd, month[mm], yy);
	Cli_Printf(cli, "%04x\n", de->flags);
}

/**********************************************************************/

static uint8_t *
dfs_read_sect(unsigned secno)
{
	void *p;

	p = scsi_disk_pointer_to_sector(0, secno);
	AN(p);
	return (p);
}

static struct dfs_superblock *
dfs_read_super_block(void)
{
	struct dfs_superblock *dsb;
	uint8_t *bp;
	unsigned u;

	dsb = calloc(sizeof *dsb, 1);
	AN(dsb);
	bp = dfs_read_sect(4);
	dsb->sec4->magic = vbe16dec(bp);
	dsb->sec4->freeblk = vbe16dec(bp + 2);
	for (u = 0; u < N_DIR_STANZA; u++)
		dsb->sec4->dirstanza[u] = vbe16dec(bp + 4 + 2 * u);

	assert(dsb->sec4->magic == 0x7fed);
	return (dsb);
}

static int
dfs_iter_dirent(void **priv, struct dfs_dirent *de)
{
	struct dfs_superblock *dsb;
	uint8_t *bp;
	unsigned u;

	if (*priv == NULL) {
		dsb = dfs_read_super_block();
		AN(dsb);
		*priv = dsb;
	} else {
		dsb = *priv;
	}
	do {
		if (dsb->next_sz == N_DIR_STANZA) {
			free(dsb);
			*priv = NULL;
			return (0);
		}
		bp = dfs_read_sect(
		    dsb->sec4->dirstanza[dsb->next_sz] + dsb->next_sec
		);
		bp += dsb->next_de;
		dsb->next_de += DFS_DIRENT_LEN;
		if (dsb->next_de == (1<<10)) {
			dsb->next_de = 0;
			dsb->next_sec++;
		}
		if (dsb->next_sec == (1<<8)) {
			dsb->next_sec = 0;
			dsb->next_sz++;
		}
	} while (*bp == 0xff);

	memcpy(de->data, bp, sizeof de->data);

	memcpy(de->name, bp, DFS_NAME_LEN);
	de->name[DFS_NAME_LEN] = '\0';

	de->hash = vbe16dec(bp + 30);
	de->used_sec = vbe16dec(bp + 32);
	de->size = ((unsigned)de->used_sec) << 10;
	de->alloc_sec = vbe16dec(bp + 34);
	de->first_sec = vbe16dec(bp + 36);
	for (u = 38; u < 58; u++)
		assert(bp[u] == 0);
	de->time = vbe16dec(bp + 58);
	de->date = vbe16dec(bp + 60);
	de->flags = vbe16dec(bp + 62);
	de->ptr = dfs_read_sect(de->first_sec);
	return(1);
}

static int
dfs_file_has_nul(const struct dfs_dirent *de)
{
	unsigned u;

	// Check that there are NUL characters in the file
	for (u = 0; u < de->size; u++) {
		if (!de->ptr[u])
			return (1);
	}
	return (0);
}

/**********************************************************************/

static int
dfs_open(const char *filename, struct dfs_dirent *dep, int flags)
{
	void *iter = NULL;

	AZ(flags);
	struct dfs_dirent de[2];

	while(dfs_iter_dirent(&iter, de)) {
		if (!strcasecmp(de->name, filename)) {
			*dep = de[0];
			while(dfs_iter_dirent(&iter, de + 1))
				continue;
			return(0);
		}
	}
	errno = ENOENT;
	return (-1);
}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_dfs_cat(struct cli *cli)
{
	struct dfs_dirent de[1];
	FILE *fout;

	if (cli->help || cli->ac < 2 || cli->ac > 3) {
		Cli_Usage(cli, "<dfs_filename> [<filename>]",
		    "Cat the contents of dfs_filename to stdout or filename.");
		return;
	}

	if (dfs_open(cli->av[1], de, 0)) {
		Cli_Error(cli,
		    "Cannot open DFS file '%s': %s\n",
		    cli->av[1], strerror(errno)
		);
		return;
	}

	dfs_render_dirent(cli, de);

	if (cli->ac == 3) {
		fout = fopen(cli->av[2], "w");
		if (fout == NULL) {
			Cli_Error(cli,
			    "Cannot open '%s' for writing: %s\n",
			    cli->av[2], strerror(errno)
			);
		} else {
			if (dfs_file_has_nul(de))
				(void)fputs((char*)de->ptr, fout);
			else
				(void)fwrite(de->ptr, 1, de->size, fout);
			AZ(fclose(fout));
		}
	} else {
		if (dfs_file_has_nul(de))
			(void)puts((char*)de->ptr);
		else
			(void)fwrite(de->ptr, 1, de->size, stdout);
	}
}

/**********************************************************************/

static int
dfs_de_compare(const void *a, const void *b)
{
	return (
	    strcmp(
		((const struct dfs_dirent*)a)->name,
		((const struct dfs_dirent*)b)->name
	    )
	);
}

static void v_matchproto_(cli_func_f)
cli_dfs_dir(struct cli *cli)
{
	void *iter = NULL;
	struct dfs_dirent de[4096], *dep;
	int nde = 0, i;

	if (cli->help) {
		Cli_Usage(cli, "[<glob> …]",
		    "List DFS directory optionally matching pattern(s).");
		return;
	}

	dep = de;
	while(dfs_iter_dirent(&iter, dep)) {
		if (cli->ac == 1) {
			dep++;
			nde++;
			continue;
		}
		for (i = 1; i < cli->ac; i++) {
			if (fnmatch(cli->av[i], dep->name, 0))
				continue;
			dep++;
			nde++;
			break;
		}
	}
	qsort(de, nde, sizeof de[0], dfs_de_compare);
	for (i = 0; i < nde; i++)
		dfs_render_dirent(cli, de + i);
}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_dfs_read(struct cli *cli)
{
	struct dfs_dirent de[1];
	FILE *fout;

	if (cli->help || cli->ac != 3) {
		Cli_Usage(cli, "<dfs_filename> <filename>",
		    "Read the contents of dfs_filename into filename.");
		return;
	}

	if (dfs_open(cli->av[1], de, 0)) {
		Cli_Error(cli,
		    "Cannot open DFS file '%s': %s\n",
		    cli->av[1], strerror(errno)
		);
		return;
	}

	dfs_render_dirent(cli, de);

	fout = fopen(cli->av[2], "w");
	if (fout == NULL) {
		Cli_Error(cli,
		    "Cannot open '%s' for writing: %s\n",
		    cli->av[2], strerror(errno)
		);
	} else {
		(void)fwrite(de->ptr, 1, de->size, fout);
		AZ(fclose(fout));
	}
}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_dfs_neuter(struct cli *cli)
{
	struct dfs_dirent de[1];
	char *p, *q;
	unsigned adr, start;

	if (cli->help || cli->ac != 2) {
		Cli_Usage(cli, "<dfs_experiment>",
		    "Make the dfs_experiment a no-op returning success.");
		return;
	}

	if (dfs_open(cli->av[1], de, 0)) {
		Cli_Error(cli,
		    "Cannot open DFS file '%s': %s\n",
		    cli->av[1], strerror(errno)
		);
		return;
	}

	dfs_render_dirent(cli, de);
	p = (char*)de->ptr;
	adr = 0x10;
	start = 0;
	while (*p != '\0') {
		q = strchr(p, '\n');
		AN(q);
		if (*p == 'P') {
			p = q + 1;
			continue;
		}
		if (*p == '\r' || *p == '\n') {
			p = q + 1;
			continue;
		}
		if (!isxdigit(p[0]) ||
		    !isxdigit(p[1])) {
			Cli_Error(cli,
			    "Dont understand line at address 0x%x\n", adr
			);
			return;
		}
		if (start == 0)
			assert (sscanf(p, "%x", &start) == 1);
		else if (adr == start) {
			memcpy(p, "64\r\n5C\r\n", 8);
			break;
		}
		adr += 1;
		p = q + 1;
	}

}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_dfs_patch(struct cli *cli)
{
	struct dfs_dirent de[1];
	unsigned offset, val;
	int i;
	char *err;

	if (cli->help || cli->ac < 3) {
		Cli_Usage(cli, "<offset> <byte>…", "Write bytes at offset.");
		return;
	}

	if (dfs_open(cli->av[1], de, 0)) {
		Cli_Error(cli,
		    "Cannot open DFS file '%s': %s\n",
		    cli->av[1], strerror(errno)
		);
		return;
	}

	dfs_render_dirent(cli, de);

	err = NULL;
	offset = strtoul(cli->av[2], &err, 0);
	if ((err != NULL && *err != '\0')) {
		Cli_Error(cli, "Cannot grog <offset>");
		return;
	}
	if (offset >= ((unsigned)de->used_sec) << 10) {
		Cli_Error(cli, "<offset> past end of dfs-file.");
		return;
	}

	for (i = 3; cli->av[i] != NULL; i++) {
		err = NULL;
		val = strtoul(cli->av[i], &err, 0);
		if ((err != NULL && *err != '\0') || val > 255) {
			Cli_Error(cli, "Cannot grog <byte> (%s)", cli->av[i]);
			return;
		}
		de->ptr[offset++] = val;
	}
}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_dfs_sed(struct cli *cli)
{
	struct dfs_dirent de[1];
	char buf[BUFSIZ];
	unsigned u;
	int i;
	char templ1[] = "/tmp/temp.XXXXXX";
	int fd1;
	char templ2[] = "/tmp/temp.XXXXXX";
	int fd2;
	FILE *pfd;
	ssize_t sz, sza;

	if (cli->help || cli->ac < 3) {
		Cli_Usage(cli, "<dfs_filename> <sed_cmd> …",
		    "Edit dfs_filename with sed(1).");
		return;
	}

	if (dfs_open(cli->av[1], de, 0)) {
		Cli_Error(cli,
		    "Cannot open DFS file '%s': %s\n",
		    cli->av[2], strerror(errno)
		);
		return;
	}
	if (!dfs_file_has_nul(de)) {
		Cli_Error(cli,
		    "DFS file '%s' is not a text file\n",
		    cli->av[2]
		);
		return;
	}
	for (u = 0; u < de->size; u++) {
		if (de->ptr[u] > 0x7e) {
			Cli_Error(cli,
			    "DFS file '%s' is not a text file\n",
			    cli->av[2]
			);
			return;
		}
	}

	dfs_render_dirent(cli, de);
	fd1 = mkstemp(templ1);
	assert(fd1 > 0);
	fd2 = mkstemp(templ2);
	assert(fd2 > 0);
	(void)write(fd1, de->ptr, strlen((char*)(de->ptr)));
	for (i = 2; i < cli->ac; i++) {
		(void)write(fd2, cli->av[i], strlen(cli->av[i]));
		(void)write(fd2, "\n", 1);
	}
	bprintf(buf, "sed -f %s %s", templ2, templ1);
	AZ(close(fd1));
	AZ(close(fd2));
	pfd = popen(buf, "r");
	AN(pfd);
	sza = 0;
	while (sza < de->size) {
		sz = fread(de->ptr + sza, 1, de->size - sza, pfd);
		if (sz <= 0)
			break;
		sza += sz;
	}
	if (sza < de->size)
		de->ptr[sza] = '\0';
	AZ(pclose(pfd));
	AZ(unlink(templ1));
	AZ(unlink(templ2));
	if (sza == de->size)
		Cli_Error(cli, "Edit extend past dfs file allocation\n");
}

/**********************************************************************/

static void v_matchproto_(cli_func_f)
cli_dfs_write(struct cli *cli)
{
	struct dfs_dirent de[1];
	FILE *fout;
	size_t sz;

	if (cli->help || cli->ac != 3) {
		Cli_Usage(cli, "<filename> <dfs_filename>",
		    "Write the contents of filename into dfs_filename.");
		return;
	}

	if (dfs_open(cli->av[2], de, 0)) {
		Cli_Error(cli,
		    "Cannot open DFS file '%s': %s\n",
		    cli->av[2], strerror(errno)
		);
		return;
	}

	dfs_render_dirent(cli, de);

	fout = fopen(cli->av[1], "r");
	if (fout == NULL) {
		Cli_Error(cli,
		    "Cannot open '%s' for reading: %s\n",
		    cli->av[1], strerror(errno)
		);
	} else {
		sz = fread(de->ptr, 1, de->size, fout);
		if (sz < de->size)
			de->ptr[sz] = '\0';
		AZ(fclose(fout));
	}
}

/**********************************************************************/

static const struct cli_cmds cli_dfs_cmds[] = {
	{ "cat",		cli_dfs_cat },
	{ "dir",		cli_dfs_dir },
	{ "neuter",		cli_dfs_neuter },
	{ "patch",		cli_dfs_patch },
	{ "read",		cli_dfs_read },
	{ "sed",		cli_dfs_sed },
	{ "write",		cli_dfs_write },
	{ NULL,			NULL },
};

void v_matchproto_(cli_func_f)
Cli_dfs(struct cli *cli)
{

	Cli_Dispatch(cli, cli_dfs_cmds);
}
