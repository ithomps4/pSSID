import sched
import time
import iso8601 as iso
import datetime

s = sched.scheduler(time.time, time.sleep)

def iso_to_s(iso_time):
    return iso.iso8601_as_timedelta(iso_time).total_seconds()

def low_freq():
    print('This is the low')
    s.enter(5, 2, low_freq, argument=())

def high_freq():
    print('This is the high')
    s.enter(2, 1, high_freq, argument=())

def main():
    sec_10 = iso_to_s('PT10S')
    sec_5 = iso_to_s('PT5S')
    s.enter(sec_5, 1, high_freq, argument=())
    s.enter(sec_10, 2, low_freq, argument=())
    s.run()
    print('Exiting')

main()
