# Overview
This is a proof-of-concept implementation that shows how to aggregate
CT-over-DNS STHs using XDP. Every n:th matching packet is copied to a ring
buffer (n=1), and it is polled by a user space application that could interact
with an off-path challenger that verifies log consistency periodically.

## Getting started
### Install
Follow this
  [XDP setup guide](https://github.com/cilium/cilium/blob/doc-1.0/Documentation/bpf.rst),
installing the
  [net-next](https://git.kernel.org/pub/scm/linux/kernel/git/davem/net-next.git)
kernel version v4.17.06-rc. To use the same physical setup as us, install Ubuntu
Server 18.04 and acquire an Intel X520 10Gb SFP+ network card. Don't forget to
build `iproute2` and `bpftool`, as well as running `make headers_install` in the
top-most `net-next` directory.

Now copy-paste all files in this directory to `net-next/samples/bpf`, modify
`Makefile` such that the four lines in `Makefile-diff` are added, and run `make`
to compile all BPF samples (including our newly added XDP program). This should
create an executable named `xdp_sample_pkts`.

### Run the code
To load the program and fill the tables, run
  `xdp_sample_pkts <ifname>`,
  `secpar.sh`, and
  `add-logs.sh`.
This gives a setup that copies all matching packets for Google's
  Icarus,
  Pilot,
  Rocketeer, and
  Skydiver
logs. To ensure that all packets are processed by a single core that we poll in
`xdp_sample_pkts`, run `single-core.sh`.

What's expected now is that CT-over-DNS traffic should be aggregated and
printed in the terminal running `xdp_sample_pkts`. You can fetch an STH yourself
via CT-over-DNS
  (`dig sth.ct.rocketeer.googleapis.com -c IN -t TXT @8.8.8.8`),
or use the captured response in `sth.pcap` to replay with a correct destination
MAC address.

## Future work
* IPv6
* Fix IPv4 fragment parsing shortcut
* Better probabilistic filtering for fragments

## Licence
GPLv2
