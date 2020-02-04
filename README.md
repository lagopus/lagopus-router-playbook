

# lagopus-router-playbook

This repository contains ansible modules and exmaple playbooks for
lagopus-router setup, spawn, and configuration.


## Quick Start

### 1. Install lagopus-router on your local Linux machine


Install ansible and run site.yml. We tested on ubuntu 18.04.

```
sudo apt install ansible

# prepare ssh-keys or pass-phrase to execute ansible-playbook

git clone https://github.com/upa/lagopus-router-ansible.git
cd lagopus-rotuer-ansible
ANSIBLE_LIBRARY=module ansible-playbook --ask-become-pass -i hosts site.yml
```

Note that default site.yml tries to bind 0000:01:00.0 to
igb_uio. Please modify here before executing ansible if needed.

```
# in lagopus-router-ansible/site.yml
  - name: bind device to dpdk driver
    become: yes
    devbind: device=000:01:00.0 driver=igb_uio  # <= here
```

After ansible-playbook finished, run cli ($GOPATH/bin must be included
in $PATH).

```
cli
vsw>
```


### 2. Test lagopus-router using vagrant

Install VirtualBox, Vagrant, and ansible. We tested on macOS 10.13.6,
VirtualBox 5.2.24, Vagrant 2.2.23, and Ansible 2.7.6 installed from
brew.

```
brew install ansible

git clone https://github.com/upa/lagopus-router-ansible.git
cd lagopus-rotuer-ansible
ANSIBLE_LIBRARY=module vagrant up --provision
```

This Vagrantfile creates two VMs based on generic/ubuntu1804. One is a
lagopus-router and another is a simple linux node. The created
topology is shown below.

```
+----------------------------------+
|             lagopus1             |
|  +----------------------------+  |
|  | VSI1                       |  |
|  |  +----------------------+  |  |
|  |  |    Bridge Vlan100    |  |  |
|  |  |        Vlan100       |  |  |
|  |  +---+--------------+---+  |  |
|  |      |              |      |  |
|  +----------------------------+  |
|         |              |         |
|     +---+---+      +---+---+     |
|     | if0.0 |      | if1.0 |     |
|     +---+---+      +---+---+     |
|         | VID:100      | VID:100 |
|      +--+--+        +--+--+      |
|      | if0 |        | if1 |      |
+------+--+--+--------+--+--+------+
          |              |        
          |              |
          |              |
+-----+---+---+---+--+---+---+--+--|
|     |  eth2 |   |  |  eth3 |  |  |
|     +---+---+   |  +---+---+  |  |
|     10.0.0.20   |  10.0.0.21  |  |
|		  |             |  |
|		  |   testns    |  |
|                 +-------------+  |
|               node1              |
+----------------------------------+
```

Vagrant creates two ubuntu VMs, and ansible does lagopus-router
installation, configuration, and execution. After `vagrant up`
finished, you can ssh by `vagrant ssh node1` and ping to 10.0.0.21
through lagopus-router from defaulet netns on node1.

`provisioning` directory contains playbooks for this example.
`setup.yml` installs lagopus-router, and `lagopus.yml` spawns vsw and
openconfigd. `node1.yml` just creates and setup netns on node1.



## Ansible Modules for Lagopus Router

we implemented 5 ansible modules, *dpdk_install*, *devbind*,
*hugepages*, *spawn*, and *vswconfig*, for lagopus router, but they
are not exclusive to lagopus.


## dpdk_install

### Synopsis:

dpdk_install module installs DPDK from source. It also loads uio and
igb_uio modules.

### Parameters:

| Parameter | Cohices/Defaults | Comments |
|-----------|------------------|----------|
| version   | 18.11.1          | DPDK version. |
| url       | http://fast.dpdk.org/rel/dpdk-[version].tar.xz | URL where DPDK source tar ball exists |
| target    | x86_64-native-linuxapp-gcc | DPDK compile target architecture |
| build_dir | /usr/src         | where DPDK source is extracted. |
| build_shared_lib | False     | Build DPDK with CONFIG_RTE_BUILD_SHARED_LIB=y compile option |
| jobs      | 1                | number of CPUs used to compile DPDK source


