import getpass
import logging
import os
import pwd
import socket
import requests

from Crypto.PublicKey import RSA

import consul_utils


def exec_put(args):

    log = logging.getLogger('hecate_put')

    user_name = getpass.getuser()
    hostname = socket.gethostname()

    try:
        passwd = pwd.getpwnam(user_name)
    except KeyError:
        print('User %s does not exist locally' % user_name)
        exit(1)

    user_home = passwd[5]
    ssh_dir = os.path.join(user_home, '.ssh')

    skip_local_creation = False
    id_rsa_key = os.path.join(ssh_dir, 'id_rsa')
    id_rsa_pub = os.path.join(ssh_dir, 'id_rsa.pub')

    log.info('Provisioning key for user ''%s''' % user_name)
    log.debug('User home directory ''%s''' % user_home)
    log.debug('User SSH directory ''%s''' % ssh_dir)
    log.debug('Private key ''%s''' % id_rsa_key)
    log.debug('Public key ''%s''' % id_rsa_pub)

    consul_user_path = 'ssh/authorized_keys/%s/' % user_name
    consul_public_key_path = '%s%s' % (consul_user_path, hostname)

    log.debug('Consul user path ''%s''' % consul_user_path)
    log.debug('Consul public key path ''%s''' % consul_public_key_path)

    con = consul_utils.get_conn(args)

    try:
        local_key_exists = os.path.exists(id_rsa_key)
        local_public_key_exists = os.path.exists(id_rsa_pub)
        remote_public_key_exitsts = con.kv.get(consul_public_key_path)[1] is not None

        if args.verbose:
            print 'Using user home: %s' % user_home

        if not os.path.exists(user_home):
            print 'User home directory does not exist!'
            exit(1)

        # Check if .ssh && id_rsa/id_rsa.pub exists
        if not os.path.exists(ssh_dir):
            print 'Creating %s' % ssh_dir
            os.makedirs(ssh_dir)

        if local_key_exists:
            log.warn('Local private exists: %s' % id_rsa_key)

        if local_public_key_exists:
            log.warn('Local public exists: %s' % id_rsa_pub)

        if local_public_key_exists:
            log.warn('Remote public key exists: %s' % consul_public_key_path)

        # We want to verify two conditions:
        # 1. Both the public and private key exist AND we want to overwrite the values
        # 2. OR neither the public or private keys exist
        if local_key_exists and not local_public_key_exists:
            print 'id_rsa.pub does not exist but private key does... something is wrong!'
            exit(1)

        if local_public_key_exists and not local_key_exists:
            print 'id_rsa does not exists but public key does... something is wrong!'
            exit(1)

        # In the event that both exist:
        # 1. If the overwrite flag has been set, proceed with creation
        # 2. If the remote file doesn't exist, we just need to upload it
        if local_key_exists and local_public_key_exists and not args.overwrite:

            if not remote_public_key_exitsts:
                log.info('Key pair exists locally, skipping new key generation')

                skip_local_creation = True
            else:
                print 'Existing key pair found!  Specify --overwrite to replace'
                exit(1)

        if remote_public_key_exitsts and not args.overwrite:
            print 'Existing key found at %s!  Specify --overwrite to replace' % consul_public_key_path
            exit(1)

        # Once we are here we know we can proceed with creation and upload
        # 1. Generate the key pair
        # 2. Write out ~/.ssh/id_rsa
        # 3. Write out ~/.ssh/id_rsa.pub
        # 4. Upload the public key

        if skip_local_creation:
            log.info('Reading public key information from %s' % id_rsa_pub)
            with open(id_rsa_pub, 'r') as local_public_key:
                public_key = local_public_key.read()
        else:
            print 'Generating SSH key pair...'

            log.warn('Generating new public/private key pair using RSA algorithm')

            generated_key = RSA.generate(2048)
            public_key = generated_key.publickey().exportKey('OpenSSH')

            with open(id_rsa_key, 'w') as rsa_private_key:
                os.chown(id_rsa_key, passwd[2], passwd[3])
                os.chmod(id_rsa_key, 0600)

                log.info('Writing private key to %s' % id_rsa_key)
                log.debug('chown - %s:%s' % (passwd[2], passwd[3]))
                log.debug('mode - %s' % 0600)

                rsa_private_key.write(generated_key.exportKey('PEM'))

            with open(id_rsa_pub, 'w') as rsa_public_key:
                os.chown(id_rsa_pub, passwd[2], passwd[3])

                log.info('Writing public key to %s' % id_rsa_pub)
                log.debug('chown - %s:%s' % (passwd[2], passwd[3]))

                rsa_public_key.write(public_key)

        log.info('Uploading public key to Consul: %s' % consul_public_key_path)

        if con.kv.put(consul_public_key_path, public_key) is None:
            print 'Unable to store public key in Consul at path %s' % consul_public_key_path
            exit(1)

        print 'Public key uploaded successfully... user %s is now provisioned for host %s' % (user_name, hostname)
        print 'Please allow approximately 3 hours for public key propagation'

    except requests.exceptions.ConnectionError as e:
        print 'Failed to connect to Consul host!'
        print e
        exit(1)
