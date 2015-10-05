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

class ProcessQueue(object):
    """
    abstract class for process queue
    """
    def __init__(self):
        self.queueType = "abstract"

    def printType(self):
        print self.queueType


class FCFSQueue(ProcessQueue):
    def __init__(self):
        self.queueType = "FCFS"
        self.process_queue = deque()
    
    def appendProcess(self, burst_time, p):
        self.process_queue.append((burst_time, p))

    def nextProcess(self):
        burst_time, p = self.process_queue.popleft()
        return burst_time, p

    def isEmpty(self):
        if self.process_queue:
            return False 
        return True 
 
    def printQueue(self):
        for ele in self.process_queue:    #ele[0] is the burst time
            sys.stdout.write(" %d" % ele[1].ID)

class SRTQueue(ProcessQueue): 
    def __init__(self):
        self.queueType = "SRT"
        self.process_queue = Q.PriorityQueue()
    
    def printType(self):
        print self.queueType

    def appendProcess(self, burst_time, p):
        self.process_queue.put((burst_time, p))

    def preempt2queue(self, kickoffProcess_burst_time, kickoffProcess):
        self.process_queue.put((kickoffProcess_burst_time, kickoffProcess))

    def nextProcess(self):
        burst_time, p = self.process_queue.get()
        return burst_time, p

    def isEmpty(self):
        return self.process_queue.qsize()==0
 
    def printQueue(self):
        if self.isEmpty(): return
        #have to pop all elements and put them back v_v
        tmp = []
        while not self.process_queue.empty():
            burst_time, p = self.process_queue.get()
            sys.stdout.write(" %d" % p.ID)
            tmp.append((burst_time, p))
        for ele in tmp:
            self.process_queue.put(ele)

class PWAQueue(ProcessQueue): 
    def __init__(self):
        self.queueType = "PWA"
	self.process_queue = [] 

    def printType(self):
        print self.queueType

    def appendProcess(self, burst_time, p):
        self.process_queue.append((burst_time, p)) 

    def deleteProcess(self, p_val):
         for ele in self.process_queue:
             p = ele[1]
             if p.ID == p_val.ID:
                 self.process_queue.remove(ele)
         
    def preempt2queue(self, kickoffProcess_burst_time, kickoffProcess):
        self.process_queue.append((kickoffProcess_burst_time, kickoffProcess))

    def nextProcess(self):
	#Level from 0 - 5, 0 is the highest
        for i in range(6):
            for ele in self.process_queue:
	        burst_time, p = ele[0], ele[1]
		if p.priority == i:
		     self.process_queue.remove(ele)
                     return burst_time, p
        return None

    def isEmpty(self):
	return len(self.process_queue)==0 
 
    def printQueue(self):
        for i in range(6):
            for ele in self.process_queue:    #ele[0] is the burst time
	        if ele[1].priority == i:
                    sys.stdout.write(" %d" % ele[1].ID)

    
