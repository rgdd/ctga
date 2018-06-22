#!/usr/bin/python

import logging
import pyasn

from sys import maxint
from netaddr import IPNetwork, IPAddress
from ripe.atlas.sagan import TracerouteResult
from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasResultsRequest

ip2as = pyasn.pyasn('data/ip2as.db')

def weight(asn):
  '''weight:
  Returns the IP space size of an AS.
  '''
  return ip2as.get_as_size(asn)

def bestProbe(pids, p2f):
  '''bestProbe:
  Returns the best redundant probe ID in pids based on tracked failures.

  @param pids   List of probe IDs.
  @param p2f    Dictionary with Probe IDs to fail counters.
  '''
  best, failCnt = pids[0], maxint
  for pid in pids:
    if pid not in p2f:
      return pid
    if p2f[pid] < failCnt:
      best, failCnt = pid, p2f[pid]
  return best

def probeMap(ipv4=True, **pf):
  '''probeMap:
  Downloads and groups probe information that adheres to the pf filter.

  @param ipv4   Set/unset to target probes with assigned IPv4/IPv6 AS numbers.
  @param pf     Probe filter, see Ripe Atlas documentation for details.
  @ret 1        Dictionary with Probe-IDs to AS numbers.
  @ret 2        Dictionary with AS numbers to probe lists.
  @ret 3        Number of probes without an assigned IPv4/IPv6 ASN.
  '''
  p2a, a2p, cnt, asnVx = {}, {}, 0, 'asn_v4' if ipv4 else 'asn_v6'
  for probe in ProbeRequest(**pf):
    if probe[asnVx] is not None:
      p2a[int(probe['id'])] = int(probe[asnVx]) 
      a2p.setdefault(int(probe[asnVx]), [])
      a2p[int(probe[asnVx])].append(probe)
    else:
      cnt += 1
  return p2a, a2p, cnt

def privateIp(ip):
  '''privateIp:
  Determines whether an IPv4 address is private.
   
  @param ip   IPv4 address (str).
  '''
  return IPAddress(ip) in IPNetwork("192.168.0.0/16") or \
     IPAddress(ip) in IPNetwork("172.16.0.0/12") or \
     IPAddress(ip) in IPNetwork("10.0.0.0/8")

def makeIpPath(hops):
  '''makeIpPath:
  Creates an IP path set.

  @param hops   List of traceroute hops; a hops is a list of IPv4 strings.
  '''
  ipSet = set()
  for hop in hops:
    ipSet = ipSet.union(set(hop))
  return ipSet

def makePath(hops, *ignore):
  '''makePath:
  Creates a set of traversed ASes from a Paris traceroute result. If an entry is
  not an AS number, it is categorized as '*', 'Unknown', or 'Private'.

  @param hops     List of traceroute hops; a hop is a list of IPv4 strings.
  @param ignore   Exclude these entries from the final AS path set.
  '''
  ipSet, asSet = makeIpPath(hops), set()
  for ip in ipSet:
    if ip is None:
      asSet.add('*')
    elif privateIp(ip):
      asSet.add('Private')
    else:
      as_ = ip2as.lookup(ip)[0]
      asSet.add('Unknown' if as_ is None else as_)
  return asSet.difference(set(ignore))

def fetchRawResults(msmIds):
  '''fetchRawResults:
  Downloads and merges several RIPE Atlas measurements, returning the results
  as a single list.

  @param msmIds   List of measurement IDs.
  '''
  logging.info('Fetching raw results from measurements: {}'.format(msmIds))
  results = []
  for msmId in msmIds:
    ok, result = AtlasResultsRequest(**{
      'msm_id': msmId,
    }).create()
    if ok:
      results += result 
    else:
      logging.error("Failed to download measurement {}".format(msmId))
  return results

def parseRawTracerouteResults(results, fnMakePath, *prune):
  '''parseRawTracerouteResults:
  Parses RIPE Atlas traceroute results into path sets, grouping on probe IDs.

  @param results    List of raw traceroute results.
  @param fnMakePath Function that returns a path's set representation; it
                    accepts a traceroute.ip_path object as input, and optionally
                    a list *prune that contains locations to exclude. Refer to
                    ripeh.makePath and caidah.makePath for examples.
  @param prune      List of strings to exclude from our AS paths.
  @ret 1            List of probe IDs to pruned AS paths.
  @ret 2            List of probe IDs to fail counters.
  '''
  logging.info('Parsing raw traceroute results using filter: {}'.format(prune))
  p2r, p2f = {}, {}
  for result in results:
    tr = TracerouteResult(result)
    if tr.is_success:
      path = fnMakePath(tr.ip_path, *prune)
      p2r.setdefault(tr.probe_id, [])
      p2r[tr.probe_id].append(path)
    else:
      p2f.setdefault(tr.probe_id, 0)
      p2f[tr.probe_id] += 1
  return p2r, p2f

def pruneResults(p2r, p2f, p2a, a2p):
  '''pruneResults:
  Returns pruned results of p2r and p2f: the best probe in each unique AS is
  selected and redundant ones are removed. Probe A is better than probe B if
  p2f[A] < p2f[B]; if A !in p2f, then it is selected on a first-encounter basis.

  @param p2r  Dictionary with probe IDs to parsed traceroute results.
  @param p2f  Dictionary with probe IDs to failed traceroute counters.
  @param p2a  Dictionary with probe IDs to AS numbers.
  @param a2p  Dictionary with AS numbers to probe lists.
  @ret 1      Pruned representation of p2r.
  @ret 2      Pruned representation of p2f.
  '''
  logging.info('Pruning parsed traceroute results to remove redundancy...')
  msmPids, toRemove, processedAsns = set(p2r.keys()), [], {}
  for pid in p2r.keys():
    if pid in p2a:
      asn = p2a[pid]
      if asn not in processedAsns:
        processedAsns[asn] = True
        asnPids = set([ probe['id'] for probe in a2p[asn] ])
        selectedPids = list(msmPids.intersection(asnPids))
        bestPid = bestProbe(selectedPids, p2f)
        selectedPids.remove(bestPid)
        toRemove += selectedPids
    else:
      logging.warning("No AS number for probe {}, removing...".format(pid))
      toRemove.append(pid)

  for pid in toRemove:
    if pid in p2r: del p2r[pid]
    if pid in p2f: del p2f[pid]
  return p2r, p2f
