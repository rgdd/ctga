#!/bin/bash

#
# This script assumes that the most recent map is secpar. It adjusts the copy
# frequency $frec_val, and dumps the entire secpar map:
#   - entry 0: current frequency
#   - entry 1: number of marked packets
#

id=`sudo bpftool map | tail -n2 | head -n1 | cut -d ':' -f1`
frec_key='0x00 0x00 0x00 0x00'
frec_val='0x01 0x00 0x00 0x00'
echo "[INFO] secpar dump (id=$id)..."
sudo bpftool map update id $id key $frec_key value $frec_val
sudo bpftool map dump id $id
