'''
    system_hotkey.util

    general utilites..
'''
import _thread as thread
from queue import Queue
from functools import wraps


def unique_int(values):
    '''
    returns the first lowest integer
    that is not in the sequence passed in

    if a list looks like 3,6
    of the first call will return 1, and then 2
    and then 4 etc
    '''
    last = 0
    for num in values:
        if last not in values:
            break
        else:
            last += 1
    return last


class CallSerializer():
    def __init__(self):
        self.queue = Queue()
        thread.start_new_thread(self.call_functions, (),)

    def call_functions(self):
        while 1:
            func, args, kwargs = self.queue.get(block=True)
            func(*args, **kwargs)

    def serialize_call(self, function):
        '''
        a call to a function decorated will not have
        overlapping calls, i.e thread safe
        '''
        @wraps(function)
        def decorator(*args, **kwargs):
            self.queue.put((function, args, kwargs))
        return decorator
