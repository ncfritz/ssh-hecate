import os
import pwd
import shutil
import sys

import requests

import consul_utils


def exec_sync(args):

    consul_users_path = 'ssh/authorized_keys/'

    users_to_sync = []

    con = consul_utils.get_conn(args)

    try:
        if args.all:

            # Access check, we must be running as root to execute this
            if os.getuid() != 0:
                print 'Must be run as root to sync all users'
                exit(1)

            users_result = con.kv.get(consul_users_path, keys=True, separator='/')

            if users_result[1] is None:
                print 'No remote users found for synchronization'
                exit(0)

            for user_entry in users_result[1]:

                user_entry = user_entry[len(consul_users_path):]
                user_entry = user_entry[:-1] if user_entry.endswith('/') else user_entry

                if len(user_entry) > 0:

                    try:
                        users_to_sync.append(pwd.getpwnam(user_entry))
                    except KeyError:
                        print('User %s does not exist locally, skipping' % user_entry)
        else:
            try:
                user_to_sync = pwd.getpwnam(args.user_name)

                # Access check, we must be running as root or the uid of the specific user that was requested
                if os.getuid() != 0 and user_to_sync[2] != os.getuid():
                    print 'Must be run as the currently logged in user or root'
                    exit(1)

                users_to_sync.append(user_to_sync)

            except KeyError:
                print('User %s does not exist locally' % args.user_name)
                exit(1)

        if len(users_to_sync) > 0:

            for user_to_sync in users_to_sync:

                consul_user_path = '%s/%s/' % (consul_users_path, user_to_sync[0])

                keys_result = con.kv.get(consul_user_path, recurse=True)

                if keys_result[1] is not None:

                    ssh_dir = os.path.join(user_to_sync[5], '.ssh')
                    authorized_keys_file = os.path.join(ssh_dir, 'authorized_keys')

                    if not os.path.exists(ssh_dir):
                        print 'Creating %s' % ssh_dir
                        os.makedirs(ssh_dir)

                    if os.path.exists(authorized_keys_file):
                        print 'Backing up authorized keys file'
                        shutil.copy(authorized_keys_file, '%s.bak' % authorized_keys_file)

                    sys.stdout.write('%s:'.ljust(32, ' ') % user_to_sync[0])

                    with open(authorized_keys_file, 'w') as authorized_keys:
                        os.chown(authorized_keys_file, user_to_sync[2], user_to_sync[3])

                        for key_entry in keys_result[1]:

                            if key_entry['Value'] is not None:
                                sys.stdout.write('.')
                                authorized_keys.write('%s\n' % key_entry['Value'].strip())

                        print

                else:
                    print 'No keys found in Consul for user %s' % user_to_sync[0]
        else:
            print 'No local users found for synchronization'
            exit(0)

    except requests.exceptions.ConnectionError as e:
        print 'Failed to connect to Consul host!'
        print e
        exit(1)
