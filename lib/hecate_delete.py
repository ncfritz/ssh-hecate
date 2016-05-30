import os
import pwd
import logging
import requests

import consul_utils
import hecate_util


def exec_delete(args):

    log = logging.getLogger(name='hecate_delete')

    log.debug('Executing as %s(%s)' % (os.getlogin(), os.getuid()))

    try:
        user_to_delete = pwd.getpwnam(args.user_name)
        log.debug('Expecting uid 0 or %s' % user_to_delete[2])
    except KeyError:
        if os.getuid() == 0:
            log.info('User %s does not exist locally, but we are running as root... proceeding' % args.user_name)
            pass
        else:
            print 'User %s does not exist locally, must be run as root to delete user %s' % \
                  (args.user_name, args.user_name)
            exit(1)

    # Access check, we must be running as root or the uid of the specific user that was requested
    if os.getuid() != 0 and user_to_delete[2] != os.getuid():
        print 'Must be run as the currently logged in user or root'
        exit(1)

    consul_ssh_path = 'ssh/authorized_keys/'
    consul_user_path = '%s%s/' % (consul_ssh_path, args.user_name)
    consul_key_path = '%s%s' % (consul_user_path, args.host_name)

    con = consul_utils.get_conn(args)

    try:
        log.info('Deleting key for user ''%s''' % args.user_name)
        log.info('Deleting key for host ''%s''' % args.host_name)
        log.debug('Using key path ''%s''' % consul_key_path)

        keys_result = con.kv.get(consul_user_path, recurse=True, keys=True)

        if keys_result[1] is None:
            print 'User %s does not exist in Consul' % args.user_name
            exit(0)

        if not args.force:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!!                    WARNING                    !!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print
            print 'This operation is permanent and can cause disruption to user SSH access to systems!'
            print
            print 'The following keys will be deleted for user %s:' % args.user_name

            keys = []

            for key_entry in keys_result[1]:

                key_entry = key_entry[len(consul_user_path)-1:]

                if len(key_entry) > 0:
                    key_entry = key_entry[1:] if key_entry.startswith('/') else key_entry
                    key_entry = key_entry[:-1] if key_entry.endswith('/') else key_entry

                    if key_entry == args.host_name or args.host_name is None:
                        keys.append(key_entry)

            hecate_util.print_columns(keys)
            print

            confirm = raw_input('Confirm delete [y/N]: ').lower() in ['y', 'yes']

            if not confirm:
                print 'Aborting...'
                exit(0)

        if args.host_name is None:
            log.info('Deleting keys at %s' % consul_user_path)

            for key_entry in keys_result[1]:
                print 'Deleting key at: %s' % key_entry
                con.kv.delete(key_entry)
        else:
            log.info('Deleting key at %s' % consul_key_path)
            con.kv.delete(consul_key_path)

        # Ensure that the ssh/authorized_keys path still exists in Consul
        con.kv.put(consul_ssh_path, None)

    except requests.exceptions.ConnectionError as e:
        print 'Failed to connect to Consul host!'
        log.critical(e)
        exit(1)
