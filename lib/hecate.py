#!/usr/bin/python
import argparse
import getpass
import socket

import hecate_util
from hecate_get import exec_get
from hecate_list import exec_list
from hecate_put import exec_put
from hecate_sync import exec_sync
from hecate_service import exec_service

# hecate put
# hecate list
# hecate get
# hecate sync
# hecate daemon

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    hecate_util.setupCommonArgs(parser)
    subparsers = parser.add_subparsers(title = 'Valid commands',
                                       description = 'command',
                                       help = 'command help')


    put_parser = subparsers.add_parser('provision')
    put_parser.set_defaults(func = exec_put)
    put_parser.add_argument('--overwrite',
                            default = False,
                            action = 'store_true',
                            required = False,
                            help = 'Overwrite the existing value if present in Consul',
                            dest = 'overwrite')

    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(func = exec_list)
    list_parser.add_argument('--type', '-t',
                             default = 'keys',
                             choices = ['users', 'keys'],
                             required = False,
                             help = 'The type of entity to list',
                             dest = 'type')
    list_parser.add_argument('--user', '-u',
                             default = getpass.getuser(),
                             required = False,
                             help = 'The user to list entities for, defaults to current user',
                             dest = 'user_name')

    get_parser = subparsers.add_parser('get')
    get_parser.set_defaults(func = exec_get)
    get_parser.add_argument('--user', '-u',
                            default = getpass.getuser(),
                            required = False,
                            help = 'The user to get the public key for, defaults to current user',
                            dest = 'user_name')
    get_parser.add_argument('--host', '-uh',
                            default = socket.gethostname(),
                            required = False,
                            help = 'The host to get the public key for, defaults to current host',
                            dest = 'host_name')

    sync_parser = subparsers.add_parser('sync')
    sync_parser.set_defaults(func = exec_sync)
    sync_parser.add_argument('--user', '-u',
                             default = getpass.getuser(),
                             required = False,
                             help = 'The user to get the public key for, defaults to current user',
                             dest = 'user_name')
    sync_parser.add_argument('--all', '-a',
                             default = False,
                             action = 'store_true',
                             required = False,
                             help = 'Perform sync for all users',
                             dest = 'all')

    daemon_parser = subparsers.add_parser('daemon')
    daemon_parser.set_defaults(func = 'exec_service')
    daemon_parser.add_argument('--frequency', '-f',
                               type = int,
                               required = False,
                               default = 60 * 60 * 3, # three hours
                               help = 'How often to run the sync in seconds',
                               dest = 'frequency')
    daemon_parser.add_argument('--jitter', '-j',
                               type = int,
                               default = 60 * 60, # one hour
                               required = False,
                               help = 'The amount to potentially jitter the frequenct',
                               dest = 'jitter')

    args = parser.parse_args()
    hecate_util.setupLogging(args)
    args.func(args)

