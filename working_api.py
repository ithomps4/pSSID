#!/usr/bin/python -u
"""

This program goes through all of the steps needed to do a single
run of a pScheduler task through its REST API.

To install non-standard modules used by this script (available from
the standard CentOS repository):

    yum -y install python-dateutil python-requests

"""

import datetime
import dateutil.parser
import json
import pycurl
import StringIO
import time
import urllib

from dateutil.tz import tzlocal


# -----------------------------------------------------------------------------

#
# Configurables
#


# Logging configuration
pSSID_logger = logging.getLogger('SysLogger')
pSSID_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log', facility = 'local6')
pSSID_logger.addHandler(handler)


LEAD = "localhost"


# -----------------------------------------------------------------------------

#
# Utilities
#

def fail(message):
    """Complain about a problem and exit."""
    print message
    exit(1)


def json_load(source):
    """Load a blob of JSON into Python objects"""

    try:
        json_in = json.loads(str(source))
    except ValueError as ex:
        raise ValueError("Invalid JSON: " + str(ex))

    return json_in


def json_dump(obj):
    """Convert a blob of Python objects to a string"""
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))



# -----------------------------------------------------------------------------

# URL Handling functions.  These are lifted directly from the
# pScheduler library.


class URLException(Exception):
    pass


class PycURLRunner(object):

    def __init__(self, url, params, bind, timeout, allow_redirects, headers, verify_keys):
        """Constructor"""

        self.curl = pycurl.Curl()

        full_url = url if params is None else "%s?%s" % (url, urllib.urlencode(params))
        self.curl.setopt(pycurl.URL, str(full_url))

        if bind is not None:
            self.curl.setopt(pycurl.INTERFACE, bind)

        self.curl.setopt(pycurl.FOLLOWLOCATION, allow_redirects)

        if headers is not None:
            self.curl.setopt(pycurl.HTTPHEADER, [
                "%s: %s" % (str(key), str(value))
                for (key, value) in headers.items()
            ])

        if timeout is not None:
            self.curl.setopt(pycurl.TIMEOUT_MS, int(timeout * 1000.0))

        self.curl.setopt(pycurl.SSL_VERIFYHOST, verify_keys)
        self.curl.setopt(pycurl.SSL_VERIFYPEER, verify_keys)

        self.buf = StringIO.StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.buf.write)


    def __call__(self, json, throw):
        """Fetch the URL"""
        try:
            self.curl.perform()
            status = self.curl.getinfo(pycurl.HTTP_CODE)
            text = self.buf.getvalue()
        except pycurl.error as ex:
            (code, message) = ex
            status = 400
            text = message
        finally:
            self.curl.close()
            self.buf.close()

        #If status is outside the HTTP 2XX success  range
        if status < 200 or status > 299:
            if throw:
                raise URLException(text.strip())
            else:
                return (status, text)

        if json:
            return (status, json_load(text))
        else:
            return (status, text)



def url_get( url,          # GET URL
             params=None,  # GET parameters
             bind=None,    # Bind request to specified address
             json=True,    # Interpret result as JSON
             throw=True,   # Throw if status isn't 200
             timeout=None, # Seconds before giving up
             allow_redirects=True, # Allows URL to be redirected
             headers=None, # Hash of HTTP headers
             verify_keys=False  # Verify SSL keys
             ):
    """
    Fetch a URL using GET with parameters, returning whatever came back.
    """

    curl = PycURLRunner(url, params, bind, timeout, allow_redirects, headers, verify_keys)
    return curl(json, throw)



def __content_type_data(content_type, headers, data):

    """Figure out the Content-Type based on an incoming type and data and
    return that plus data in a type that PycURL can handle."""

    assert(content_type is None or isinstance(content_type, basestring))
    assert(isinstance(headers, dict))

    if content_type is None or "Content-Type" not in headers:

        # Dictionaries are JSON
        if isinstance(data, dict):
            content_type = "application/json"
            data = json_dump(data)

        # Anything else is plain text.
        else:
            content_type = "text/plain"
            data = str(data)

    return content_type, data




