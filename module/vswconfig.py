#!/usr/bin/env python3

import os

class VswConfig(object):

    def __init__(self, module):
        self.module = module

        args = [ arg for arg in module.params["config"].split(" ") if arg ]
        self.config_args = args
        self.cli_command = module.params["cli_command"]


    def run(self):
        
        args = [ self.cli_command, "-m", "configure" ] + self.config_args
        (rc, stdout, stderr) = self.module.run_command(args)

        if rc != 0:
            msg = "{}: {}".format("config failed {}: {}".format(args), stderr)
            self.module.fail_json(msg)

        self.module.exit_json(changed = True)
            

def main():

    module = AnsibleModule(
        argument_spec = dict(
            config      = dict(required = True),
            cli_command = dict(required = False, default = "cli_command")
        ),
        supports_check_mode = False,
    )

    vswconfig = VswConfig(module)

    vswconfig.run()
    

from ansible.module_utils.basic import *
main()
        
