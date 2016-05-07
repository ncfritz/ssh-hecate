import logging
import coloredlogs

def setupLogging(args):
    levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

    coloredlogs.install(level=levels[min(len(levels) - 1, args.verbose)],
                        datefmt='%H:%M:%S',
                        level_styles={ 'debug': { 'color': 'green' },
                                       'info': { 'color': 'cyan' },
                                       'warning': { 'color': 'yellow', 'bold': True },
                                       'error': { 'color': 'red' },
                                       'critical': { 'color': 'red', 'bold': True }
                                     },
                        field_styles=coloredlogs.parse_encoded_styles(''))

def setupCommonArgs(parser):
    parser.add_argument('--verbose', '-v',
                        default = 0,
                        action = 'count',
                        required = False,
                        help = 'Be verbose',
                        dest = 'verbose')
    parser.add_argument('--consul-host', '-ch',
                        required = False,
                        help = 'The Consul host',
                        dest = 'consul_host')
    parser.add_argument('--consul-port', '-cp',
                        type = int,
                        required = False,
                        help = 'The Consul port',
                        dest = 'consul_port')
    parser.add_argument('--consul-token', '-ct',
                        default = None,
                        required = False,
                        help = 'The Consul authentication token',
                        dest = 'consul_token')
    parser.add_argument('--consul-data-center', '-cd',
                        default = None,
                        required = False,
                        help = 'The Consul data center',
                        dest = 'consul_data_center')
    parser.add_argument('--consul-verify-ssl', '-cv',
                        default = False,
                        action = 'store_true',
                        required = False,
                        help = 'Verify SSL of Consul host',
                        dest = 'consul_verify_ssl')