#include <stdint.h>

#include "Components/tables.h"

const uint8_t lut181[16384] = {
	#include "F181_tbl.h"
};

const uint8_t lut182[512] = {
	#include "F182_tbl.h"
};
