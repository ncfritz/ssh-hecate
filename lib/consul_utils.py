import os
import json
import consul
import jsonmerge
import pwd
import logging
import getpass

default_configuration = {
    'consul_host': '127.0.0.1',
    'consul_port': 8500
}


def get_conn(args):

    log = logging.getLogger(name='consul_utils')

    try:
        passwd = pwd.getpwnam(getpass.getuser())
    except KeyError:
        print('User %s does not exist locally' % args.user_name)
        exit(1)

    user_home = passwd[5]
    user_config = os.path.join(user_home, '.hecate/config.json')
    global_config = '/usr/local/hecate/etc/config.json'

    log.info('Loading global config.json from %s' % global_config)
    log.info('Loading user config.json from %s' % user_config)

    configuration = default_configuration

    if os.path.exists(global_config):
        configuration = jsonmerge.merge(configuration, json.load(open(global_config, 'r')))

        if log.isEnabledFor(logging.DEBUG):
            log.info('Merging global config')
            dump_dict(configuration)
    else:
        log.warn('No global config found at %s' % global_config)

    if os.path.exists(user_config):
        configuration = jsonmerge.merge(configuration, json.load(open(user_config, 'r')))

        if log.isEnabledFor(logging.DEBUG):
            log.info('Merging user config')
            dump_dict(configuration)
    else:
        log.warn('No user config found at %s' % user_config)

    configuration = jsonmerge.merge(configuration, clean_dict(vars(args)))

    if log.isEnabledFor(logging.DEBUG):
        log.info('Merging command line arguments')
        dump_dict(configuration)

    return consul.Consul(host=configuration['consul_host'],
                         port=configuration['consul_port'],
                         token=(configuration['consul_token'] if 'conul_token' in configuration else None),
                         scheme='http',
                         consistency='default',
                         dc=(configuration['consul_dc'] if 'consul_dc' in configuration else None),
                         verify=configuration['consul_verify_ssl'])


def dump_dict(d):

    log = logging.getLogger(name='consul_utils')

    for (k, v) in d.iteritems():
        log.debug('config[%s] = %s' % (k, v))


def clean_dict(d):
    if not isinstance(d, dict):
        return d

    return dict((k, clean_dict(v)) for k, v in d.iteritems() if v is not None)
