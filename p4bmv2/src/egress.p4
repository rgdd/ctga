control ctgaEgress(inout header_t h, inout metadata_t m,
    inout standard_metadata_t sm) {

  apply {
    // encapsulate copied packets
    if (sm.instance_type == 1) {
      h.control_plane.setValid();
      h.control_plane.src = 0xaaaaaaaaaaaa; // dummy src
      h.control_plane.dst = 0xbbbbbbbbbbbb; // dummy dst
      h.control_plane.type = CONTROL_PLANE_STH;
    }
  }
}
