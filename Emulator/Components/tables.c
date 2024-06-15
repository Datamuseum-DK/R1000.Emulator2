#include <stdint.h>

#include "Components/tables.h"

/*
 * The order of the four S signals are reversed relative to the datasheet
 * to match the same the R1000 schematic symbol.
 */
const uint8_t lut181[16384] = {
	#include "F181_tbl.h"
};

const uint8_t lut182[512] = {
	#include "F182_tbl.h"
};
