control ctgaDeparser(packet_out p, in header_t h) {
  apply {
    p.emit(h);
  }
}
