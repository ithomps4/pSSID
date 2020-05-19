import psjson as psjson
import sys
import json
import syslog

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

# Send test to api to run
# @TODO run in loop using queue
sys.argv = ['api.py', task]
execfile('api.py')
