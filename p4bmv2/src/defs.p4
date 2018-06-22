// architecture and controller dependent
typedef bit<9> port_t;
const bit<32> CONTROL_PLANE_SESSION_ID = 250;
const bit<16> CONTROL_PLANE_STH = 0xffff;

// protocol identifiers
const bit<16> PROTO_IPV4 = 0x0800;
const bit<8>  PROTO_UDP  = 0x11;
const bit<16> PROTO_DNS  = 53;

// dns: single question + single answer filter
const tuple<bit<16>, bit<16>> DNS_FILTER = {1, 1};

// dns: class=IN and type=TXT
const bit<16> DNS_TYPE_TXT = 16;
const bit<16> DNS_CLASS_IN = 1;
