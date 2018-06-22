# Overview
Here we show how to download and process our RIPE Atlas traceroute measurements.
Run `analyze.py` to reproduce path length, path stability, and (un)weighted
probe coverage. View progress by inspecting `analyze.log`.

## Dependencies
### Python 2.7
Install the following dependencies to run our code on a fresh Ubuntu 18.04
server installation.
```
sudo apt install python-minimal python-pip
sudo pip install requests json_lines pyasn netaddr ripe.atlas.sagan \
  ripe.atlas.cousteau
```

### Download public data sets
To map IP addresses to IXP identifiers we used a
  [public data set from CAIDA](https://www.caida.org/data/ixps/).
After filling out the form on how you will use the data set, put it in the
`data` directory as follows:

```
wget http://data.caida.org/datasets/ixps/ix-asns_201802.jsonl
tail -n +2 ix-asns_201802.jsonl > data/ix-asns.jsonl
```

To map IP addresses to AS numbers we used another
  [public data set from Routeviews](http://archive.routeviews.org/bgpdata/2018.03/RIBS/).
Put it in the `data` directory as follows:

```
wget ftp://archive.routeviews.org//bgpdata/2018.03/RIBS/rib.20180312.1400.bz2
pyasn_util_convert.py --single rib.20180312.1400.bz2 data/ip2as.db
```

We used REST APIs to obtain
  [RIPE Atlas probe metadata](https://atlas.ripe.net/docs/api/v2/reference/#!/probes/Probe_List_GEt) and
  [CAIDA's largest AS rank](http://as-rank.caida.org/api/v1).
Although these data sets can be fetched again by setting `refresh=True` in our
scripts, the results may differ unless the already provided snapshots are used.
