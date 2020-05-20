import psjson as psjson
import sys
import json
import syslog
import time
import daemon
import optparse
import threading

# Daemon-related options

opt_parser.add_option("--daemon", help="Daemonize", action="store_true", dest="daemon", default=False)

opt_parser.add_option("--pid-file", help="Location of PID file", action="store", type="string", dest="pidfile", default=None)

(options, args) = opt_parser.parse_args()

"""
@ Daemon function to run tests
"""
def apid(queue):
    while True:
        for test in queue:
            sys.argv = ['api.py', test]
            execfile('api.py')
        print('Sleeping')
        time.sleep(10)

def main():
    # Requires a json file to parse
    if len(sys.argv) != 2:
        raise ValueError('Provide json file to parse')

    # Open json file and load using psjson
    file = open(sys.argv[1])
    data = psjson.json_load(file)


    # Dicey data structures to hold json
    # @TODO clean up structures
    archives = data['archives']
    tests = data['tests']
    schedules = data['schedules']
    addresses = data['addresses']
    tasks = data['tasks']
    test_dict = {}
    to_test = []
    queue = []

    # Create a dict of tests and test info
    for item in tests:
        test_dict.update({str(item) : tests[item]})

    # Create list of tests to run
    # @TODO create queue
    for entry in tasks:
        to_test.append(test_dict[tasks[entry]['test']])

    # Appened extra json to allow test to be run
    for x in to_test:
        task = {'schema':1, 'schedule': {}}
        task['test'] = x
        queue.append(task)

    sys.argv = ['api.py', task]
    execfile('api.py')

    apid(queue)

    api_worker = threading.Thread(
        target=lambda: apid(queue))
    api_worker.setDaemon(True)
    api_worker.start()

    print('Exiting...')

if options.daemon:
    pidfile = pscheduler.PidFile(options.pidfile)
    with daemon.DaemonContext(pidfile=pidfile):
        pscheduler.safe_run(lambda: main())
else:
    pscheduler.safe_run(lambda: main())
