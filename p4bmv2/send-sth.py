#!/usr/bin/python

#
# This script sends a DNS get-STH response from a source to a destination.
#

import logging
import argparse

from scapy.all import *

# Length octet + STH
TXT_RDATA = \
  "\xad172961256.1510823008986.tVFF1VsSS6G4lfR9Am/jGGJW7ao5MtVNopZtRBFFGS0=."+\
  "BAMASDBGAiEAvRyrYpcq2qVXUl2rq/3SgfxLOAEZUmZkSWHFIbcvvmECIQDZb8vDwuALFw3cs"+\
  "lW+HOABNADEbXOXOrKyvhcPTbDvDA=="

def get_args():
  parser = argparse.ArgumentParser(description="Sends a crafted STH response")
  parser.add_argument('--iface',
    help='sender interface, e.g., eth0',
    type=str,
    action='store',
    default='eth0',
  )
  parser.add_argument('--src',
    help='source IP',
    type=str,
    action="store",
    default='10.0.0.1',
  )
  parser.add_argument('--dst',
    help='destination IP',
    type=str,
    action="store",
    default='10.0.0.2',
  )
  parser.add_argument('--frag',
    help='set if packet should be fragmented',
    action="store_true",
  )
  parser.add_argument('--dns-api',
    help='DNS STH API, e.g., sth.pilot.ct.googleapis.com',
    type=str,
    action="store",
    default='sth.pilot.ct.googleapis.com',
  )
  parser.add_argument('--txt-rdata',
    help='rdata portion that contains an STH',
    type=str,
    action="store",
    default=TXT_RDATA,
  )
  return parser.parse_args()

def get_sth(src, dst, dn, txt_rdata):
  return \
    IP(src=src, dst=dst) /\
    UDP() /\
    DNS(
      qd=DNSQR(
        qname=dn,
        qtype="TXT",
        qclass="IN"
      ),
      an=DNSRR(
        rrname=dn,
        type="TXT",
        ttl=64,
        rdata=txt_rdata,
      )
    )

def get_udp(src, dst, sport, dport, payload):
  return \
    IP(src=src, dst=dst) /\
    UDP(sport=sport, dport=dport) /\
    Raw(payload)

def send_packet(iface, packet, frag):
  pkts = fragment(packet, fragsize=len(packet)/2) if frag else packet
  for pkt in pkts:
    logging.info('Sending packet...')
    send(pkt, iface=iface, verbose=0)

def main(args):
  logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
  send_packet(
    args.iface,
    get_sth(args.src, args.dst, args.dns_api, args.txt_rdata),
    args.frag
  )

if __name__ == "__main__":
  main(get_args())
