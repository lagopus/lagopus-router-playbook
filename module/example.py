#!/usr/bin/env python


def main():
    module = AnsibleModule(
        argument_spec = {}
    )

    result = dict(
        some_key = "test",
    )

    module.exit_json(changed = False, **result)


from ansible.module_utils.basic import *

main()
