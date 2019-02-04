

## lagopus-router-ansible

Memo

### dpdk_install

Default directory is /usr/src, and default dpdk version is 17.11.1 for
lagopus


### devbind module

This module does not uses dpdk-devbind.py. It modify
/sys/bus/pci/devices/[PCI_BUS] and /sys/bus/pci/drivers/[DRV_NAME].
Note that this uses /sys/bus/pci/devices[PCI_BUS]/driver_override that
requires Linux kernel 3.15 and later.


