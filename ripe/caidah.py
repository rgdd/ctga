#!/usr/bin/python

import requests
import logging
import json
import json_lines as jsonl

ip2ix = {}
with open('data/ix-asns.jsonl') as f:
  for item in jsonl.reader(f):
    for ip in item['ipv4']:
      ip2ix.setdefault(ip, [])
      ip2ix[ip].append(item['ix_id'])

def getRankedAsns(timeout=10, refresh=False):
  '''getRankedAsns:
  Returns a list of top-ranked ASes.

  @param timeout  Time in seconds before server must respond; defaults to 10s.
  @param refresh  Set if a current ranking should be downloaded.
  '''
  if not refresh:
    with open('data/asnrank-2018-04-06') as f:
      return json.load(f)

  ranking, page, maxPage = [], 1, 500
  response = requests.get(
    'http://as-rank.caida.org/api/v1/asns/ranked',
    timeout=timeout,
    params = {
      'count': 0, # No ASes
    },
  )

  n = response.json()['total'] # AS count
  while (n > 0):
    response = requests.get(
      'http://as-rank.caida.org/api/v1/asns/ranked',
      timeout = timeout,
      params = {
        'page': page,
        'count': min(n, maxPage),
      },
    )
    n, page = n-min(n, maxPage), page+1
    for asn in response.json()['data']:
      ranking.append(int(asn))

  return ranking 

def makePath(hops):
  '''makePath:
  Creates a set of traversed IXP IDs using CAIDA's dataset.

  @param hops     List of traceroute hops; a hop is a list of IPv4 strings.
  @ret 1          Set of traversed IX IDs.
  '''
  ipSet = set()
  for hop in hops:
    ipSet = ipSet.union(set(hop))

  ixSet = set()
  for ip in ipSet:
    if ip is not None and ip in ip2ix:
      ixSet.add(sorted(list(set(ip2ix[ip])))[0])

  return ixSet
