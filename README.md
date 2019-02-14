

# lagopus-router-ansible

This repository contains ansible modules and exmaple playbooks for
lagopus-router setup, spawn, and configuration.


## Ansible Modules for Lagopus Router

we implemented 5 ansible modules, *dpdk_install*, *devbind*,
*hugepages*, *spawn*, and *vswconfig*, for lagopus router, but they
are not exclusive to lagopus.

### dpdk_install

#### Synopsis:

dpdk_install module installs DPDK from source. It also loads uio and
igb_uio modules.

#### Parameters:

| Parameter | Cohices/Defaults | Comments |
|-----------|------------------|----------|
| version   | 17.11.1          | DPDK version. |
| url       | http://fast.dpdk.org/rel/dpdk-[version].tar.xz | URL where DPDK source tar ball exists |
| target    | x86_64-native-linuxapp-gcc | DPDK compile target architecture |
| build_dir | /usr/src         | where DPDK source is extracted. |
| build_shared_lib | False     | Build DPDK with CONFIG_RTE_BUILD_SHARED_LIB=y compile option |
| jobs      | 1                | number of CPUs used to compile DPDK source

#### Examples

```
- hosts: host
  become: yes
  tasks:
  - name: install dpdk
    dpdk_install: build_shared_lib=true jobs=6
```

This playbook installs DPDK version 17.11.1 at /usr/src. The build
directory is /usr/src/dpdk-stable-17.11.1/build as a result.



### devbind

#### Synopsis:

devbind module bind NIC to specified drivers. This module *DOES NOT*
uses dpdk-devbind.py. This module modify
/sys/bus/pci/devices/[PCI_BUS] and /sys/bus/pci/drivers/[DRV_NAME].
Thus, this module does not depend on DPDK, so that it can apply to any
PCI devices and device drivers mapping. Note that this requires Linux
kernel 3.15 and later because of
/sys/bus/pci/devices[PCI_BUS]/driver_override.


#### Parameters:

| Parameter | Cohices/Defaults | Comments |
|-----------|------------------|----------|
| device    |                  | PCI bus number |
| driver    |                  | device driver name such as igb_uio, mlx5_core, ixgbe, etc. |


#### Examples:

```
- hosts: host
  become: yes
  tasks:
  - name: bind device to dpdk driver
    devbind: device=000:01:00.0 driver=igb_uio
```