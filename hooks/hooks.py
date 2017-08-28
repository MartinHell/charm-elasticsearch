#!/usr/bin/env python3
"""Setup hooks for the elasticsearch charm."""

import sys
import charmhelpers.contrib.ansible
import charmhelpers.contrib.python.packages as python
import charmhelpers.contrib.charmsupport.nrpe as nrpe
import charmhelpers.payload.execd
import charmhelpers.core.host
from charmhelpers.core import hookenv
import os
import shutil
import subprocess as sp

mountpoint = '/srv/elasticsearch'
config = hookenv.config()

hooks = charmhelpers.contrib.ansible.AnsibleHooks(
    playbook_path='playbook.yaml',
    default_hooks=[
        'config-changed',
        'cluster-relation-joined',
        'logs-relation-joined',
        'data-relation-joined',
        'data-relation-changed',
        'data-relation-departed',
        'data-relation-broken',
        'peer-relation-joined',
        'peer-relation-changed',
        'peer-relation-departed',
        'nrpe-external-master-relation-changed',
        'rest-relation-joined',
        'start',
        'stop',
        'upgrade-charm',
        'client-relation-joined',
        'client-relation-departed',
    ])


@hooks.hook('install', 'upgrade-charm')
def install():
    """Install ansible before running the tasks tagged with 'install'."""
    # Allow charm users to run preinstall setup.
    if is_container:
        config["env-vars"] = {"ES_SKIP_SET_KERNEL_PARAMETERS": "true"}
    else:
        config["env-vars"] = {}
    charmhelpers.payload.execd.execd_preinstall()
    charmhelpers.contrib.ansible.install_ansible_support(
        from_ppa=False)

    # We copy the backported ansible modules here because they need to be
    # in place by the time ansible runs any hook.
    charmhelpers.core.host.rsync(
        'ansible_module_backports',
        '/usr/share/ansible')
    update_nrpe_config()

def install_nrpe_deps():
    NAGIOSCHECK = { 'path': '/tmp/nagioscheck', 'url': 'https://github.com/MartinHell/pynagioscheck.git' }
    NAGIOS_PLUGIN = { 'path': '/tmp/nagiosplugin', 'url': 'https://github.com/Boolman/nagios-plugin-elasticsearch.git' }
    if not has_imported("Repo"):
        try:
            python.pip_install("gitpython")
            from git import Repo
        except:
            return False

    try:
        Repo.clone_from(NAGIOSCHECK['url'], NAGIOSCHECK['path'])
        Repo.clone_from(NAGIOS_PLUGIN['url'], NAGIOS_PLUGIN['path'])
        sp.Popen(["python", "setup.py", "install"], cwd=NAGIOSCHECK['path'], stdout=sp.PIPE, stderr=sp.STDOUT).communicate()
        sp.Popen(["python", "setup.py", "install"], cwd=NAGIOS_PLUGIN['path'], stdout=sp.PIPE, stderr=sp.STDOUT).communicate()
    except:
        return False


@hooks.hook('nrpe-external-master-relation-joined',
            'nrpe-external-master-relation-changed')
def update_nrpe_config():
    # python-dbus is used by check_upstart_job
    if not install_nrpe_deps():
        return

    hostname = nrpe.get_nagios_hostname()
    current_unit = nrpe.get_nagios_unit_name()
    nrpe_setup = nrpe.NRPE(hostname=hostname)
    nrpe_setup.add_check(
        shortname='elasticsearch-cluster-status',
        description='Elasticsearch cluster status check {%s}' % current_unit,
        check_cmd=('/usr/local/bin/check-elasticsearch')
    )
    nrpe_setup.write()

@hooks.hook('data-relation-joined', 'data-relation-changed')
def data_relation():
    if hookenv.relation_get('mountpoint') == mountpoint:
        # Other side of relation is ready
        migrate_to_mount(mountpoint)
    else:
        # Other side not ready yet, provide mountpoint
        hookenv.log('Requesting storage for {}'.format(mountpoint))
        hookenv.relation_set(mountpoint=mountpoint)


@hooks.hook('data-relation-departed', 'data-relation-broken')
def data_relation_gone():
    hookenv.log('Data relation no longer present, stopping elasticsearch.')
    charmhelpers.core.host.service_stop('elasticsearch')


def migrate_to_mount(new_path):
    """Invoked when new mountpoint appears. This function safely migrates
    elasticsearch data from local disk to persistent storage (only if needed)
    """
    old_path = '/var/lib/elasticsearch'
    if os.path.islink(old_path):
        hookenv.log('{} is already a symlink, skipping migration'.format(
            old_path))
        return True
    # Ensure our new mountpoint is empty. Otherwise error and allow
    # users to investigate and migrate manually
    files = os.listdir(new_path)
    try:
        files.remove('lost+found')
    except ValueError:
        pass
    if files:
        raise RuntimeError('Persistent storage contains old data. '
                           'Please investigate and migrate data manually '
                           'to: {}'.format(new_path))
    os.chmod(new_path, 0o700)
    charmhelpers.core.host.service_stop('elasticsearch')
    # Ensure we have trailing slashes
    charmhelpers.core.host.rsync(os.path.join(old_path, ''),
                                 os.path.join(new_path, ''),
                                 options=['--archive'])
    shutil.rmtree(old_path)
    os.symlink(new_path, old_path)
    charmhelpers.core.host.service_start('elasticsearch')


def is_container():
    """Return True if system is running inside a container"""
    virt_type = sp.check_output('systemd-detect-virt').decode().strip()
    if virt_type == 'lxc':
        return True
    else:
        return False


if __name__ == "__main__":
    hooks.execute(sys.argv)
