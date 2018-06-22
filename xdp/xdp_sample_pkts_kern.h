#ifndef MAIN_H
#define MAIN_H

#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <linux/version.h>
#include <uapi/linux/bpf.h>
#include "bpf_helpers.h"

#define LITTLE_ENDIAN
#define DONE_ACTION XDP_PASS
#define SAMPLE_SIZE 420ul
#define DN_MAX 90

// rbuf is a ring buffer of packets sent from kernel to user space
struct bpf_map_def SEC("maps") rbuf = {
  .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
  .key_size = sizeof(int),
  .value_size = sizeof(__u32),
  .max_entries = 2,
};

// log is a map of known CT logs (user-space populated)
struct bpf_map_def SEC("maps") logs = {
  .type = BPF_MAP_TYPE_HASH,
  .key_size = DN_MAX,
  .value_size = sizeof(int),
  .max_entries = 64,
};

// secpar is a map related to probabilistic filtering (user-space populated)
//  - entry 0: copy frequency 
//  - entry 1: packet counter
struct bpf_map_def SEC("maps") secpar = {
  .type = BPF_MAP_TYPE_ARRAY,
  .key_size = sizeof(__u32),
  .value_size = sizeof(__u32),
  .max_entries = 2,
};

#define FINDEX 0;
#define PINDEX 1;

//
// We avoid htons() and other kernel headers due to include issues at some
// point. This is either way good for overview, but it could be refactored
//
#ifdef LITTLE_ENDIAN
#define PROTO_IPV4    0x0008
#define PROTO_UDP     0x11
#define PROTO_DNS     0x3500
#define DNS_TYPE_TXT  0x1000
#define DNS_CLASS_IN  0x0100
#define U16_VALUE_1   0x0100

#else // big endian
#define PROTO_IPV4    0x0800
#define PROTO_UDP     0x11
#define PROTO_DNS     0x0035
#define DNS_TYPE_TXT  0x0010
#define DNS_CLASS_IN  0x0001
#define U16_VALUE_1   0x0001
#endif

struct Ethernet {
  __u8    dst[6];
  __u8    src[6];
  __be16  type;
} __attribute__((packed));
typedef struct Ethernet ethernet_t;

struct IPv4 {
#ifdef LITTLE_ENDIAN
  __u8   ihl:4,
         version:4;
#else
  __u8   version:4,
         ihl:4;
#endif
  __u8   tos;
  __be16 length;
  __be16 id;
  __be16 fragment; // sloppy, but ok for poc
  __u8   ttl;
  __u8   protocol;
  __be16 checksum;
  __be32 src;
  __be32 dst;
};
typedef struct IPv4 ipv4_t;

struct Udp {
  __be16 src;
  __be16 dst;
  __be16 length;
  __be16 checksum;
};
typedef struct Udp udp_t;

struct Dns {
  __be16 id;
  __be16 flags;
  __be16 qd;
  __be16 an;
  __be16 ns;
  __be16 ad;
};
typedef struct Dns dns_t;

struct Dn {
  __u8 value[DN_MAX];
};
typedef struct Dn dn_t;

struct Question {
  __be16 type;
  __be16 class;
};
typedef struct Question question_t;

#endif /* MAIN_H */
