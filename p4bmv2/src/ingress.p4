control ctgaIngress(inout header_t h, inout metadata_t m,
    inout standard_metadata_t sm) {
  register<bit<32>>(1) secpar;                                 // copy frequency
  register<bit<32>>(1) pktcnt;                     // number of matching packets
  register<bit<32>>(1) nextcopy;                 // next matching packet to copy

  // action do_nothing does nothing
  action do_nothing() {
  }

  // action do_forward marks a packet to be forwarded to an output port
  action do_forward(port_t  p) {
    sm.egress_spec = p;
  }

  // action do_drop marks a packet to be dropped
  action do_drop() {
    sm.egress_spec = 0;
    mark_to_drop();
  }

  // action do_copy marks the packet to be copied to the control plane
  action do_copy() {
    clone(CloneType.I2E, CONTROL_PLANE_SESSION_ID);
  }

  // action do_qdn_hash computes a crc32 hash over a domain name
  action do_qdn_hash() {
    hash(
      m.qdn_hash,
      HashAlgorithm.crc32,
      (bit<16>)0,
      {
        h.dns_qdn[0],
        h.dns_qdn[1],
        h.dns_qdn[2],
        h.dns_qdn[3],
        h.dns_qdn[4],
        h.dns_qdn[5]
      },
      (bit<32>)4294967295
    );
  }

  // table routing either drops or forwards a packet based on an incoming port
  table routing {
    key = {
      sm.ingress_port: exact;
    }
    actions = {
      do_drop;
      do_forward;
    }
    size = 2;
    default_action = do_drop;
  }

  // table logs looks for STHs from recognized CT logs
  table logs {
    key = {
      m.qdn_hash: exact;
    }
    actions = {
      do_nothing;
    }
    size = 64;
    default_action = do_nothing;
  }

  // packet processing pipeline: always route, and sometimes copy
  apply {
    routing.apply();
    if (h.ipv4.isValid()) {

      // aggregate fragments
      if (h.ipv4.frag_offset != 0 || h.ipv4.mf == 1) {
        #include "do_filter_copy.p4"
      }

      // aggregate sths
      else if (h.dns_question.isValid() &&
          h.dns_question.type == DNS_TYPE_TXT &&
          h.dns_question.class == DNS_CLASS_IN) {
        do_qdn_hash();
        if (logs.apply().hit) {
          #include "do_filter_copy.p4"
        }
      }
    }
  }
}
