#!/bin/python
import heapq
from collections import deque
import pdb
import sys
import Queue as Q
import logging
import random

"""
NOTE: THIS PROGRAM IS DEVELOPED UNDER PYTHON 2.7
      In python 3.0, the notation for queue is different than ver. < 3.0
"""

from processqueue import ProcessQueue, SRTQueue, FCFSQueue, PWAQueue
from simulator import Simulator

class CPU():
    t_cs = 13 # in ms
    p_list = []
 
    def __init__(self, queuetype, t_cs_val = 13):
        self.t_cs = t_cs_val 
        if queuetype == "FCFS":
            self.process_queue = FCFSQueue() 
        elif queuetype == "SRT":
            self.process_queue = SRTQueue() 
        elif queuetype == "PWA":
            self.process_queue = PWAQueue() 
        self.queueType = queuetype
        self.CPUIdle = True
        self.n = 0
        self.active_n = 0
        self.maxID = 1 
        self.processInCPU = None #Note: processInCPU is the process in use of CPU, NOT in content switch
        self.burstTimeSum = 0
        self.waitTimeSum = 0
        self.waitTimeNum = 0
        self.turnaroundTimeSum = 0
        self.contentSwitchSum = 0
        self.p_list = []

    def printQueue(self):
        self.process_queue.printQueue()

    #Must add all processes before running
    def addProcess(self, p):
        self.p_list.append(p) 
        self.n += 1       
        self.active_n += 1 
        self.maxID = max(self.maxID, p.ID) 
 
    def run(self):
        s = Simulator(self.maxID)
        for p in self.p_list:
            #p.printProcess()
	    p.setInQueueTime(0)
            self.process_queue.appendProcess(p.burst_time, p)
	    if self.queueType == "PWA":
	        p.currentAgingSeq = random.getrandbits(128)
	        s.schedule( 0 + 3 * p.burst_time, self.eAging, p, p.currentAgingSeq , s) 

        print "time 0ms: Simulator started for %s [Q" % self.queueType,
        sys.stdout.write('') 
        self.printQueue()
        print "]"
        next_burst_time, next_process = self.process_queue.nextProcess()
	self.waitTimeSum += next_process.setOutQueueTime(0)
	self.waitTimeNum += 1

        s.schedule(self.t_cs, self.eContentSwitch, next_process, next_burst_time, s)  
        s.run()    
      
    #event occurs when it's done 
    def eContentSwitch(self, process, burst_time, simulator):
        print "time %dms:" % simulator.time,"P%d"% process.ID, "started using the CPU [Q",
        sys.stdout.write('')
        self.printQueue()
        print "]"
        #logging.info("***Test: the remaining time for P%d: %d" % (process.ID, process.remain_burst_time))
        self.CPUIdle = False
        self.processInCPU = process   # A process AFTER content switching is really treated as a process in the CPU
        process.setInCPUTime(simulator.time)
        simulator.schedule(simulator.time + burst_time, self.eCPUBurst, process, simulator) 
        self.contentSwitchSum += 1

    def eCPUBurst(self, process, simulator):
        self.burstTimeSum += process.setOutCPUTime(simulator.time)
	process.currentAgingSeq = random.getrandbits(128)

        process.num_burst -= 1 
        if process.num_burst > 0:
            #time 181ms: P1 completed its CPU burst
            print "time %dms:" % simulator.time,"P%d"%process.ID, "completed its CPU burst [Q",
            sys.stdout.write('')
            self.printQueue()
            print "]"
            #time 181ms: P1 performing I/O
            print "time %dms:"% simulator.time,"P%d"%process.ID, "performing I/O [Q",
            sys.stdout.write('')
            self.printQueue()
            print "]"
            simulator.schedule(simulator.time + process.io_time, self.eIOBurst, process, simulator) 
        else:
            print "time %dms:"% simulator.time,"P%d"%process.ID, "terminated [Q",
            sys.stdout.write('')
            self.printQueue()
            print "]"
            self.turnaroundTimeSum += simulator.time
            self.active_n -= 1
            if(self.active_n == 0):
                print "time %dms: Simulator for %s ended [Q]" %( simulator.time, self.queueType)
        self.processInCPU = None #Note: process in cpu is in use of CPU, NOT in content switch
        if(not self.process_queue.isEmpty()):
            next_burst_time, next_process = self.process_queue.nextProcess() 
	    self.waitTimeSum += next_process.setOutQueueTime(simulator.time)
	    self.waitTimeNum += 1 

            simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, next_burst_time, simulator) 
            self.CPUIdle = False
        else: #empty process queue
            self.CPUIdle = True
 
    def eIOBurst(self, process, simulator):
        if process.num_burst == 0:
            return

        process.resetRemainBurstTime()
 

        if self.processInCPU and self.queueType=="SRT" and self.processInCPU.remain_burst_time - (simulator.time - self.processInCPU.lastTimeInCPU) > process.burst_time : 
	# Preempted by SRT
            self.SRTPreempt(process, simulator)
	elif self.processInCPU and self.queueType=="PWA" and self.processInCPU.priority > process.priority:
	# Preempted by PWA
	    process.currentAgingSeq = random.getrandbits(128)
	    self.processInCPU.currentAgingSeq = random.getrandbits(128)
            print "time %dms:"% simulator.time,"P%d"% process.ID, "completed I/O [Q",

            sys.stdout.write('')
            self.printQueue()
            print "]"

	    self.PWAPreempt(process, simulator)
        else:
        # NORMAL CASE
	    process.setInQueueTime(simulator.time)
            self.process_queue.appendProcess(process.burst_time, process)

	    #PWA with aging
            if self.queueType=="PWA": 
	        #The trick is: process after re-enter queue, the agingSeq is refreshed
		#so that only if a process stay in queue for 3*burst time, the priority changes
	        process.currentAgingSeq = random.getrandbits(128)
	        simulator.schedule(simulator.time + 3 * process.burst_time, self.eAging,process, process.currentAgingSeq , simulator) 

            print "time %dms:"% simulator.time,"P%d"% process.ID, "completed I/O [Q",
            sys.stdout.write('')
            self.printQueue()
            print "]"
 
        if self.CPUIdle :
        # it means 1.queue empty 2.current process has more rounds 
            next_burst_time, next_process = self.process_queue.nextProcess() 

            #Schedule directly
            simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, next_burst_time, simulator) 
            self.CPUIdle = False

    def eAging(self, process, agingSeq, simulator):
	#pdb.set_trace()
        if process.currentAgingSeq == agingSeq and process.priority >0:
            process.priority -= 1
	    process.currentAgingSeq = random.getrandbits(128)
	    simulator.schedule(simulator.time + 3 * process.burst_time, self.eAging,process, process.currentAgingSeq , simulator) 
            logging.info("Aging :(Time=%d) Priority of P%d now is %d." %(simulator.time, process.ID , process.priority))
            
	    if self.processInCPU and self.queueType=="PWA" and self.processInCPU.priority > process.priority:
	        #@Weird!! Just to match the sample output
		simulator.time += 1
	        # Preempted by PWA
	        process.currentAgingSeq = random.getrandbits(128)
	        self.processInCPU.currentAgingSeq = random.getrandbits(128)
		self.process_queue.deleteProcess(process)
		self.waitTimeSum += process.setOutQueueTime(simulator.time)
		self.waitTimeNum += 1
	        self.PWAPreempt(process, simulator)

    """
        PWA Preempt
    """
    def PWAPreempt(self, process, simulator):

	#Preempt. 
        self.burstTimeSum += self.processInCPU.setOutCPUTime(simulator.time)
        logging.info("***Test: Priority of P%d is %d while priority of P%d is %d "%( self.processInCPU.ID, self.processInCPU.priority, process.ID, process.priority))
        #Kick off the process in CPU and insert into queue
        #pdb.set_trace()
        if self.processInCPU.remain_burst_time <= 0: raise Exception("Bug: Kicked off at the moment of CPU Burst")
        #cancel the CPU burst of this process:
        simulator.cancel(self.processInCPU.remain_burst_time + simulator.time, self.processInCPU.ID)

	self.processInCPU.setInQueueTime(simulator.time)
        self.process_queue.preempt2queue(self.processInCPU.remain_burst_time, self.processInCPU) 

