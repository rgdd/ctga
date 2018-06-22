parser ctgaParser(packet_in p, out header_t h, inout metadata_t m,
    inout standard_metadata_t sm) {

  state start {
    m.qdn_hash = 0;
    transition parse_ethernet;
  }

  state parse_ethernet {
    p.extract(h.ethernet);
    transition select(h.ethernet.type) {
      PROTO_IPV4: parse_ipv4;
      default:    accept;
    }
  }

  state parse_ipv4 {
    p.extract(h.ipv4);
    transition select(h.ipv4.ihl) {
      5:       parse_l4;
      default: parse_ipv4_options;
    }
  }

  state parse_ipv4_options {
    p.extract(h.ipv4_options, (bit<32>)(((bit<16>)h.ipv4.ihl-5)*32));
    transition parse_l4;
  }

  state parse_l4 {
    transition select(h.ipv4.protocol) {
      PROTO_UDP: parse_udp;
      default:   accept;
    }
  }

  state parse_udp {
    p.extract(h.udp);
    transition select(h.udp.src) {
      PROTO_DNS: parse_dns;
      default:   accept;
    }
  }

  state parse_dns {
    p.extract(h.dns);
    transition select(h.dns.qd, h.dns.an) {
      DNS_FILTER: parse_dns_qdn; // single question, single answer
      default:    accept;
    }
  }

  state parse_dns_qdn {
    bit<32> n = (bit<32>)(p.lookahead<bit<8>>()) * 8;
    p.extract(h.dns_qdn.next, n);
    transition select(n) {
      0:       parse_dns_question;
      default: parse_dns_qdn;
    }
  }

  state parse_dns_question {
    p.extract(h.dns_question);
    transition accept;
  }
}
