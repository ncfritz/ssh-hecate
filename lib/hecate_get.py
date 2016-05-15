import logging

import requests

import consul_utils


def exec_get(args):

    log = logging.getLogger(name='hecate_get')

    consul_user_path = 'ssh/authorized_keys/%s/' % args.user_name
    consul_key_path = '%s%s' % (consul_user_path, args.host_name)

    con = consul_utils.get_conn(args)

    try:
        log.info('Getting key for user ''%s''' % args.user_name)
        log.info('Getting key for host ''%s''' % args.host_name)
        log.debug('Using key path ''%s''' % consul_key_path)

        if con.kv.get(consul_user_path, recurse=True)[1] is None:

            print 'User %s does not exist in Consul' % args.user_name
            exit(0)

        key = con.kv.get(consul_key_path)[1]

        if key is not None:
            log.info('CreateIndex: %s' % key['CreateIndex'])
            log.info('ModifiedIndex: %s' % key['ModifyIndex'])
            log.info('LockIndex: %s' % key['LockIndex'])
            log.info('Key: %s' % key['Key'])
            log.info('Flags: %s' % key['Flags'])

            print '\n%s\n' % key['Value'].strip()

        else:
            print 'User %s does not have a public key uploaded for host %s' % (args.user_name, args.host_name)

    except requests.exceptions.ConnectionError as e:
        print 'Failed to connect to Consul host!'
        log.critical(e)
        exit(1)
