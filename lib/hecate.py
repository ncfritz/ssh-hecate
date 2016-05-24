#!/usr/bin/python
import argparse
import getpass
import socket

import hecate_util
from hecate_put import exec_put
from hecate_list import exec_list
from hecate_get import exec_get
from hecate_delete import exec_delete
from hecate_sync import exec_sync
from hecate_config import exec_config
from hecate_service import exec_service

# hecate provision
# hecate list
# hecate get
# hecate delete
# hecate sync
# hecate config
# hecate daemon

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='hecate')
    hecate_util.setup_common_args(parser)
    subparsers = parser.add_subparsers(title='Valid commands',
                                       description='command')

    put_parser = subparsers.add_parser('provision')
    put_parser.set_defaults(func=exec_put)
    put_parser.add_argument('--overwrite',
                            default=False,
                            action='store_true',
                            required=False,
                            help='Overwrite the existing value if present in Consul',
                            dest='overwrite')

    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(func=exec_list)
    list_parser.add_argument('--type', '-t',
                             default='keys',
                             choices=['users', 'keys'],
                             required=False,
                             help='The type of entity to list',
                             dest='type')
    list_parser.add_argument('--user', '-u',
                             default=getpass.getuser(),
                             required=False,
                             help='The user to list entities for, defaults to current user',
                             dest='user_name')

    get_parser = subparsers.add_parser('get')
    get_parser.set_defaults(func=exec_get)
    get_parser.add_argument('--user', '-u',
                            default=getpass.getuser(),
                            required=False,
                            help='The user to get the public key for, defaults to current user',
                            dest='user_name')
    get_parser.add_argument('--host', '-uh',
                            default=socket.gethostname(),
                            required=False,
                            help='The host to get the public key for, defaults to current host',
                            dest='host_name')

    delete_parser = subparsers.add_parser('delete')
    delete_parser.set_defaults(func=exec_delete)
    delete_parser.add_argument('--user', '-u',
                               default=getpass.getuser(),
                               required=False,
                               help='The user to delete the public key for, defaults to current user',
                               dest='user_name')
    delete_parser.add_argument('--host', '-uh',
                               default=None,
                               help='The host to delete the public key for, defaults to current host, if not '
                                    'specified will completely remove the user',
                               dest='host_name')
    delete_parser.add_argument('--force', '-f',
                               default=False,
                               action='store_true',
                               required=False,
                               help='Force the operation, this will suppress the [y/N] prompt',
                               dest='force')

    sync_parser = subparsers.add_parser('sync')
    sync_parser.set_defaults(func=exec_sync)
    sync_parser.add_argument('--user', '-u',
                             default=getpass.getuser(),
                             required=False,
                             help='The user to get the public key for, defaults to current user',
                             dest='user_name')
    sync_parser.add_argument('--all', '-a',
                             default=False,
                             action='store_true',
                             required=False,
                             help='Perform sync for all users',
                             dest='all')

    config_parser = subparsers.add_parser('config')
    config_parser.set_defaults(func=exec_config)
    config_parser.add_argument('--global', '-g',
                               default=False,
                               action='store_true',
                               required=False,
                               help='Global configuration',
                               dest='editGlobal')
    config_parser.add_argument('--edit', '-e',
                               default=False,
                               action='store_true',
                               required=False,
                               help='Edit configuration',
                               dest='edit')

    daemon_parser = subparsers.add_parser('daemon')
    daemon_parser.set_defaults(func=exec_service)
    daemon_parser.add_argument('--frequency', '-f',
                               type=int,
                               required=False,
                               default=60 * 60 * 3,  # three hours
                               help='How often to run the sync in seconds',
                               dest='frequency')
    daemon_parser.add_argument('--jitter', '-j',
                               type=int,
                               default=60 * 60,  # one hour
                               required=False,
                               help='The amount to potentially jitter the frequency',
                               dest='jitter')

    args = parser.parse_args()
    hecate_util.setup_logging(args)

    try:
        args.func(args)
    except KeyboardInterrupt:
        # Skip to the new line
        print
