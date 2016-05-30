import logging
import math
import coloredlogs


def setup_logging(args):

    levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

    coloredlogs.install(level=levels[min(len(levels) - 1, args.verbose)],
                        datefmt='%H:%M:%S',
                        level_styles={
                            'debug': {'color': 'green'},
                            'info': {'color': 'cyan'},
                            'warning': {'color': 'yellow', 'bold': True},
                            'error': {'color': 'red'},
                            'critical': {'color': 'red', 'bold': True}
                        },
                        field_styles=coloredlogs.parse_encoded_styles(''))


def setup_common_args(parser):

    parser.add_argument('--verbose', '-v',
                        default=0,
                        action='count',
                        required=False,
                        help='Be verbose',
                        dest='verbose')
    parser.add_argument('--consul-host', '-ch',
                        required=False,
                        help='The Consul host',
                        dest='consul_host')
    parser.add_argument('--consul-port', '-cp',
                        type=int,
                        required=False,
                        help='The Consul port',
                        dest='consul_port')
    parser.add_argument('--consul-token', '-ct',
                        default=None,
                        required=False,
                        help='The Consul authentication token',
                        dest='consul_token')
    parser.add_argument('--consul-data-center', '-cd',
                        default=None,
                        required=False,
                        help='The Consul data center',
                        dest='consul_dc')
    parser.add_argument('--consul-verify-ssl', '-cv',
                        default=False,
                        action='store_true',
                        required=False,
                        help='Verify SSL of Consul host',
                        dest='consul_verify_ssl')

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