### Example

```
- hosts: host
  become: yes
  tasks:
  - name: install dpdk
    dpdk_install: build_shared_lib=true jobs=6
```

This playbook installs DPDK version 18.11.1 into /usr/src, and the
build directory is /usr/src/dpdk-stable-18.11.1/build as default.



## devbind

### Synopsis:

devbind module bind NIC to specified drivers. This module *DOES NOT*
use dpdk-devbind.py. This module modify /sys/bus/pci/devices/[PCI_BUS]
and /sys/bus/pci/drivers/[DRV_NAME]. Thus, this module does not depend
on DPDK so that it can apply to any PCI devices and device drivers
mapping. Note that this requires Linux kernel 3.15 and later because
of /sys/bus/pci/devices[PCI_BUS]/driver_override.


### Parameters:

| Parameter | Cohices/Defaults | Comments |
|-----------|------------------|----------|
| device    | Required         | PCI bus number |
| driver    | Required         | device driver name such as igb_uio, mlx5_core, ixgbe, etc |


### Example:

```
- hosts: host
  become: yes
  tasks:
  - name: bind device to dpdk driver
    devbind: device=000:01:00.0 driver=igb_uio
```


## hugepages

### Synopsis:

hugepages module allocates hugepages.


### Parameters:

| Parameter | Cohices/Defaults | Comments |
|-----------|------------------|----------|
| size      | 2M or 1G, defualt is 2M | size of a hugepage |
| nr_pages  | Required         | number of hugepages to be allocated |
| node      | 0                | Numa node where hugepages to be allocated |


### Example:

```
- hosts: host
  become: yes
  tasks:
  - name: set hugepages
    hugepages: nr_pages=1024
```



## spawn

### Synopsis:

spawn module spawns a program as a daemon process. Unlike *command*
module, spawn module manages existance of the process. Note that this
module must work with *async* and *poll* modules.


### Parameters:

| Parameter | Cohices/Defaults | Comments |
|-----------|------------------|----------|
| args      | Required         | command arguments |
| stdout    | /dev/null        | file path in which stdout output redirected |
| stderr    | /dev/null        | file path in which stderr output redirected |
| pidfile   | /var/run/[command] | pid file path |
| respawn   | false            | if true, the existing process is killed and respawned |
| cwd       | ansible default dir | working directory |

When respawn is false, spawn module checks pidfile. If the pidfile
exists, it checks existance of a process with the pid. If the pidfile
does not exist, it checks all processes and there cmdline.


### Example:

```
- hosts: host
  become: yes
  tasks:
  - name: spawn vsw
    spawn:
      args: vsw -v -f /home/upa/work/vsw-dir/vsw1.conf
      pidfile: /tmp/vsw.pid
      stderr: /tmp/vsw-stderr
      stdout: /tmp/vsw-stdout
      respawn: true
    async: 10
    poll: 1
    become: yes
```


## vswconfig


### Synopsis:

vswconfig module is a lagopus-router specific module (correctly,
openconfigd-specific). It configures vsw through cli_command of
openconfigd.


| Parameter | Cohices/Defaults | Comments |
|-----------|------------------|----------|
| config    | Required         | a command line for configuration mode |
| cli_command | cli_command    | path for cli_command |


### Example:

```
- hosts: host
  vars:
    GOPATH : /home/upa/go
  environment:
    GOPATH: "{{ GOPATH }}"
    PATH: "{{ lookup('env', 'PATH') }}:{{ GOPATH }}/bin"
  tasks:
  - name: configure vsw
    vswconfig: config={{ item }}
    with_items:
      - set network-instances network-instance vsi3 config type L2VSI
      - set network-instances network-instance vsi3 config enabled true
      - commit
```

cli_command is usually installed in $GOPATH/bin directory. To execute
cli_command from asnbile, set GOPATH and $GOPATH/bin in PATH env
variable, or use `cli_command` parameter to specifiy cli_command path.
