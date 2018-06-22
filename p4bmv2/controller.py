#!/usr/bin/python

#
# Simple controller that prints the size of control-plane copied packets.
#

from scapy.all import sniff, hexdump

def packet_in_handler(pkt):
  '''packet_in_handler:
  Control plane processing of copied frames goes here.
  '''
  print 'Received frame: {} bytes'.format(len(pkt))

def main(iface, etype):
  sniff(
    iface = iface,
    filter = " ".join(["ether", "proto", etype]),
    prn = lambda pkt: packet_in_handler(pkt)
  )

if __name__ == "__main__":
  main('eth0', '0xffff')
