#!/usr/bin/python

#
# As shown in Figure 1, this script sets up a topology where three hosts h1, h2,
# and h3 are connected through a P4 enabled software switch s1. For example, h1
# could be a DNS client, h2 a DNS server, and h3 a controller (control plane).
#                      
#                               controller
#                                   |
#                                  [3]
#           client----------[1]P4 switch[2]----------server
#        Figure 1: Topology setup by this script; [x] denotes port x.
#
# To load the switch with commands, provide them in the file ``commands.txt''.
#

import argparse
import subprocess

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from p4_mininet import P4Switch, P4Host

def get_args():
  '''get_args:
  Parses command line arguments, see descriptions below.
  '''
  parser = argparse.ArgumentParser(description="P4 topology")
  parser.add_argument('--behavioral-exe',
    help = 'Path to behavioral executable',
    type = str,
    action = "store",
    required = True
  )
  parser.add_argument('--json',
    help = 'Path to JSON config file',
    type = str,
    action = "store",
    required = True
  )
  parser.add_argument('--cli',
    help = 'Path to BM API',
    type = str,
    action = "store",
    required = True
  )
  return parser.parse_args()

class Topology(Topo):
  '''Topology:
  Configures the topology shown in Figure 1.
  '''
  def __init__(self, switchPath, jsonPath, thriftPort, **opts):
    Topo.__init__(self, **opts)

    self.addSwitch("s1", sw_path=switchPath, json_path=jsonPath,
      thrift_port=thriftPort, pcap_dump=False)

    self.addHost("h1", ip="10.0.0.1", mac="00:00:00:00:00:01")
    self.addHost("h2", ip="10.0.0.2", mac="00:00:00:00:00:02")
    self.addHost("h3", ip="10.0.0.3", mac="00:00:00:00:00:03")

    self.addLink("h1", "s1")
    self.addLink("h2", "s1")
    self.addLink("h3", "s1")

def main(args, cmds, thrift_port):
  '''main:
  Start an interactive Mininet session for the topology shown in Figure 1.
  '''
  # Load mininet topology
  topo = Topology(args.behavioral_exe, args.json, thrift_port)
  net = Mininet(topo=topo, host=P4Host, switch=P4Switch, controller=None)
  net.start()

  # Fill P4 tables
  cmd = [args.cli, args.json, str(thrift_port)]
  with open(cmds, "r") as f:
    try:
      print subprocess.check_output(cmd, stdin=f)
    except subprocess.CalledProcessError as e:
      print e, "\n", e.output

  # Run mininet in interactive mode
  CLI(net)
  net.stop()

if __name__ == "__main__":
  main(get_args(), "commands.txt", 20003)
