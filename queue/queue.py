import sched
import time
import iso8601 as iso
import datetime

s = sched.scheduler(time.time, time.sleep)

def low_freq():
    print('This is the low')
    s.enter(5, 2, low_freq, argument=())

def high_freq():
    print('This is the high')
    s.enter(2, 1, high_freq, argument=())

def main():
    sec_10 = (iso.iso8601_as_timedelta('PT10S')).total_seconds()
    sec_5 = (iso.iso8601_as_timedelta('PT5S')).total_seconds()
    s.enter(sec_5, 1, high_freq, argument=())
    s.enter(sec_10, 2, low_freq, argument=())
    s.run()
    print('Exiting')

main()
