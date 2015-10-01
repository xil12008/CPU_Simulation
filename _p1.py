import heapq
from collections import deque
import pdb
import sys

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
   
    def printProcess(self):
        print self.ID, self.burst_time, self.num_burst, self.io_time
 
class CPU():
    t_cs = 13 # in ms
    p_list = []
    process_queue = deque()
 
    def __init__(self, t_cs_val = 13):
        self.t_cs = t_cs_val 
        self.process_queue = deque()
        self.CPUIdle = True
        self.n = 0
        self.active_n = 0
        self.maxID = 1 
 
    def printQueue(self):
        for ele in self.process_queue:
            sys.stdout.write(" %d" % ele.ID)

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
            self.process_queue.append(p)
        #time 0ms: Simulator started [Q 1 2 4 3]
        print "time 0ms: Simulator started [Q",
        sys.stdout.write('') 
        self.printQueue()
        print "]"
        s.schedule(self.t_cs, self.eContentSwitch, self.process_queue.popleft(), s)  
        s.run()    
      
    #event occurs when it's done 
    #def event(id, simulator, scheduled, rescheduled=None):
    def eContentSwitch(self, process, simulator):
        #time 13ms: P1 started using the CPU 
        print "time %dms:" % simulator.time,"P%d"% process.ID, "started using the CPU [Q",
        sys.stdout.write('')
        self.printQueue()
        print "]"
        self.CPUIdle = False
        simulator.schedule(simulator.time + process.burst_time, self.eCPUBurst, process, simulator) 

    def eCPUBurst(self, process, simulator):
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
            #time 579ms: P2 terminated
            print "time %dms:"% simulator.time,"P%d"%process.ID, "terminated [Q",
            sys.stdout.write('')
            self.printQueue()
            print "]"
            self.active_n -= 1
            if(self.active_n == 0):
                print "time %dms: Simulator ended" % simulator.time
        if(self.process_queue):
            next_process = self.process_queue.popleft() 
            simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, simulator) 
            self.CPUIdle = False
        else: #empty process queue
            self.CPUIdle = True
    
    def eIOBurst(self, process, simulator):
        if process.num_burst == 0:
            return
        self.process_queue.append(process)
        #time 468ms: P1 completed I/O
        print "time %dms:"% simulator.time,"P%d"% process.ID, "completed I/O [Q",
        sys.stdout.write('')
        self.printQueue()
        print "]"

        if self.CPUIdle :
        # it means 1.queue empty 2.current process has more rounds 
            next_process = self.process_queue.popleft() 
            #Schedule directly
            simulator.schedule(simulator.time + self.t_cs, self.eContentSwitch, next_process, simulator) 
            self.CPUIdle = False

if(__name__=="__main__"):
    #@TODO make the filename optional
    infile = r"./processes.txt"
    if len(sys.argv)>1 and str(sys.argv[1]):
        infile = str(sys.argv[1]) 
    with open(infile) as f:
        f = f.readlines()
    cpu = CPU() 
    
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
    
