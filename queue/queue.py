import sched
import time

s = sched.scheduler(time.time, time.sleep)

def low_freq():
    print('This is the low')
    s.enter(5, 2, low_freq, argument=())

def high_freq():
    print('This is the high')
    s.enter(2, 1, high_freq, argument=())

def main():
    s.enter(2, 1, high_freq, argument=())
    s.enter(5, 2, low_freq, argument=())
    s.run()
    print('Exiting')

main()
