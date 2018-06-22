#!/bin/bash

pushd /sys/class/net/enp1s0f0/device/msi_irqs/
for i in *; do echo 0 > /proc/irq/$i/smp_affinity_list; cat /proc/irq/$i/smp_affinity_list; done
popd
echo "CPU affinity set"
