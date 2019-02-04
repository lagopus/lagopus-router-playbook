#!/usr/bin/env python3

import os

class DPDKInstall(object):

    def __init__(self, module):

        self.module = module
        self.version = module.params["version"]
        self.target = module.params["target"]
        self.build_dir = module.params["build_dir"]
        self.build_shared_lib = module.params["build_shared_lib"]
        self.jobs = module.params["jobs"]

        u = "http://fast.dpdk.org/rel/dpdk-{}.tar.xz".format(self.version)
        self.url = module.params["url"] or u
        self.tar = "{}/dpdk-{}.tar.xz".format(self.build_dir, self.version)
        self.src = "{}/dpdk-stable-{}".format(self.build_dir, self.version)


    def write_dpdk_common_base(self, params):
        """
        params is a list of tuples that includes key and value.
        for exmaple, ("CONFIG_RTE_BUILD_SHARED_LIB", "y")
        """

        conf = "{}/config/common_base".format(self.src)
        conf_orig = "{}/config/common_base.oirg".format(self.src)

        # save original config if not moved
        if not os.path.exists(conf_orig):
            args = [self.module.get_bin_path("mv", required = True),
                    conf, conf_orig]
            (rc, stdout, stderr) = self.module.run_command(args)
            if rc != 0:
                msg = "failed to mv {} to {}: {}".format(conf, confi_orig,
                                                         stderr)
                self.module.fail_json(msg = msg)
                
        try:
            ofp = open(conf, "w")
            ifp = open(conf_orig, "r")
        except Exception as e:
            msg = "failed to open dpdk common_base: {}".format(e)
            self.module.fail_json(msg = msg)
            
        for line in ifp:
            outline = line
            for (k, v) in params:
                if k in line:
                    outline = "{}={}".format(k, v)
            ofp.write(outline)

        ofp.close()
        ifp.close()


    def check_dpdk_common_base(self, params):
        """
        params is a list of tuples that includes key and value.
        for exmaple, ("CONFIG_RTE_BUILD_SHARED_LIB", "y").
        if differences exist, return True, otherwise False.
        """
        conf = "{}/config/common_base".format(self.src)

        with open(conf, "r") as f:
            for line in f:
                for (k, v) in params:
                    if k in line:
                        if line.strip() != "{}={}".format(k, v):
                            return True
        return False


    def do(self, check = False):

        msg = ""
        changed = False
        params = []
        if self.build_shared_lib:
            params.append(("CONFIG_RTE_BUILD_SHARED_LIB", "y"))
        else:
            params.append(("CONFIG_RTE_BUILD_SHARED_LIB", "n"))

        # make build dir
        if not os.path.exists(self.build_dir):
            if check:
                msg = "build dir {} does not exist".format(self.build_dir)
                self.module.exit_json(changed = True, msg = msg)

            args = [self.module.get_bin_path("mkdir", required = True),
                    "-p", self.build_dir]
            (rc, stdout, stderr) = self.module.run_command(args)
            if rc != 0:
                msg = "failed to create {}: {}".format(self.build_dir, stderr)
                self.module.fail_json(msg = msg)
            
            changed = True
            msg = "make {}.".format(self.build_dir)
            
        # download and extract dpdk source
        if not os.path.exists(self.src):

            if check:
                msg = "src dir {} does not exist".format(self.src)
                self.module.exit_json(changed = True, msg = msg)

            if not os.path.exists(self.tar):
                args = [self.module.get_bin_path("wget", required = True),
                        self.url, "-O", self.tar]
                (rc, stdout, stderr) = self.module.run_command(args)
                if rc != 0:
                    msg = "failed to get {}: {}".format(self.url, stderr)
                    self.module.fail_json(msg = msg)

            # extract dpdk source
            args = [self.module.get_bin_path("tar", required = True),
                    "xf", self.tar, "-C", self.build_dir]
            (rc, stdout, stderr) = self.module.run_command(args)
            if rc != 0:
                msg = "failed to extract {}: {}, {}".format(self.tar, stderr)
                self.module.fail_json(msg = msg)

            changed = True
            msg += " extract dpdk source on {}.".format(self.tar)

        # compile and install dpdk (if not installed or config changed)
        if (not os.path.exists("/usr/local/include/dpdk") or
            self.check_dpdk_common_base(params)):

            if check:
                msg = "library /usr/local/include/dpdk does not installed"
                self.module.exit_json(changed = True, msg = msg)

            # write dpdk compile config (config/common_base)
            self.write_dpdk_common_base(params)

            # make config
            args = [self.module.get_bin_path("make", required = True),
                    "-C", self.src, "T={}".format(self.target), "config"]
            (rc, stdout, stderr) = self.module.run_command(args)
            if rc != 0:
                msg = "failed to make config dpdk: {}".format(stderr)
                self.module.fail_json(msg = msg)

            # make
            args = [self.module.get_bin_path("make", required = True),
                    "-C", self.src, "-j", str(self.jobs)]
            (rc, stdout, stderr) = self.module.run_command(args)
            if rc != 0:
                msg = "failed to compile dpdk: {}, {}".format(stderr, stdout)
                self.module.fail_json(msg = msg)

            # make install
            args = [self.module.get_bin_path("make", required = True),
                    "-C", self.src, "install"]
            (rc, stdout, stderr) = self.module.run_command(args)
            if rc != 0:
                msg = "failed to install dpdk: {}".format(stderr)
                self.module.fail_json(msg = msg)

            changed = True
            msg += " compile and install dpdk from {}.".format(self.src)

        if check:
            self.module.exit_json(changed = False)

        msg = msg if changed else None
        self.module.exit_json(changed = changed, msg = msg)


    def check(self):
        self.do(check = True)

    def run(self):
        self.do()


def main():

    module = AnsibleModule(
        argument_spec = dict(
            version = dict(required = False, type = "str",
                           default = "17.11.1"),
            url = dict(required = False, type = "str", default = None),
            target = dict(required = False, type = "str",
                          default = "x86_64-native-linuxapp-gcc"),
            build_dir = dict(required = False, type = "str",
                             default = "/usr/src"),
            build_shared_lib = dict(required = False, type = "bool",
                                    default = False),
            jobs = dict(required = False, type = "int", default = 1)
        ),
        supports_check_mode = True
    )

    dpdk = DPDKInstall(module)

    if module.check_mode:
        dpdk.check()
    else:
        dpdk.run()


from ansible.module_utils.basic import *
main()
