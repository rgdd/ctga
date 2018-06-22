#!/usr/bin/python

from argparse import ArgumentParser
from subprocess import call

def get_args():
  '''get_args:
  Parses command line arguments, see descriptions below.
  '''
  parser = ArgumentParser(
    description='Generate commands to fill a bpf table of known logs'
  )
  parser.add_argument('--map-id',
    help='use the bpftool to determine bpf map identifiers',
    action="store",
    required=True
  )
  parser.add_argument('--dn-max',
    help='max domain name length',
    type=int,
    action="store",
    required=True
  )
  return parser.parse_args()

def zero_pad(n):
  '''zero_pad:
  Returns a string of n zero-bytes.
  '''
  return "" if n <= 0 else chr(0)*n

def encode_dn(dn, dn_max):
  '''encode_dn:
  Encodes a human-readable domain name to the a zero-padded length-label format.
  '''
  labels, ldn = dn.split("."), []
  for l in labels:
    ldn.append(chr(len(l)))
    ldn.append(l)
  edn = "".join(ldn)
  return edn + zero_pad(dn_max - len(edn))

def byte_output(s):
  '''byte_output:
  Returns the string s as a human-readable byte-by-byte hex string, e.g., s="ab"
  yields '0x97 0x98 '.
  '''
  ret = ""
  for c in s:
    ret += str(hex(ord(c))) + " "
  return ret

def main(logs, map_id, dn_max):
  '''main:
  Generates commands that can be used to fill a bpf map of known logs.
  '''
  for log in logs:
    cmd = 'sudo bpftool map update id {} key {} value {}'.format(
      map_id,
      byte_output(encode_dn(log, dn_max)),
      byte_output('\x00\x00\x00\x01'),
    )
    call(cmd.split())

if __name__ == '__main__':
  args = get_args()
  main(
    logs = [
      "sth.icarus.ct.googleapis.com",
      "sth.pilot.ct.googleapis.com",
      "sth.rocketeer.ct.googleapis.com",
      "sth.skydiver.ct.googleapis.com",
    ],
    map_id = args.map_id,
    dn_max = args.dn_max,
  )
