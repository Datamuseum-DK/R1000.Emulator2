#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
# All rights reserved.
#
# Author: Poul-Henning Kamp <phk@phk.freebsd.dk>
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

'''
   Front- and back-plane wiring
   ============================

   The front- and back-planes are mostly, but not entirely parallel wiring:
   The IOC board has a lot of "private" connections to RESHA and other I/O,
   the FIU and MEM32 boards have their own thing going and only the IOC
   and MEM32 know about the ECC lines.

   This file encapsulates the exceptions
'''

GB = {
    "ECC_STOP": "GB226",
    "BP_CLK_2X": "GB294",
    "BP_CLK_2X_": "GB288",
    "BP_PHASE2X": "GB295",

    "CLK_2XE": "GB301",
    "CLK_2XE_": "GB302",
    "CLK_2X": "GB303",
    "CLK_2X_": "GB304",
    "CLK_H1_PHD": "GB305",
    "CLK_H2_PHD": "GB306",
    "CLK_H1E": "GB307",
    "CLK_H2E": "GB308",
    "CLK_H1": "GB309",
    "CLK_H2": "GB310",
    "CLK_Q1_": "GB311",
    "CLK_Q2_": "GB312",
    "CLK_Q3_": "GB313",
    "CLK_Q4_": "GB314",
    "CLK_Q4E": "GB318",

    "RESET": "GB244",
    "CLOCK_DISABLE": "GB296",
    "CLAMP": "GB323",
    "BOARD_HIT0": "GB324",
    "BOARD_HIT1": "GB325",
    "BOARD_HIT2": "GB326",
    "BOARD_HIT3": "GB327",
    "SLOT0": "GB328",
    "SLOT1": "GB329",
    "EXT_ID0": "GB330",
    "EXT_ID1": "GB331",
    "EXT_ID2": "GB332",
    "HIT_LRU0": "GB333",
    "HIT_LRU1": "GB334",
    "HIT_LRU2": "GB335",
    "HIT_LRU3": "GB336",
}

