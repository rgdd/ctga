#!/usr/bin/python

#
# This script sends a UDP packet from a source to a destination.
#

import logging
import argparse

from scapy.all import *

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
  parser.add_argument('--sport',
    help='source port',
    type=int,
    action="store",
    default=15000,
  )
  parser.add_argument('--dport',
    help='destination port',
    type=int,
    action="store",
    default=16000,
  )
  parser.add_argument('--payload',
    help='udp payload',
    type=str,
    action="store",
    default='a'*32,
  )
  parser.add_argument('--frag',
    help='set if packet should be fragmented',
    action="store_true",
  )
  return parser.parse_args()

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
    get_udp(args.src, args.dst, args.sport, args.dport, args.payload),
    args.frag
  )

if __name__ == "__main__":
  main(get_args())
