import os
import json
import jsonmerge
import pwd
import logging
import getpass
import consul_utils

from IPy import IP


def exec_config(args):

    log = logging.getLogger('hecate_config')

    user_name = getpass.getuser()

    try:
        passwd = pwd.getpwnam(user_name)
    except KeyError:
        print('User %s does not exist locally' % user_name)
        exit(1)

    user_home = passwd[5]
    user_base = os.path.join(user_home, '.hecate')
    global_base = '/usr/local/hecate/etc'

    user_config_path = os.path.join(user_base, 'config.json')
    global_config_path = os.path.join(global_base, 'config.json')

    args_dict = vars(args)
    user_config = {}
    global_config = {}
    args_config = {
        'consul_host': (args_dict['consul_host'] if 'consul_host' in args_dict else None),
        'consul_port': (args_dict['consul_port'] if 'consul_host' in args_dict else None),
        'consul_token': (args_dict['consul_token'] if 'consul_token' in args_dict else None),
        'consul_verify_ssl': (args_dict['consul_verify_ssl'] if 'consul_verify_ssl' in args_dict else None)
    }

    log.info('Loading global config.json from %s' % global_config_path)
    log.info('Loading user config.json from %s' % user_config_path)

    if os.path.exists(user_config_path):
        user_config = json.load(open(user_config_path, 'r'))

    if os.path.exists(global_config_path):
        global_config = json.load(open(global_config_path, 'r'))

    if args.edit:

        # Access check, we must be running as root to execute this
        if args.editGlobal and os.getuid() != 0:
            print 'Must be run as root to write global config'
            exit(1)

        new_config = {
            'consul_host': read_ip(),
            'consul_port': read_port(8500),
            'consul_token': raw_input('Token: '),
            'consul_verify_ssl': read_boolean()
        }

        if args.editGlobal:
            if not os.path.exists(global_base):
                os.makedirs(global_base)

            json.dump(new_config, open(global_config_path, 'w'), indent=4)
        else:
            if not os.path.exists(user_base):
                os.makedirs(user_base)

            json.dump(new_config, open(user_config_path, 'w'), indent=4)

    else:
        configs = {
            'Default': consul_utils.default_configuration,
            'Global': global_config,
            'User': user_config,
            'Args': args_config
        }
        config = {}

        print '\n%s | %s | %s | %s | %s' % \
              ('Scope'.rjust(8, ' '),
               'consul_host'.ljust(30, ' '),
               'consul_port'.ljust(11, ' '),
               'consul_token'.ljust(40, ' '),
               'consul_verify_ssl')
        print '%s-+-%s-+-%s-+-%s-+-%s' % \
              (''.ljust(8, '-'),
               ''.ljust(30, '-'),
               ''.ljust(11, '-'),
               ''.ljust(40, '-'),
               ''.ljust(17, '-'))

        for key in ['Default', 'Global', 'User', 'Args']:
            value = consul_utils.clean_dict(configs[key])
            print_config(key, value)

            config = jsonmerge.merge(config, consul_utils.clean_dict(value))
            log.info('Merging config')
            consul_utils.dump_dict(config)

        print '%s-+-%s-+-%s-+-%s-+-%s' % \
              (''.ljust(8, '-'),
               ''.ljust(30, '-'),
               ''.ljust(11, '-'),
               ''.ljust(40, '-'),
               ''.ljust(17, '-'))
        print_config('Merged', config)
        print


def print_config(label, config):
    print '%s | %s | %s | %s | %s' % (label.ljust(8, ' '),
                                      (config['consul_host'] if 'consul_host' in config else '').ljust(30, ' '),
                                      (str(config['consul_port']) if 'consul_port' in config else '').ljust(11, ' '),
                                      (config['consul_token'] if 'consul_token' in config else '').ljust(40, ' '),
                                      (config['consul_verify_ssl'] if 'consul_verify_ssl' in config else ''))


def read_ip():
    while True:
        try:
            return IP(raw_input('Consul host [IP]: ')).strNormal()
        except ValueError:
            print 'Error: Invalid IP, must be a valid IPv4 or IPv6 address'


def read_port(default_value):
    while True:
        try:
            i = raw_input('Consul port: ')

            if i is None:
                return default_value

            port = int(i)

            if port < 1 or port > 65535:
                raise ValueError()

            return port
        except ValueError:
            print 'Error: Invalid port, must be a valid int [1, 65,535]'


def read_boolean():
    return raw_input('Verify SSL [y/N]: ').lower() in ['y', 'yes']