TRANSIT = {
    "*": {
         "GB293": GB["BP_CLK_2X"],
         "GB287": GB["BP_CLK_2X_"],
    },
    "fiu": {
         "GB268": "*",			# F.PAGE_STATE~0
         "GB271": "*",			# F.PAGE_STATE~1
         "GB264": GB["BOARD_HIT0"],	# MEM2: N/C
         "GB265": GB["BOARD_HIT1"],	# MEM2: N/C
         "GB266": GB["BOARD_HIT2"],	# MEM2: GB264
         "GB267": GB["BOARD_HIT3"],	# MEM2: GB265
    },
    "ioc": {
                                                  "GB004": "*",
        "GB005": "*", "GB006": "*", "GB007": "*", "GB008": "*",
                                    "GB013": "*", "GB014": GB["EXT_ID0"],
        "GB015": "*", "GB016": "*", "GB017": "*", "GB018": GB["EXT_ID1"],
        "GB021": "*",               "GB023": "*", "GB024": "*",
        "GB025": "*", "GB026": "*", "GB027": "*", "GB028": GB["EXT_ID2"],
        "GB031": "*", "GB032": "*", "GB033": "*", "GB034": "*",
        "GB035": "*", "GB036": "*", "GB037": "*", "GB038": "*",
        "GB041": "*", "GB042": "*", "GB043": "*", "GB044": "*",
        "GB045": "*", "GB046": "*", "GB047": "*", "GB048": "*",
        "GB051": "*", "GB052": "*", "GB053": "*", "GB054": "*",
        "GB055": "*", "GB056": "*", "GB057": "*", "GB058": "*",
        "GB061": "*", "GB062": "*", "GB063": "*", "GB064": "*",
                      "GB066": "*",               "GB068": "*",
        "GB071": "*", "GB072": "*",
        "GB075": "*", "GB076": "*",               "GB078": "*",
                                    "GB083": "*", "GB084": "*",
                                    "GB087": "*",
                      "GB092": "*", "GB093": "*", "GB094": "*",

                                    "GB107": "*",

                                    "GB137": "*", "GB138": "*",
                                                  "GB144": "*",
        "GB145": "*", "GB146": "*", "GB147": "*", "GB148": "*",
                                    "GB153": "*", "GB154": "*",
        "GB155": "*",
                                    "GB173": "*", "GB174": "*",
        "GB175": "*",               "GB177": "*",
                                                  "GB184": "*",
        "GB185": "*", "GB186": "*", "GB187": "*", "GB188": "*",
        "GB191": "*", "GB192": "*", "GB193": "*", "GB194": "*",
        "GB195": "*", "GB196": "*", "GB197": "*", "GB198": "*",
        "GB201": "*", "GB202": "*", "GB203": "*", "GB204": "*",
        "GB205": "*", "GB206": "*",
        "GB211": "*", "GB212": "*", "GB213": "*", "GB214": "*",
        "GB215": "*",                             "GB218": "*",
        "GB221": "*",               "GB223": "*", "GB224": "*",
        "GB225": "*",               "GB227": "*", "GB228": "*",
        "GB231": "*",               "GB233": "*", "GB234": "*",
        "GB235": "*",               "GB237": "*", "GB238": "*",
        "GB241": "*", "GB242": "*",
        "GB245": "*",               "GB247": "*", "GB248": "*",
        "GB251": "*",               "GB253": "*", "GB254": "*",
        "GB255": "*", "GB256": "*", "GB257": "*", "GB258": "*",

        "GB265": "*", "GB266": "*",
        "GB271": "*", "GB272": "*", "GB273": "*",

        "GF003": "*", "GF007": "*",
        "GF011": "*", "GF015": "*", "GF019": "*",
        "GF023": "*", "GF027": "*",
        "GF031": "*", "GF035": "*", "GF039": "*",
        "GF043": "*", "GF047": "*",
        "GF051": "*", "GF055": "*", "GF059": "*",
        "GF063": "*", "GF067": "*",
        "GF071": "*", "GF075": "*", "GF079": "*",
        "GF083": "*", "GF087": "*",
        "GF091": "*", "GF095": "*", "GF099": "*",
        "GF103": "*", "GF107": "*",
        "GF111": "*", "GF115": "*", "GF119": "*",
        "GF123": "*", "GF127": "*",
        "GF131": "*", "GF167": "*",
        "GF171": "*", "GF175": "*", "GF179": "*",
        "GF183": "*", "GF187": "*",
        "GF191": "*", "GF195": "*", "GF199": "*",
        "GF203": "*", "GF207": "*",
        "GF211": "*", "GF215": "*", "GF219": "*",
        "GF223": "*", "GF227": "*",
        "GF231": "*", "GF235": "*", "GF239": "*",
        "GF243": "*", "GF247": "*",
        "GF251": "*", "GF255": "*", "GF259": "*",
        "GF263": "*", "GF267": "*",
        "GF271": "*", "GF275": "*", "GF279": "*",
        "GF283": "*", "GF287": "*",
        "GF291": "*",
    },
    "mem32": {
        "GB054": GB["HIT_LRU0"],
        "GB055": GB["HIT_LRU1"],
        "GB056": GB["HIT_LRU2"],
        "GB058": GB["HIT_LRU3"],
        "GB242": GB["SLOT0"],
        "GB243": GB["SLOT1"],
        "GB264": GB["BOARD_HIT0"],
        "GB265": GB["BOARD_HIT1"],
        "GB266": GB["BOARD_HIT2"],
        "GB267": GB["BOARD_HIT3"],
    },
}

DEFAULTS = {
    # In case there is no IOC to drive this
    GB["ECC_STOP"]: False,
}

def alloc_transit():
    ''' Allocate dynamic transits '''
    highest = {
	"GF": 320,
	"GB": 319,
    }
    for gates in TRANSIT.values():
        for pin in sorted(gates):
            if gates[pin] != "*":
                highest[pin[:2]] = max(highest[pin[:2]], int(gates[pin][2:], 10) + 1)
    for _brd, gates in sorted(TRANSIT.items()):
        for src, dst in sorted(gates.items()):
            if dst == "*":
                gates[src] = src[:2] + "%03d" % highest[src[:2]]
                highest[src[:2]] += 1
    return highest

PLANE_SIZE = alloc_transit()

def do_transit(board, src):
    ''' Transit one pin for one board '''
    rval = src
    for i in ('*', board.lower()):
        tbl = TRANSIT.get(i, {})
        dst = tbl.get(src)
        if dst:
            rval = dst
            break
    return rval, DEFAULTS.get(rval)
