/*-
 * Copyright (c) 2021 Poul-Henning Kamp
 * All rights reserved.
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


#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

#include "Infra/r1000.h"
#include "Infra/context.h"

#ifndef MAP_NOSYNC	// OSX
#  define MAP_NOSYNC 0
#endif

static const ssize_t context_size = 50<<20;

static int context_fd = -1;
static uint8_t *context_start = NULL;
static uint8_t *context_ptr = NULL;
static const uint8_t *context_end = NULL;

void
CTX_init(const char *path)
{
	ssize_t sz, szl;
	char buf[BUFSIZ];
	void *ptr;

	bprintf(buf, "%s.ctx", path);
	context_fd = open(buf, O_RDWR | O_CREAT | O_TRUNC, 0644);
	if (context_fd < 0) {
		fprintf(stderr, "Cannot open %s for writing: %s\n",
		    buf, strerror(errno));
	}

	memset(buf, 0, sizeof buf);
	for (szl = 0; szl < context_size; ) {
		sz = sizeof buf;
		if (sz + szl > context_size)
			sz = context_size - szl;
		sz = write(context_fd, buf, sz);
		assert(sz > 0);
		szl += sz;
	}
	ptr = mmap(NULL, context_size, PROT_READ|PROT_WRITE,
	    MAP_SHARED | MAP_NOSYNC, context_fd, 0);
	assert(ptr != MAP_FAILED);
	context_start = ptr;
	context_ptr = ptr;
	context_end = context_ptr + context_size;
}

void *
CTX_Get(const char *ident, uint32_t length)
{

	struct ctx *ctx;

	assert(context_fd > -1);
	assert(sizeof *ctx == 128);
	assert(strlen(ident) + 1 <= sizeof ctx->ident);
	if (length & 0xf) {
		length |= 0xf;
		length += 1;
	}
	assert(context_ptr + length <= context_end);
	ctx = (void*)context_ptr;
	context_ptr += length;
	AN(ctx);
	ctx->magic = CTX_MAGIC;
	ctx->length = length;
	bprintf(ctx->ident, "%s", ident);
	return (ctx);
}

void *
CTX_GetRaw(const char *ident, uint32_t length)
{

	uint8_t *ptr;

        ptr = CTX_Get(ident, length + sizeof(struct ctx));
        return (ptr + sizeof(struct ctx));
}

struct ctx *
CTX_Iter(void **priv)
{
	struct ctx *retval;
	uint8_t **next = (uint8_t **)priv;

	if (*next == NULL)
		*next = context_start;
	if ((*next) >= context_ptr)
		retval = NULL;
	else {
		retval = (struct ctx *)(void*)(*next);
		assert(retval->length >= sizeof(*retval));
		*next += retval->length;
	}
	return (retval);
}

struct ctx *
CTX_Find(const char *name)
{
	void *ctx_iter_priv = NULL;
	struct ctx *cp;

	do {
		cp = CTX_Iter(&ctx_iter_priv);
		if (cp != NULL && !strcmp(cp->ident, name))
			return (cp);
	} while (cp != NULL);
	return (cp);
}
