import os
import json
import consul
import jsonmerge
import pwd
import logging
import getpass

def getConn(args):

    log = logging.getLogger(name='consul_utils')

    configuration = {
        'consul_host': '127.0.0.1',
        'consul_port': 8500
    }

    try:
        passwd = pwd.getpwnam(getpass.getuser())
    except KeyError:
        print('User %s does not exist locally' % args.user_name)
        exit(1)

    user_home = passwd[5]
    user_config = os.path.join(user_home, '.hecate/config.json')
    global_config = '/etc/hecate/config.json'

    log.info('Loading global config.json from %s' % global_config)
    log.info('Loading user config.json from %s' % user_config)

    if os.path.exists(global_config):
        configuration = jsonmerge.merge(configuration, json.load(open(global_config, 'r')))

        if log.isEnabledFor(logging.DEBUG):
            log.info('Merging global config')
            dumpDict(configuration)
    else:
        log.warn('No global config found at %s' % global_config)

    if os.path.exists(user_config):
        configuration = jsonmerge.merge(configuration, json.load(open(user_config, 'r')))

        if log.isEnabledFor(logging.DEBUG):
            log.info('Merging user config')
            dumpDict(configuration)
    else:
        log.warn('No user config found at %s' % user_config)

    configuration = jsonmerge.merge(configuration, cleanDict(vars(args)))

    if log.isEnabledFor(logging.DEBUG):
        log.info('Merging command line arguments')
        dumpDict(configuration)

    return consul.Consul(host = configuration['consul_host'],
                         port = configuration['consul_port'],
                         token = (configuration['consul_token'] if 'conul_token' in configuration else None),
                         scheme = 'http',
                         consistency = 'default',
                         dc = None,
                         verify = configuration['consul_verify_ssl'])

def dumpDict(d):

    log = logging.getLogger(name='consul_utils')

    for (k, v) in d.iteritems():
        log.debug('config[%s] = %s' % (k, v))

def cleanDict(d):
     if not isinstance(d, dict):
         return d
     return dict((k, cleanDict(v)) for k, v in d.iteritems() if v is not None)