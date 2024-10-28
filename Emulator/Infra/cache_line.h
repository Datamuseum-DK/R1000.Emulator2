/*-
 * Copyright (c) 2005-2020 Poul-Henning Kamp
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
 * MEM32:
 * ------
 *
 * SPC ---NAM---------------><----------- OFF -------------->
 * 000 1         2         3         4         5          
 * 012 01234567890123456789012345678901234567890
 * ---------------------------------------------
 *  x  | x       |         |         |        x|   H11
 *     |  x      |         |         x         |   H10
 *     |   x     |         |         |x        |   H9
 *     |    x    |         |         | x       |   H8
 *     |     x   |         |        x|         |   H7
 *     |      x  |         |         |  x      |   H6
 *     |       x |         |         |      x  |   H5
 *     |        x|         |         |     x   |   H4
 *     |         x         |         |    x    |   H3
 *     |         |x        |         |   x     |   H2
 * x   |         |         |         |         x   H1
 *   x |         |         |         |       x |   H0
 * ---------------------------------------------
 * 
 * FIU:
 * ----
 *
 * SPC ---NAM---------------><----------- OFF -------------->
 *     1         2         3 0         1      |  2         3
 * 012 012345678901234567890101234567890123456789012345678901
 * ----------------------------------------------------------
 *  x  | x       |         |         |        x|           H11
 *     |  x      |         |         x         |           H10
 *     |   hhhh  |         |        h|hhh     hh
 *     |       llll        |         | llllll  |
 * x   |         |         |         |         x           H1
 *   x |         |         |         |       x |           H0
 * 
 *
 * cache_line.[ch]:
 * ----------------
 *
 * SPC ---NAM---------------><----------- OFF -------------->
 * 012 012345678901234567890101234567890123456789012345678901
 * ----------------------------------------------------------
 *                                  xxxxxxxxxxxx-------------	tbl_l
 *       xxxxxxxxxx----------					tbl_h
 * xxx								tbl_s
 * ----------------------------------------------------------
 */

#include <stdint.h>

extern const uint16_t cache_line_tbl_h[1024];
extern const uint16_t cache_line_tbl_l[4096];
extern const uint16_t cache_line_tbl_s[8];
