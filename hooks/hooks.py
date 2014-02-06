#!/usr/bin/env python
"""Setup hooks for the elasticsearch charm."""

import sys
import charmhelpers.contrib.ansible


hooks = charmhelpers.contrib.ansible.AnsibleHooks(
    playbook_path='playbook.yaml',
    default_hooks=[
        'config-changed',
        'cluster-relation-joined',
        'start',
        'stop',
    ])


@hooks.hook()
def install():
    """Install ansible before running the tasks tagged with 'instal'."""
    charmhelpers.contrib.ansible.install_ansible_support(from_ppa=True)


if __name__ == "__main__":
    hooks.execute(sys.argv)
