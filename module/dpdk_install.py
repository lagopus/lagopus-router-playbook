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
        self.igb_uio = "{}/build/kmod/igb_uio.ko".format(self.src)


    def run_cmd(self, args, errmsg):
        args[0] = self.module.get_bin_path(args[0], required = True)
        (rc, stdout, stderr) = self.module.run_command(args)
        if rc != 0:
            msg = "{}: {}".format(errmsg, stderr)
            self.module.fail_json(msg = msg)


    def write_dpdk_common_base(self, params):
        """
        params is a list of tuples that includes key and value.
        for exmaple, ("CONFIG_RTE_BUILD_SHARED_LIB", "y")
        """

        conf = "{}/config/common_base".format(self.src)
        conf_orig = "{}/config/common_base.oirg".format(self.src)

        # save original config if not moved
        if not os.path.exists(conf_orig):
            self.run_cmd(["mv", conf, conf_orig],
                         "failed to mv {} to {}".format(conf, conf_orig))

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

    def check_kmod_installed(self, modname):
        
        with open("/proc/modules") as f:
            for line in f:
                mod = line.split(" ")[0]
                if modname == mod:
                    return True
        return False


    def do(self, check = False):

        msgs = []
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

            self.run_cmd(["mkdir", "-p", self.build_dir],
                         "failed to create {}".format(self.build_dir))
            changed = True
            msgs.append("make {}.".format(self.build_dir))
            
        # download and extract dpdk source
        if not os.path.exists(self.src):

            if check:
                msg = "src dir {} does not exist".format(self.src)
                self.module.exit_json(changed = True, msg = msg)

            if not os.path.exists(self.tar):
                self.run_cmd(["wget", self.url, "-O", self.tar],
                             "failed to get {}".format(self.url))

            # extract dpdk source
            self.run_cmd(["tar", "xf", self.tar, "-C", self.build_dir],
                         "failed to extract {}".format(self.tar))

            changed = True
            msgs.append("extract dpdk source on {}.".format(self.tar))

        # compile and install dpdk (if not installed or config changed)
        if (not os.path.exists("/usr/local/include/dpdk") or
            self.check_dpdk_common_base(params)):

            if check:
                msg = "library /usr/local/include/dpdk does not installed"
                self.module.exit_json(changed = True, msg = msg)

            # write dpdk compile config (config/common_base)
            self.write_dpdk_common_base(params)

            # make config
            self.run_cmd(["make", "-C", self.src, "T={}".format(self.target),
                          "config"], "failed to make config dpdk")

            # make
            self.run_cmd(["make", "-C", self.src, "-j", str(self.jobs)],
                         "failed to compile dpdk")

            # make install
            self.run_cmd(["make", "-C", self.src, "install"],
                         "failed to install dpdk")

            changed = True
            msgs.append(" compile and install dpdk from {}.".format(self.src))

        # install uio kernel module
        if not self.check_kmod_installed("uio"):
            if check:
                msg = "install uio kernel module"
                self.module.exit_json(changed = True, msg = msg)

            self.run_cmd(["modprobe", "uio"], "failed to modprobe uio")
            
            changed = True
            msgs.append("install uio kernel module.")

        # install igb_uio kernel module
        if not self.check_kmod_installed("igb_uio"):
            if check:
                msg = "install igb_uio kernel module"
                self.module.exit_json(changed = True, msg = msg)

            self.run_cmd(["insmod", self.igb_uio], "failed to insmod igb_uio")

            changed = True
            msgs.append("install igb_uio kernel module.")

        if check:
            self.module.exit_json(changed = False)

        msg = " ".join(msgs) if changed else None
        self.module.exit_json(changed = changed, msg = msg)


    def check(self):
        self.do(check = True)

    def run(self):
        self.do()


def main():

    module = AnsibleModule(
        argument_spec = dict(
            version          = dict(default = "18.11.1"),
            url              = dict(default = None),
            target           = dict(default = "x86_64-native-linuxapp-gcc"),
            build_dir        = dict(default = "/usr/src"),
            build_shared_lib = dict(type = "bool", default = False),
            jobs             = dict(type = "int", default = 1)
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
