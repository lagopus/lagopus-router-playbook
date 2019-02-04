#!/usr/bin/env python3

import os

SYS_DEVICES = "/sys/bus/pci/devices"
SYS_DRIVERS = "/sys/bus/pci/drivers"

class Devbind(object):

    def __init__(self, module):

        self.module = module
        self.device = self.pci_bus_num(module.params["device"])
        self.driver = module.params["driver"]
        self.sys_device_path = "{}/{}".format(SYS_DEVICES, self.device)
        self.sys_driver_path = "{}/{}".format(SYS_DRIVERS, self.driver)

        if self.driver == "None":
            self.driver = None # not bind to any drivers

        # validate
        if not os.path.exists(self.sys_device_path):
            msg = "deivce {} does not exist".format(self.device)
            self.module.fail_json(msg = msg)

        if not os.path.exists(self.sys_driver_path):
            msg = "driver {} does not exist".format(self.driver)
            self.module.fail_json(msg = msg)


    def pci_bus_num(self, device):
        dom, bus, slot_func = device.split(":")
        slt, fnc = slot_func.split(".")
        return "{:04x}:{:02x}:{:02x}.{:x}".format(int(dom, 16), int(bus, 16),
                                                  int(slt, 16), int(fnc, 16))


    def get_current_driver(self):

        driver_path = "{}/{}".format(self.sys_device_path, "driver")
        if not os.path.exists(driver_path):
            return None
        else:
            return os.path.basename(os.readlink(driver_path))

    def will_changed(self):

        if self.driver != self.get_current_driver():
            return True
        else:
            return False
        

    def check(self):
        if self.will_changed():
            self.module.exit_json(changed = True)
        else:
            self.module.exit_json(changed = False)


    def sysfs_write(self, path, value):

        try:
            f = open(path, "w")
        except Exception as e:
            msg = "failed to open {}: {}".format(path, e)
            self.module.fail_json(msg = msg)
            
        f.write(value)
        f.close()


    def run(self):

        if not self.will_changed():
            self.module.exit_json(changed = False)
            
        # unbind
        if self.get_current_driver():
            unbind_path = "{}/driver/unbind".format(self.sys_device_path)
            self.sysfs_write(unbind_path, self.device)
        
        # driver_override
        override_path = "{}/driver_override".format(self.sys_device_path)
        self.sysfs_write(override_path, self.driver)

        # bind
        bind_path = "{}/bind".format(self.sys_driver_path)
        self.sysfs_write(bind_path, self.device)

        self.module.exit_json(changed = True)


def main():

    module = AnsibleModule(
        argument_spec = dict(
            device = dict(required = True),
            driver = dict(required = True),
        ),
        supports_check_mode = True
    )

    devbind = Devbind(module)

    if module.check_mode:
        devbind.check()
    else:
        devbind.run()


from ansible.module_utils.basic import *
main()
