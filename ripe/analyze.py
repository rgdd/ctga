#!/usr/bin/python

'''
analyze.py

This script downloads and processes our RIPE Atlas traceroute measurements such
that path length, path stability, and (un)weighted probe coverage results can be
reproduced. Don't forget to aquire public data sets first, see README.
'''

from __future__ import division

import pickle
import logging
import caidah
import ripeh

from ripe.atlas.sagan import TracerouteResult
from ripe.atlas.cousteau import AtlasResultsRequest

def main(plNmax, psNmax, covNmax, pfGoo, pfNor, msmGoo, msmNor):
  '''main:
  Downloads and processes our traceroute measurements, outputing path length,
  path stability, and (un)weighted probe coverage for Google and NORDUnet.
  '''
  p2a, a2p = getProbes()
  p2rGooAS, p2rGooIXP, p2fGoo = getResults(p2a, a2p, pfGoo, msmGoo, 'Google')
  p2rNorAS, p2rNorIXP, p2fNor = getResults(p2a, a2p, pfNor, msmNor, 'NORDUnet')
  analyze(plNmax, psNmax, covNmax, p2rGooAS, p2rGooIXP, p2fGoo, p2a, 'Google')
  analyze(plNmax, psNmax, covNmax, p2rNorAS, p2rNorIXP, p2fNor, p2a, 'NORDUnet')

def getProbes(refresh=False):
  '''getProbes:
  Uses RIPE Atlas probe metadata to map probes to AS numbers and vice versa.

  @param refresh  Set to refresh probe metadata (as opposed to using what was
                  current at the time of our measurements).
  '''
  if refresh:
    logging.info('Fetching probe info...')
    p2a, a2p, _ = ripeh.probeMap()
  else:
    logging.info('Loading probe info...')
    with open('data/p2a.pickle') as f: p2a = pickle.load(f)
    with open('data/a2p.pickle') as f: a2p = pickle.load(f)
  logging.info('...done!\n')
  return p2a, a2p

def getResults(p2a, a2p, pf, msms, info=''):
  '''getResults:
  Fetches our traceroute measurements, exluding redundant probes and creating
  lists of AS/IXP path sets for each probe.

  @param p2a    Dictionary with probe IDs to AS numbers.
  @param a2p    Dictionary with AS numbers to probe IDs.
  @param pf     Path filter, i.e., hops (list) that should be excluded.
  @param msms   List of RIPE Atlas measurement identifiers.
  '''
  logging.info('Fetching results for {}...'.format(info))
  raw = ripeh.fetchRawResults(msms)

  logging.info('Parsing and pruning AS results...')
  p2rAS, p2f = ripeh.parseRawTracerouteResults(raw, ripeh.makePath, *pf)
  p2rAS, p2f = ripeh.pruneResults(p2rAS, p2f, p2a, a2p)

  logging.info('Parsing IXP results...')
  p2rIXP, p2f = ripeh.parseRawTracerouteResults(raw, caidah.makePath)
  p2rIXP, p2f = ripeh.pruneResults(p2rIXP, p2f, p2a, a2p)

  return p2rAS, p2rIXP, p2f

def analyze(plNmax, psNmax, covNmax, p2rAS, p2rIXP, p2f, p2a, info):
  '''analyze:
  Looks at path length, path stability, probe coverage, and weighted probe
  coverage for a given traceroute target.
  '''
  pl(p2rAS, plNmax, True, info); pl(p2rIXP, plNmax, False, info)
  ps(p2rAS, psNmax, True, info); ps(p2rIXP, psNmax, False, info)
  cov(p2rAS, p2rIXP, p2a, covNmax, info)

def pl(p2r, nmax, AS, info):
  '''pl:
  Returns the fraction of paths that were of length 0...nmax+ (list).
  '''
  logging.info('Looking at {} path length...'.format(info))
  cnt, paths = [0]*(nmax+1), 0
  for pid in p2r:
    for path in p2r[pid]:
      cnt[min(len(path), nmax)] += 1
      paths += 1
  f = [ c/paths for c in cnt ]
  print 'pdf_pl{}_{}(nmax={}): {}'.format('AS' if AS else 'IXP', info, nmax, f)
  return f

def ps(p2r, nmax, AS, info):
  '''ps:
  Returns the fraction of paths that changed 1...nmax+ times (list).
  '''
  logging.info('Looking at {} path stability...'.format(info))
  cnt = [0]*(nmax+1)
  for pid in p2r:
    uniquePaths = set()
    for path in p2r[pid]:
      uniquePaths.add(frozenset(path))
    cnt[min(len(uniquePaths), nmax)] += 1 
  f = [ c/len(p2r) for c in cnt ]
  print 'pdf_ps{}_{}(nmax={}): {}'.format('AS' if AS else 'IXP', info, nmax, f)
  return f

