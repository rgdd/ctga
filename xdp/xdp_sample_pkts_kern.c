#include "xdp_sample_pkts_kern.h"

// do_copy copies a packet to user space if it is less than a threshold
static int do_copy(struct xdp_md *ctx) {
  void *data = (void *)(long)ctx->data;
  void *data_end = (void *)(long)ctx->data_end;
  struct S {
    u16 pkt_len;
  } __attribute__((packed)) meta;

  meta.pkt_len = (u16)(data_end - data);
  if (data + meta.pkt_len <= data_end) {
    u64 flags = (u64)meta.pkt_len << 32;
    bpf_perf_event_output(ctx, &rbuf, flags, &meta, sizeof(meta));
  }

  return 0;
}

// pktcnt_inc increments and returns the value of a monotonic packet counter
static int pktcnt_inc() {
  u32 pindex = PINDEX;
  u32 *pktcnt = bpf_map_lookup_elem(&secpar, &pindex);
  return !pktcnt ? 0 : (*pktcnt += 1);
}

// get_frequency reads a control plane copy frequency from register
static int get_frequency() {
  u32 findex = FINDEX;
  u32 *frequency = bpf_map_lookup_elem(&secpar, &findex);
  return !frequency ? 0 : *frequency;
}

// filter returns non-zero if this packet should be filtered
static int filter() {
  u32 pktcnt = pktcnt_inc();
  u32 frequency = get_frequency();
  return frequency > 0 ? pktcnt % frequency : 1;
}

// do_filter_copy copies a packet unless it should be filtered
int do_filter_copy(struct xdp_md *ctx) {
  if (!filter()) {
    do_copy(ctx);
  }
  return DONE_ACTION;
}

// xdp_sample is the main program which aggregates ct-over-dns sths
SEC("xdp_sample")
int xdp_sample_prog(struct xdp_md *ctx)
{
  u8 *head = (void *)(unsigned long)ctx->data;
  u8 *tail = (void *)(unsigned long)ctx->data_end;

  //--------------------------------------------------------------------------//
  //                                Ethernet                                  //
  //--------------------------------------------------------------------------//
  ethernet_t *eth = (void *)(unsigned long)ctx->data;
  head += sizeof(ethernet_t);
  if (head > tail) {
    return DONE_ACTION;
  }

  if (eth->type != PROTO_IPV4) {
    return DONE_ACTION;
  }

  //--------------------------------------------------------------------------//
  //                                  IPv4                                    //
  //--------------------------------------------------------------------------//
  ipv4_t *ipv4 = (void *)head;
  if (head+sizeof(ipv4_t) > tail) {
    return DONE_ACTION;
  }
  head += ipv4->ihl*4;

  if (ipv4->protocol != PROTO_UDP) {
    return DONE_ACTION;
  }
  
  if (ipv4->fragment) {
    return do_filter_copy(ctx);
  }

  //--------------------------------------------------------------------------//
  //                           No fragment and UDP                            //
  //--------------------------------------------------------------------------//
  udp_t *udp = (void *)head;
  head += sizeof(udp_t);
  if (head > tail) {
    return DONE_ACTION;
  }

  if (udp->src != PROTO_DNS) {
    return DONE_ACTION;
  }

  //--------------------------------------------------------------------------//
  //                                  DNS                                     //
  //--------------------------------------------------------------------------//
  dns_t *dns = (void *)head;
  head += sizeof(dns_t);
  if (head > tail) {
    return DONE_ACTION;
  }

  if (dns->qd != U16_VALUE_1 || dns->an != U16_VALUE_1) {
    return DONE_ACTION; // not an sth per requirement
  }

  // parse domain name as a null-terminated string
  dn_t qdn = {};
  u8 *value = 0;
  u16 offset = 0;
  #pragma unroll
  while (offset < DN_MAX) { 
    if (head+offset+1 > tail) {
      return DONE_ACTION;
    }
    if (!*(value = head+offset)) {
      break;
    }
    qdn.value[offset++] = *value;
  }
  head += offset+1;

  if (value && *value) {
    return DONE_ACTION; // too large dn to be a recognized log
  }

  if (!bpf_map_lookup_elem(&logs, &qdn)) {
    return DONE_ACTION; // not a recognized log
  }

  question_t *question = (void *)head;
  head += sizeof(question_t);
  if (head > tail) {
    return DONE_ACTION;
  }

  if (question->type != DNS_TYPE_TXT || question->class != DNS_CLASS_IN) {
    return DONE_ACTION; // not an sth
  }

  return do_filter_copy(ctx);
}

char _license[] SEC("license") = "GPL";
u32 _version SEC("version") = LINUX_VERSION_CODE;
