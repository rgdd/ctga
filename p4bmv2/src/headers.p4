header ethernet_t {
  bit<48> src;
  bit<48> dst;
  bit<16> type;
}

header ipv4_t {
  bit<4>  version;
  bit<4>  ihl;
  bit<6>  dscp;
  bit<2>  ecn;
  bit<16> length;
  bit<16> id;
  bit<1>  reserved;
  bit<1>  df;
  bit<1>  mf;
  bit<13> frag_offset;
  bit<8>  ttl;
  bit<8>  protocol;
  bit<16> checksum;
  bit<32> src;
  bit<32> dst;
}

header ipv4_options_t {
  varbit<320> options;
}

header udp_t {
  bit<16> src;
  bit<16> dst;
  bit<16> length;
  bit<16> checksum;
}

header dns_t {
  bit<16> id;
  bit<1>  qr;
  bit<4>  opcode;
  bit<1>  aa;
  bit<1>  tc;
  bit<9>  flags;
  bit<16> qd;
  bit<16> an;
  bit<16> ns;
  bit<16> ar;
}

// dns question: domain name 
header dns_label_t {
  bit<8>     length;  // length of label in bytes
  varbit<80> value;   // max interesting label is 10 bytes
}

// dns question: type and class
header dns_question_t {
  bit<16> type;
  bit<16> class;
}

struct header_t {
  // control plane encapsulation
  ethernet_t      control_plane;
  // actual packet
  ethernet_t      ethernet;
  ipv4_t          ipv4;
  ipv4_options_t  ipv4_options;
  udp_t           udp;
  dns_t           dns;
  dns_label_t[6]  dns_qdn;
  dns_question_t  dns_question;
}
