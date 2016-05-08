import logging
import os
import random
import threading
import time

from hecate_sync import exec_sync


def exec_service(args):

    # Access check, we must be running as root to execute this
    if os.getuid() != 0:
        print 'Must be run as root to sync all users'
        exit(1)

    try:
        # Force the service to synchronize for all users
        args.all = True

        # Start the background thread
        service_thread = threading.Thread(target=run_background, args=[args])
        service_thread.daemon = True
        service_thread.start()

        # Simple spin to prevent us from dropping out of the try/except.  This allows
        # us to properly intercept and handle a ^C
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print 'Caught keyboard interrupt... exiting'

def run_background(args):

    log = logging.getLogger(name='hecate_get')

    # Calculate the time the sleep, this will be jittered so we don't accidentally spam the server
    # in the event that a cluster of machines comes up at the same time
    jitter = random.randint(0, args.jitter)
    sleep_time = args.frequency + jitter

    log.debug('Starting synchronization run - Frequency: %s, Jitter: %s' % (args.frequency, jitter))

    # Effectively sleep until we need to wake up and sync
    threading.Timer(sleep_time, run_background, [args]).start()

    log.info('Running exec_sync')

    # Perform the sync
    exec_sync(args)