def url_post( url,          # GET URL
              params={},    # GET parameters
              data=None,    # Data to post
              content_type=None,  # Content type
              bind=None,    # Bind request to specified address
              json=True,    # Interpret result as JSON
              throw=True,   # Throw if status isn't 200
              timeout=None, # Seconds before giving up
              allow_redirects=True, #Allows URL to be redirected
              headers={},   # Hash of HTTP headers
              verify_keys=False  # Verify SSL keys
              ):
    """
    Post to a URL, returning whatever came back.
    """

    content_type, data = __content_type_data(content_type, headers, data)
    headers["Content-Type"] = content_type

    curl = PycURLRunner(url, params, bind, timeout, allow_redirects, headers, verify_keys)

    curl.curl.setopt(pycurl.POSTFIELDS, data)

    return curl(json, throw)



# -----------------------------------------------------------------------------

#
# MAIN PROGRAM BEGINS HERE
#

# -----------------------------------------------------------------------------

#
# Post the task to the server's "tasks" endpoint
#

def run_task(json_blob):

    tasks_url = "https://%s/pscheduler/tasks" % (LEAD)

    try:
        status, task_url = url_post(tasks_url, data=json_dump(json_blob))
    except Exception as ex:
        fail("Unable to post task: %s" % (str(ex)))


    # -----------------------------------------------------------------------------

    #
    # Fetch the posted task with extra details.
    #

    try:
        status, task_data = url_get(task_url, params={"detail": True})
        if status != 200:
            raise Exception(task_data)
    except Exception as ex:
        fail("Failed to post task: %s" % (str(ex)))


    try:
        first_run_url = task_data["detail"]["first-run-href"]
    except KeyError:
        fail("Server returned incomplete data.")


    # -----------------------------------------------------------------------------

    #
    # Get first run and make sure we have what we need to function.  The
    # server will wait until the first run has been scheduled before
    # returning a result.
    #

    status, run_data = url_get(first_run_url)

    if status == 404:
        fail("The server never scheduled a run for the task.")
    if status != 200:
        fail("Error %d: %s" % (status, run_data))

    for key in ["start-time", "end-time", "result-href"]:
        if key not in run_data:
            fail("Server did not return %s with run data" % (key))



    # -----------------------------------------------------------------------------

    #
    # Wait for the end time to pass
    #

    try:
        # The end time comes back as ISO 8601.  Parse it.
        end_time = dateutil.parser.parse(run_data["end-time"])
    except ValueError as ex:
        fail("Server did not return a valid end time for the task: %s" % (str(ex)))

    now = datetime.datetime.now(tzlocal())
    sleep_time = end_time - now if end_time > now else datetime.timedelta()
    sleep_seconds = (sleep_time.days * 86400) \
                    + (sleep_time.seconds) \
                    + (sleep_time.microseconds / (10.0**6))

    time.sleep(sleep_seconds)


    # -----------------------------------------------------------------------------

    #
    # Wait for the result to be produced and fetch it.
    #

    status, result_data = url_get(run_data["result-href"],
                                  params={"wait-merged": True})
    if status != 200:
        fail("Did not get a result: %s" % (result_data))

    # Log result to pSSID.log
    pSSID_logger.info(run_data["result-href"])



    # -----------------------------------------------------------------------------

    #
    # If the run succeeded, fetch a plain-text version of the result.
    #
    # This fetches the same endpoint as above but doesn't wait for the
    # merged (finished) result and asks for it in text format.  Supported
    # formats are application/json, text/plain and text/html.  Note that
    # not all tests generate proper text/html.
    #

    if not result_data["succeeded"]:
        fail("Test failed to run properly.")


    status, result_text = url_get(run_data["result-href"],
                                  params={"format": "text/plain"},
                                  json=False)

    if status != 200:
        fail("Did not get a result: %s" % (result_text))
