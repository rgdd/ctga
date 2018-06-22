#!/bin/bash

#
# Run this script to start an interactive Mininet session
#

source myenv.sh

SRC=main.p4
TOPO=topology.py
BUILD=build
JSON=$BUILD/main.json
TARGET=$BMV2/targets/simple_switch/simple_switch
CLIAPI=$BMV2/targets/simple_switch/sswitch_CLI

mkdir -p $BUILD

p4c $SRC -o $BUILD            # compile
sudo $TARGET >/dev/null 2>&1  # warm up
sudo PYTHONPATH=$PYTHONPATH:$BMV2/mininet/ python $TOPO \
  --behavioral-exe $TARGET \
  --json $JSON \
  --cli $CLIAPI
