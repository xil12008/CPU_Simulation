import heapq
from collections import deque
import pdb
import sys
import Queue as Q
import logging
logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL)

"""
NOTE: THIS PROGRAM IS DEVELOPED UNDER PYTHON 2.7
      In python 3.0, the notation for queue is different than ver. < 3.0
"""

class ProcessQueue(object):
    def __init__(self, queueType = "FCFS"):
        if queueType=="FCFS": 
            self.process_queue = deque()
        elif queueType=="SRT":
            self.process_queue = Q.PriorityQueue()
        self.queueType = queueType
    
    def printType(self):
        print self.queueType

    def appendProcess(self, burst_time, p):
        if self.queueType=="FCFS":
           self.process_queue.append((burst_time, p))
        elif self.queueType=="SRT":
           self.process_queue.put((burst_time, p))

    def preempt2queue(self, kickoffProcess_burst_time, kickoffProcess):
        if self.queueType=="SRT":
            self.process_queue.put((kickoffProcess_burst_time, kickoffProcess))
        else:
            logging.error("Preempt is only for SRT!!")    

    def nextProcess(self):
        if self.queueType=="FCFS":
            burst_time, p = self.process_queue.popleft()
            return burst_time, p
        elif self.queueType=="SRT":
            burst_time, p = self.process_queue.get()
            return burst_time, p

    def isEmpty(self):
        if self.queueType=="FCFS":
            if self.process_queue:
                return False 
            return True 
        elif self.queueType=="SRT":
            return self.process_queue.qsize()==0
 
    def printQueue(self):
        if self.queueType=="FCFS":
            for ele in self.process_queue:    #ele[0] is the burst time
                sys.stdout.write(" %d" % ele[1].ID)
        elif self.queueType=="SRT":
            if self.isEmpty(): return
            #have to pop all elements and put them back v_v
            tmp = []
            while not self.process_queue.empty():
                burst_time, p = self.process_queue.get()
                sys.stdout.write(" %d" % p.ID)
                tmp.append((burst_time, p))
            for ele in tmp:
                self.process_queue.put(ele)

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

class ProcessInfo():
    ID = None
    burst_time = None 
    num_burst = None
    io_time = None 
   
    def __init__(self, ID_val, burst_time_val, num_burst_val, io_time_val):
       self.ID = ID_val 
       self.burst_time = burst_time_val 
       self.num_burst = num_burst_val 
       self.io_time = io_time_val 
       self.lastTimeInCPU = None 
       self.remain_burst_time = burst_time_val

    def resetRemainBurstTime(self):
        self.remain_burst_time = self.burst_time

    def setInCPUTime(self, time):
        self.lastTimeInCPU = time 
    
    def setOutCPUTime(self, time):
        if(self.lastTimeInCPU):
            self.remain_burst_time -= (time - self.lastTimeInCPU)   
            return time - self.lastTimeInCPU 
        else:
            raise Exception("Process not ever in CPU") 

    def printProcess(self):
        print self.ID, self.burst_time, self.num_burst, self.io_time
 
class CPU():
    t_cs = 13 # in ms
    p_list = []
    process_queue = ProcessQueue() 
 
    def __init__(self, queuetype, t_cs_val = 13):
        self.t_cs = t_cs_val 
        self.process_queue = ProcessQueue(queuetype) 
        self.queueType = queuetype
        self.CPUIdle = True
        self.n = 0
        self.active_n = 0
        self.maxID = 1 
        self.processInCPU = None #Note: processInCPU is the process in use of CPU, NOT in content switch
 
        self.burstTimeSum = 0
        self.turnaroundTimeSum = 0
        self.contentSwitchSum = 0
 
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
            self.process_queue.appendProcess(p.burst_time, p)
        #time 0ms: Simulator started [Q 1 2 4 3]
        print "time 0ms: Simulator started for %s [Q" % self.queueType,
        sys.stdout.write('') 
        self.printQueue()
        print "]"
        next_burst_time, next_process = self.process_queue.nextProcess()
        s.schedule(self.t_cs, self.eContentSwitch, next_process, next_burst_time, s)  
        s.run()    
      
    #event occurs when it's done 
    #def event(id, simulator, scheduled, rescheduled=None):
    def eContentSwitch(self, process, burst_time, simulator):
        #time 13ms: P1 started using the CPU 
        print "time %dms:" % simulator.time,"P%d"% process.ID, "started using the CPU [Q",
        sys.stdout.write('')
        self.printQueue()
        print "]"
        logging.info("***Test: the remaining time for P%d: %d" % (process.ID, process.remain_burst_time))
        self.CPUIdle = False
        self.processInCPU = process   # A process AFTER content switching is really treated as a process in the CPU
        process.setInCPUTime(simulator.time)
        simulator.schedule(simulator.time + burst_time, self.eCPUBurst, process, simulator) 
        self.contentSwitchSum += 1

    def eCPUBurst(self, process, simulator):
        self.burstTimeSum += process.setOutCPUTime(simulator.time)

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
                print "time %dms: Simulator for %s ended" %( simulator.time, self.queueType)
        self.processInCPU = None #Note: process in cpu is in use of CPU, NOT in content switch
        if(not self.process_queue.isEmpty()):
            next_burst_time, next_process = self.process_queue.nextProcess() 
            simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, next_burst_time, simulator) 
            self.CPUIdle = False
        else: #empty process queue
            self.CPUIdle = True
    
    def eIOBurst(self, process, simulator):
        #if simulator.time == 1625:
        #     pdb.set_trace()

        if process.num_burst == 0:
            return

        process.resetRemainBurstTime()

        if self.processInCPU and self.queueType=="SRT" and self.processInCPU.remain_burst_time - (simulator.time - self.processInCPU.lastTimeInCPU) > process.burst_time : 
             print "time %dms:"% simulator.time,"P%d"% process.ID, "completed I/O [Q",
             sys.stdout.write('')
             self.printQueue()
             print "]"

        #PREEMPT CASE

             print "time %dms:"% simulator.time,"P%d"% self.processInCPU.ID, "preempted by P%d [Q" % process.ID ,
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
             self.process_queue.preempt2queue(self.processInCPU.remain_burst_time, self.processInCPU) 
             self.processInCPU = None

#@TODO impo r question! how about a process in content switching being preempted???

             #process skip the queue and use CPU immediately
             next_burst_time, next_process = process.burst_time, process
             simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, next_burst_time, simulator) 
             self.CPUIdle = False
        else:
        # NORMAL CASE
             self.process_queue.appendProcess(process.burst_time, process)
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
       
if(__name__=="__main__"):
    infile = r"./processes.txt"
    if len(sys.argv)>1 and str(sys.argv[1]):
        infile = str(sys.argv[1]) 
    with open(infile) as f:
        f = f.readlines()

    cpu = CPU(queuetype=sys.argv[2])

    for line in f:
        if(line.strip() and line[0]=='#'):
            continue 
        segments = line.split('|')
        if(len(segments)!=4):
            #print "Wrong Input Line"
            continue
        else:
            cpu.addProcess(ProcessInfo(int(segments[0]),int(segments[1]),int(segments[2]),int(segments[3]))) 

    cpu.run()
    print cpu.burstTimeSum, cpu.turnaroundTimeSum, cpu.contentSwitchSum 



    
