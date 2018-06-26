# Aggregation-Based Gossip for Certificate Transparency
Certificate Transparency (CT) relies on a gossip mechanism to detect logs that
present conflicting versions of its structure and content to different parties;
so called split views. We propose a retrospective and application neutral
approach towards gossip that is based on client-initiated log communications in
plaintext using an existing infrastructure of packet processors, e.g., including
routers, network interface cards, and operating systems.

<p align="center">
  <img
    src="https://raw.githubusercontent.com/rgdd/ctga/master/doc/overview.png"
    width="512"
  />
</p>

The idea is that clients interact with the logs over a network, and as part of
the network in-line packet processors _aggregate_ observed responses to off-path
challengers that periodically verify log consistency. Conceptually it would be
nice to aggregate at packet processor which see diverse traffic, including those
that are located at well-connected Autonomous Systems (ASes). Based on a
simulation using RIPE Atlas probes from 3500 unique ASes, we show that our
approach towards gossip provide significant protection against many relevant
attackers with relatively little opt-in and in incremental deployment scenarios.
We implemented in-line aggregation that runs at packet processors supporting P4
and XDP, showing that up to 10 Gbps line speed can be achieved on two different
hardware targets.

Further details on the estimated impact of deployment and our proof-of-concept
implementations can be found in the `ripe`, `p4bmv2` and `xdp` directories.

## Paper
[https://arxiv.org/pdf/1806.08817.pdf](https://arxiv.org/pdf/1806.08817.pdf)

## Licence
Specified in the respective subdirectories separately
