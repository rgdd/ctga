/* -*- P4_16 -*- */

#include <core.p4>
#include <v1model.p4>

#include "src/defs.p4"
#include "src/metadata.p4"
#include "src/headers.p4"
#include "src/parser.p4"
#include "src/checksum.p4"
#include "src/ingress.p4"
#include "src/egress.p4"
#include "src/deparser.p4"

V1Switch(
  ctgaParser(),
  ctgaVerifyChecksum(),
  ctgaIngress(),
  ctgaEgress(),
  ctgaComputeChecksum(),
  ctgaDeparser()
) main;
