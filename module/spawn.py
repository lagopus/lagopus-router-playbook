#!/usr/bin/env python3

import os
import time
import signal

class Spawn(object):

    def __init__(self, module):
        self.module = module

        args = [arg for arg in module.params["args"].split(" ") if arg]
        self.args = args
        self.stdout = module.params["stdout"]
        self.stderr = module.params["stderr"]
        self.pidfile = module.params["pidfile"]
        self.respawn = module.params["respawn"]
        self.cwd = module.params["cwd"]

        if self.pidfile == "None":
            self.pidfile = "/var/run/{}".format(os.path.basename(self.args[0]))

        if self.cwd == "None":
            self.cwd = None
            

    def get_args(self, pid):

        try:
            with open("/proc/{}/cmdline".format(pid)) as f:
                cmdline = f.read().strip()
                args = [arg for arg in cmdline.split('\0') if arg]
                return args
        except Exception as e:
            msg = "failed to get args of pid {}: {}".format(pid, e)
            self.module.fail_json(msg)


    def find_process(self):
        # find a process matches self.pidfile or self.args and
        # returns psutil.Process

        pids = [int(pid) for pid in os.listdir("/proc") if pid.isdigit()]

        if os.path.exists(self.pidfile):
            with open(self.pidfile, "r") as f:
                pid = int(f.read().strip())
            if pid in pids:
                return pid
            
        for pid in pids:
            args = self.get_args(pid)

            matched = True
            if len(self.args) != len(args):
                matched = False
            else:
                for x in range(len(self.args)):
                    if self.args[x] != args[x]:
                        matched = False
                        break
                
            if matched:
                return pid

        return None


    def execute(self):
        try:
            stdout = open(self.stdout, "w")
            stderr = open(self.stderr, "w")
            p = subprocess.Popen(self.args, stdout = stdout, stderr = stderr,
                                 cwd = self.cwd)
        except Exception as e:
            msg = "failed to execute '{}': {}".format(self.args, e)
            self.module.fail_json(msg = msg)

        try:
            with open(self.pidfile, "w") as f:
                f.write(str(p.pid))
        except Exception as e:
            msg = "failed to wirte pid file {}: {}".format(self.pidfile, e)
            self.module.fail_json(msg = msg)
            


    def check(self):
        if self.respawn:
            # 'respawn' always kills and respawns the process
            self.module.exit_json(changed = True)

        if self.find_process():
            self.module.exit_json(changed = False)
        else:
            self.module.exit_json(changed = True)


    def run(self):

        pid = self.find_process()

        if pid:
            if not self.respawn:
                self.module.exit_json(changed = False)
            else:
                # the process exists and respawn specified.
                # kill the process, and spawn the process
                os.kill(pid, signal.SIGINT)
                time.sleep(3) # XXX

        self.execute()
        self.module.exit_json(changed = True)


def main():

    module = AnsibleModule(
        argument_spec = dict(
            args = dict(required = True),
            stdout = dict(required = False, default = "/dev/null"),
            stderr = dict(required = False, default = "/dev/null"),
            pidfile = dict(required = False, default = None),
            respawn = dict(required = False, type = "bool", default = False),
            cwd = dict(required = False, default = None),
        )
    )

    daemon = Spawn(module)

    if module.check_mode:
        daemon.check()
    else:
        daemon.run()

from ansible.module_utils.basic import *
main()
