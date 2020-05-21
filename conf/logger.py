import logging
import logging.handlers

test_logger = logging.getLogger('SysLogger')
test_logger.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address = '/dev/log', facility = 'local6')


test_logger.addHandler(handler)

test_logger.debug('Test log...')
