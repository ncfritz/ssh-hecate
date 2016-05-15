import logging
import math

import requests

import consul_utils


def exec_list(args):

    log = logging.getLogger(name='hecate_list')

    consul_users_path = 'ssh/authorized_keys/'
    consul_user_path = '%s%s/' % (consul_users_path, args.user_name)

    con = consul_utils.get_conn(args)

    try:

        log.info('Listing values for type ''%s''' % args.type)
        log.info('Getting key for user ''%s''' % args.user_name)
        log.debug('Using user path ''%s''' % consul_user_path)

        if args.type == 'users':

            users_result = con.kv.get(consul_users_path, keys=True, separator='/')
            users = []

            for user_entry in users_result[1]:

                user_entry = user_entry[len(consul_users_path):]

                if len(user_entry) > 0:
                    user_entry = user_entry[:-1] if user_entry.endswith('/') else user_entry
                    users.append(user_entry)

            if len(users) > 0:

                print 'Found %s user entries in Consul\n' % len(users)
                print_columns(users)
                print
            else:
                print 'No users found in Consul'

        elif args.type == 'keys':

            keys_result = con.kv.get(consul_user_path, recurse=True, keys=True)

            if keys_result[1] is None:
                print 'User %s does not exist in Consul' % args.user_name
                exit(0)

            keys = []

            for key_entry in keys_result[1]:

                key_entry = key_entry[len(consul_user_path)-1:]

                if len(key_entry) > 0:
                    key_entry = key_entry[1:] if key_entry.startswith('/') else key_entry
                    key_entry = key_entry[:-1] if key_entry.endswith('/') else key_entry
                    keys.append(key_entry)

            if len(keys) > 0:

                print 'Found %s keys for user %s in Consul\n' % (len(keys), args.user_name)
                print_columns(keys)
                print
            else:
                print 'No keys found for user %s in Consul' % args.user_name

        else:
            print 'Unknown --type argument specified!'
            exit(1)

    except requests.exceptions.ConnectionError as e:
        print 'Failed to connect to Consul host!'
        log.critical(e)
        exit(1)


def print_columns(l, cols=4, columnwise=True, gap=4):

    if cols > len(l):
        cols = len(l)

    max_len = max([len(item) for item in l])

    if columnwise:
        cols = int(math.ceil(float(len(l)) / float(cols)))

    plist = [l[i: i + cols] for i in range(0, len(l), cols)]

    if columnwise:
        if not len(plist[-1]) == cols:
            plist[-1].extend([''] * (len(l) - len(plist[-1])))

        plist = zip(*plist)

    print '\n'.join([''.join([c.ljust(max_len + gap) for c in p]) for p in plist])
