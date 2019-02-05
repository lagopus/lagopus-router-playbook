#!/usr/bin/env python3

import os



class GoGet(object):

    def __init__(self, module):
        self.module = module
        self.gopath = module.params["GOPATH"]
        self.package = module.params["package"]

        self.bin = "{}/bin".format(self.gopath)
        self.pkg = "{}/pkg".format(self.gopath)
        self.src = "{}/src".format(self.gopath)

        
    def run_cmd(self, args, errmsg):
        (rc, stdout, stderr) = self.module.run_command(args)
        if rc != 0:
            msg = "{}: {}".format(errmsg, stderr)
            self.module.fail_json(msg = msg)


    def make_dir(self, path, check = False):

        if check:
            msg = "create directory {}".format(path)
            self.module.exit_json(changed = True, msg = msg)

        self.run_cmd([self.module.get_bin_path("mkdir", required = True),
                      "-p", path],
                     "failed to create {}".format(path))


    def make_dirs(self, check = False):
        # create GOPATH, GOPATH/{src, pkg, bin} directories

        changed = False
        for path in [self.gopath, self.bin, self.pkg, self.src]:
            if not os.path.exists(path):
                self.make_dir(path, check = check)
                changed = True

        return changed

    def go_get(self, check = False):
        
        if os.path.exists("{}/{}".format(self.src, self.package)):
            return False

        if check:
            msg = "go get {}".format(self.package)
            self.module.exit_json(changed = True, msg = msg)

        os.environ["GOPATH"] = self.gopath
        self.run_cmd([self.module.get_bin_path("go", required = True),
                      "get", self.package],
                     "failed to go get {}".format(self.gopath))
        return True

    def check(self):
        self.run(check = True)
        self.module.exit_json(changed = False)

    def run(self, check = False):
        r1 = self.make_dirs(check = check)
        r2 = self.go_get(check = check)
        self.module.exit_json(changed = (r1 or r2))


def main():

    module = AnsibleModule(
        argument_spec = dict(
            GOPATH  = dict(required = True),
            package = dict(required = True),
        ),
        supports_check_mode = True
    )

    goget = GoGet(module)

    if module.check_mode:
        goget.check()
    else:
        goget.run()



from ansible.module_utils.basic import *
main()