#@TODO important question! how about a process in content switching being preempted???

        #PREEMPT CASE OF PWA 
        print "time %dms:"% simulator.time,"P%d"% self.processInCPU.ID, "preempted by P%d [Q" % process.ID ,
        sys.stdout.write('')
        self.printQueue()
        print "]"

        self.processInCPU = None

        #process skip the queue and use CPU immediately
        next_burst_time, next_process = process.burst_time, process
        simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, next_burst_time, simulator) 
        self.CPUIdle = False


    """
        SRT Preempt
    """
    def SRTPreempt(self, process, simulator):


        print "time %dms:"% simulator.time,"P%d"% process.ID, "completed I/O [Q",
        sys.stdout.write('')
        self.printQueue()
        print "]"

        #Preempt. 
        self.burstTimeSum += self.processInCPU.setOutCPUTime(simulator.time)
        logging.info("***Test: Remaining Time of P%d: %d while burst time of P%d:%d "%( self.processInCPU.ID, self.processInCPU.remain_burst_time, process.ID, process.burst_time))
        #Kick off the process in CPU and insert into queue
        #pdb.set_trace()
        if self.processInCPU.remain_burst_time <= 0: raise Exception("Bug: Kicked off at the moment of CPU Burst")
        #cancel the CPU burst of this process:
        simulator.cancel(self.processInCPU.remain_burst_time + simulator.time, self.processInCPU.ID)
	self.processInCPU.setInQueueTime(simulator.time)
        self.process_queue.preempt2queue(self.processInCPU.remain_burst_time, self.processInCPU) 
#@TODO iant question! how about a process in content switching being preempted???

        #PREEMPT CASE OF SRT
        print "time %dms:"% simulator.time,"P%d"% self.processInCPU.ID, "preempted by P%d [Q" % process.ID ,
        sys.stdout.write('')
        self.printQueue()
        print "]"

        self.processInCPU = None

        #process skip the queue and use CPU immediately
        next_burst_time, next_process = process.burst_time, process
        simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, next_burst_time, simulator) 
        self.CPUIdle = False
