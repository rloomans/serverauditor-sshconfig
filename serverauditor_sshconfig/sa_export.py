#!/usr/bin/env python
#
# Copyright 2013 Crystalnix

import sys

from serverauditor_sshconfig.core.application import SSHConfigApplication, description
from serverauditor_sshconfig.core.api import API
from serverauditor_sshconfig.core.cryptor import RNCryptor
from serverauditor_sshconfig.core.logger import PrettyLogger
from serverauditor_sshconfig.core.ssh_config import SSHConfig


class ExportSSHConfigApplication(SSHConfigApplication):

    def run(self):
        self._greeting()

        self._get_sa_user()
        self._get_sa_keys_and_connections()
        self._decrypt_sa_keys_and_connections()

        self._parse_local_config()
        self._sync_for_export()
        self._choose_new_hosts()
        self._get_full_hosts()

        self._create_keys_and_connections()

        self._valediction()
        return

    def _greeting(self):
        self._logger.log("ServerAuditor's ssh config script. Export from local machine to SA servers.", color='magenta')
        return

    @description("Synchronization...")
    def _sync_for_export(self):
        def get_identity_files(host):
            return [f[1] for f in host.get('identityfile', [])]

        def is_exist(host):
            h = self._config.get_host(host, substitute=True)
            key_check = bool(h.get('identityfile', None))
            for conn in self._sa_connections:
                if key_check:
                    key_id = conn['ssh_key']
                    if key_id:
                        key_check = self._sa_keys[key_id['id']]['private_key'] in get_identity_files(h)
                    else:
                        continue
                else:
                    key_check = True

                if (conn['hostname'] == h['hostname'] and
                        conn['ssh_username'] == h['user'] and
                        conn['port'] == int(h.get('port', 22)) and
                        key_check):  # conn['label'] == h['host']
                    return True

            return False

        for host in self._local_hosts[:]:
            if is_exist(host):
                self._local_hosts.remove(host)

        return

    def _choose_new_hosts(self):
        def get_hosts_names():
            return ['%s (%d)' % (h, i) for i, h in enumerate(self._local_hosts)]

        self._logger.log("The following new hosts have been founded in your ssh config:", sleep=0)
        self._logger.log(get_hosts_names())
        number = None
        while number != '=':
            number = raw_input("You may confirm this list (enter '='), "
                               "add (enter '+') or remove (enter number) host: ").strip()

            if number == '=':
                continue

            if number == '+':
                host = raw_input("Adding host: ")
                conf = self._config.get_host(host)
                if conf.keys() == ['host']:
                    self._logger.log("There is no config for host %s!" % host, file=sys.stderr)
                else:
                    self._local_hosts.append(host)

                self._logger.log("Hosts:\n%s" % get_hosts_names())

            else:
                try:
                    number = int(number)
                except ValueError:
                    pass
                else:
                    if number >= len(self._local_hosts) or number < 0:
                        self._logger.log("Incorrect index!", color='red', file=sys.stderr)
                    else:
                        self._local_hosts.pop(number)
                        self._logger.log("Hosts:\n%s" % get_hosts_names())

        self._logger.log("Ok!", color='green')
        return

    @description("Getting full information...")
    def _get_full_hosts(self):
        def encrypt_host(host):
            host['host'] = self._cryptor.encrypt(host['host'], self._sa_master_password)
            host['hostname'] = self._cryptor.encrypt(host['hostname'], self._sa_master_password)
            host['user'] = self._cryptor.encrypt(host['user'], self._sa_master_password)
            host['password'] = empty_and_encrypted

            host['ssh_key'] = []
            for i, f in enumerate(host.get('identityfile', [])):
                ssh_key = {
                    'label': self._cryptor.encrypt(f[0], self._sa_master_password),
                    'private_key': self._cryptor.encrypt(f[1], self._sa_master_password),
                    'public_key': empty_and_encrypted,
                    'passphrase': empty_and_encrypted
                }
                host['ssh_key'].append(ssh_key)
            return host

        empty_and_encrypted = self._cryptor.encrypt('', self._sa_master_password)
        self._full_local_hosts = [encrypt_host(self._config.get_host(h, substitute=True)) for h in self._local_hosts]
        return

    @description("Creating keys and connections...")
    def _create_keys_and_connections(self):
        self._api.create_keys_and_connections(self._full_local_hosts, self._sa_username, self._sa_auth_key)
        return


def main():
    app = ExportSSHConfigApplication(api=API(), ssh_config=SSHConfig(), cryptor=RNCryptor(), logger=PrettyLogger())
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        pass
    return


if __name__ == "__main__":

    main()