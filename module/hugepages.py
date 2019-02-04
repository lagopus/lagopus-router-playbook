#!/usr/bin/env python3

import os

size_map = {
    "2M" : "hugepages-2048kB",
    "1G" : "hugepages-1048576kB",
}


class HugePages(object):

    def __init__(self, module):
        self.module = module
        self.size = module.params["size"]
        self.nr_pages = module.params["nr_pages"]
        self.node = module.params["node"]
        
        # validation
        if not self.size in size_map:
            msg = ("invalid hugepage size '{}', ".format(self.size) +
                   "must be {}".format(" or ".join(size_map.keys())))
            module.fail_json(msg = msg)

        node_path = "/sys/devices/system/node/node{}".format(self.node)
        if not os.path.exists(node_path):
            msg = ("invalid node number '{}',".format(self.node) +
                   "{} does not exist".format(node_path))
            module.fail_json(msg = msg)

        nr_path = "{}/hugepages/{}/nr_hugepages".format(node_path,
                                                        size_map[self.size])
        if not os.path.exists(nr_path):
            msg = ("{} does not exist".format(nr_path))
            module.fail_json(msg = msg)

        # get current hugepages
        with open(nr_path, "r") as f:
            self.nr_pages_current = int(f.read().strip())

        self.nr_path = nr_path


    def will_changed(self):
        # if current nr_pages is different from specified nr_pages,
        # this will be changed.
        if self.nr_pages != self.nr_pages_current:
            return True
        else:
            return False

    def check(self):
        if self.will_changed():
            self.module.exit_json(changed = True)
        else:
            self.module.exit_json(changed = False)

    def run(self):

        if not self.will_changed():
            self.module.exit_json(changed = False)
            
        try:
            f = open(self.nr_path, "w")
        except Exception as e:
            msg = "failed open nr_hugepages: {}".format(e)
            self.module.fail_json(msg = msg)

        try:
            f.write(str(self.nr_pages))
        except Exception as e:
            msg = "failed set nr_hugepages: {}".format(e)
            self.module.fail_json(msg = msg)
                    
        self.module.exit_json(changed = True)
            


def main():
    module = AnsibleModule(
        argument_spec = dict(
            size     = dict(choices = [ "2M", "1G" ], default = "2M"),
            nr_pages = dict(required = True, type = "int"),
            node     = dict(type = "int", default = 0),
        ),
        supports_check_mode = True
    )

    huge = HugePages(module)

    if module.check_mode:
        huge.check()
    else:
        huge.run()


from ansible.module_utils.basic import *
main()
