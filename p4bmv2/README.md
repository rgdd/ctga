# Overview
This is a proof-of-concept implementation that shows how to aggregate
CT-over-DNS STHs using P4. Every n:th matching packet is control-planed copied
(n=1), and it is picked up by a controller that could interact with an off-path
challenger that verifies log consistency periodically.

## Getting started
### Install
Start by installing the
  [p4c compiler](https://github.com/p4lang/p4c) and
  [bmv2](https://github.com/p4lang/behavioral-model).
We used a global install on Ubuntu Desktop 16.04. Next, make sure that python
2.7 is available on your system with the
  [scapy package](https://scapy.readthedocs.io/en/latest/)
installed. Finally, install mininet (`sudo apt install mininet`) and update
`myenv.sh` to match the paths of your system.

### Run the code
We consider a topology where a client, a server, and a controller are attached
to a P4-enabled switch. Packets are routed statically from the client towards
the server (and vice versa); copied packets are transmitted to the controller.

```
sudo ./run.sh
```

This will compile the code and start an interactive Mininet network. For
example, enter ``xterm h1`` and try to ping the server:

```
ping 10.0.0.2 -c1

PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=1.33 ms

--- 10.0.0.2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 1.336/1.336/1.336/0.000 ms
```

Before we send an STH, open the controller (`xterm h3`) and run it:
```
./controller.py
```

Next, go back to the client terminal and send an STH that we crafted for you:
```
./send-sth.py

.
Sent 1 packets.
```

In the controller, you should see that it received the packet:
```
Received frame: 314 bytes.
```

Similarly, you could try sending fragmented STHs using ``send-sth.py --frag``.

### Future work
* IPv6
* Parser errors
* Better probabilistic filtering for fragments