def cov(p2rAS, p2rIXP, p2a, nmax, info):
  '''cov:
  Computes (weighted) probe coverage as 1...nmax vantage points aggregate.
  '''
  N = range(1, nmax+1)
  caida = caidarank()                               # CAIDA's largest AS ranking
  popAS = poprank(p2rAS)                   # Our own popularity-based AS ranking
  popIXP = poprank(p2rIXP)                # Our own popularity-based IXP ranking

  logging.info('Looking at {} probe coverage...'.format(info))
  print 'cdf__covCaidaAS__{}(nmax={}): {}'.format(info, nmax,
    coverage(p2rAS, caida,  N))
  print 'cdf__covPopAS__{}(nmax={}): {}'.format(info, nmax,
    coverage(p2rAS, popAS,  N))
  print 'cdf__covPopIXP__{}(nmax={}): {}'.format(info, nmax,
    coverage(p2rIXP, popIXP, N))

  logging.info('Looking at {} weighted probe coverage...'.format(info))
  print 'cdf__wcovCaidaAS__{}(nmax={}): {}'.format(info, nmax,
    wcoverage(p2rAS,  p2a, caida,  info, N))
  print 'cdf__wcovPopAS__{}(nmax={}): {}'.format(info, nmax,
    wcoverage(p2rAS,  p2a, popAS,  info, N))
  print 'cdf__wcovPopIXP__{}(nmax={}): {}'.format(info, nmax,
    wcoverage(p2rIXP, p2a, popIXP, info, N))

def caidarank():
  '''caidarank:
  Returns an AS ranking created by CAIDA.
  '''
  return caidah.getRankedAsns()

def poprank(p2r):
  '''poprank:
  Returns a popularity ranking based on the most frequently traversed vantage
  points. A probe can at most increment the popularity of a vantage point once.
  '''
  traversals = {}
  for pid in p2r:
    vps = set()
    for path in p2r[pid]:
      for vp in path:
        vps.add(vp)
    for vp in vps:
      traversals.setdefault(vp, 0)
      traversals[vp] += 1
  
  ties = {}
  for vp in traversals:
    ties.setdefault(traversals[vp], [])
    ties[traversals[vp]].append(vp)

  ranking = []
  for key in sorted(ties.keys(), reverse=True):
    ranking += sorted(ties[key])
  
  return ranking

def coverage(p2r, ranking, N):
  '''coverage:
  Creates cdf data points for covered probes as n top-ranked vantage points
  aggregate.

  @param p2r      Dictionary with probe IDs to path sets. 
  @param ranking  List of top-ranked aggregators.
  @param N        List of top-ranks to test, e.g., [1,2,3,4,5,6,7,8,9,10] gives
                  ten data points as top1...top10 enable aggregation.
  '''
  coverage = []
  for n in N:
    aggregators, cnt = set(ranking[:n]), 0
    for pid in p2r:
      covered = False
      for path in p2r[pid]:
        covered = covered or len(path.intersection(aggregators)) > 0
      if covered:
        cnt += 1
    coverage.append(cnt / len(p2r))
  return coverage

ipv4space = 0
def wcoverage(p2r, p2a, ranking, info, N):
  '''wcoverage:
  Creates cdf data points for covered probes with weights (IPv4 AS size) as n in
  N top-ranked vantage points aggregate.

  @param p2r      Dictionary with probe IDs to path sets. 
  @param p2a      Dictionary with probe IDs to AS numbers.
  @param ranking  List of top-ranked aggregators.
  @param N        List of top-ranks to test, e.g., [1,2,3,4,5,6,7,8,9,10] gives
                  ten data points as top1...top10 enable aggregation.
  '''
  p2w = {}
  for pid in p2r:
    p2w[pid] = ripeh.weight(p2a[pid])
  weights = sum(p2w.values())

  global ipv4space
  if weights != ipv4space:
    ipv4space = weights
    print 'ipv4space__{}: {}'.format(info, ipv4space / (2**32))

  coverage = []
  for n in N:
    aggregators, cnt = set(ranking[:n]), 0
    for pid in p2r:
      covered = False
      for path in p2r[pid]:
        covered = covered or len(path.intersection(aggregators)) > 0
      if covered:
        cnt += p2w[pid]
    coverage.append(cnt / weights)
  return coverage

if __name__ == '__main__':
  logging.basicConfig(
    level = logging.INFO,
    format = '%(levelname)s: %(message)s',
    filename = 'analyze.log',
    filemode = 'w',
  )
  pathFilter = [ '*', 'Private', 'Unknown' ]                    # AS path filter
  main(
    plNmax = 5,                               # Group paths of lengths 5 or more
    psNmax = 5,                              # Group probes with 5 or more paths
    covNmax = 1024,                 # Coverage as 1...n vantage points aggregate
    pfGoo = pathFilter + [ 15169 ],                     # exclude destination AS
    pfNor = pathFilter + [ 2603 ],                      # exclude destination AS
    msmGoo = [
      11603880,11603881,11603882,11603883,11603884,   # 10/3-20/3: 216.239.34.64
      11784033,11784035,11784037,11784039,11784041,   # 20/3-30/3: 216.239.34.64
    ],
    msmNor = [
      11784034,11784036,11784038,11784040,11784042,    # 20/3-30/3: 194.68.13.48
      11826645,11826646,11826647,11826648,11826649,    # 30/3-9/4:  194.68.13.48
    ]
  )
