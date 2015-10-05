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

class ProcessInfo():

    ID = None
    burst_time = None 
    num_burst = None
    io_time = None 
    priority = None   
 
    def __init__(self, ID_val, burst_time_val, num_burst_val, io_time_val, priority_val):
       self.ID = ID_val 
       self.burst_time = burst_time_val 
       self.num_burst = num_burst_val 
       self.io_time = io_time_val 
       self.lastTimeInCPU = None 
       self.lastTimeInQueue = None 
       self.remain_burst_time = burst_time_val
       self.priority = priority_val

    def resetRemainBurstTime(self):
        self.remain_burst_time = self.burst_time

    def setInCPUTime(self, time):
        self.lastTimeInCPU = time 
    
    def setOutCPUTime(self, time):
        if(self.lastTimeInCPU != None):
            self.remain_burst_time -= (time - self.lastTimeInCPU)   
            return time - self.lastTimeInCPU 
        else:
            raise Exception("Process not ever in CPU")  

    def setInQueueTime(self, time):
        self.lastTimeInQueue = time

    def setOutQueueTime(self, time):
        if self.lastTimeInQueue != None:
	    return time - self.lastTimeInQueue
        else:
            raise Exception("lastTimeInQueue is None")  

    def printProcess(self):
        print self.ID, self.burst_time, self.num_burst, self.io_time

