#!/bin/bash

# 
# This script assumes that the second most recently added bpf map is logs
#
 
id=`sudo bpftool map | tail -n4 | head -n1 | cut -d ':' -f1` 
echo '[INFO] adding log entries...'
./add-logs.py --map-id $id --dn-max 90

echo '[INFO] log dump...'
sudo bpftool map dump id $id
