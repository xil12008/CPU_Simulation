import heapq
from collections import deque
import pdb
import sys
import Queue as Q
import logging

"""
NOTE: THIS PROGRAM IS DEVELOPED UNDER PYTHON 2.7
      In python 3.0, the notation for queue is different than ver. < 3.0
"""

class Simulator(object):
    
    def __init__(self, maxID):
        self.queue = []
        self.time = -1 
        self.terminated = False
        self.maxID = maxID  #tie-breaker: if two processes being added to queue at the same time, the smaller ID is inserted first 

    def schedule(self, time, callback, *args):
        """
        Schedules an event to be executed at a later point in time.
        ``callback`` is a callable which executed the event-specific behavior;
        the optional ``args`` and ``kwargs`` arguments will be passed to the
        event callback at invocation time.

        Returns an object which can be used to reschedule the event.
        """
        assert time > self.time
        #tie-breaker: if two processes being added to queue at the same time, the smaller ID is inserted first 
        event = [time * self.maxID  + (args[0].ID - 1), True, callback, args]
        heapq.heappush(self.queue, event)
        event = [time, True, callback, args]
        return event
   
    def cancel(self, schedule_time, processID):
        #pdb.set_trace()
        for index, ele in enumerate(self.queue):
            #ele = [time, True, callback, args] 
            #args= [process, some other parameters]
            if ele[0] == schedule_time * self.maxID + (processID - 1) and ele[3][0].ID == processID:
                logging.info("Find P%d in queue" % processID)
                #replace canceled event with the last element, remove the last element then re-heapify the heap
                self.queue[index] = self.queue[-1]
                self.queue.pop()
                heapq.heapify(self.queue)
 
    def halt(self):
        self.terminated = True

    def reschedule(self, event, time):
        """
        Reschedules ``event`` to take place at a different point in time
        """
        assert time > self.time
        rescheduled = list(event)
        event[1] = False
        rescheduled[0] = time
        heapq.heappush(self.queue, rescheduled)
        return rescheduled


    def run(self):
        """
        Simple simulation function to test the behavior
        """
        while self.queue:
            time, valid, callback, args = heapq.heappop(self.queue)
            time = (int)(time / self.maxID)
            #tie-breaker: if two processes being added to queue at the same time, the smaller ID is inserted first 

            if not valid:
                continue
            self.time = time
            callback(*args)
            if self.terminated:
                return

