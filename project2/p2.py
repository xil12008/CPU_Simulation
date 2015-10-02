import heapq
from collections import deque
import pdb
import sys
import Queue as Q
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

from CPU import CPU
from processqueue import ProcessQueue 
from processinfo import ProcessInfo 
from simulator import Simulator 


"""
NOTE: THIS PROGRAM IS DEVELOPED UNDER PYTHON 2.7
      In python 3.0, the notation for queue is different than ver. < 3.0
"""

if(__name__=="__main__"):
    infile = r"./processes.txt"
    if len(sys.argv)>1 and str(sys.argv[1]):
        infile = str(sys.argv[1]) 
    with open(infile) as f:
        f = f.readlines()
    processList = []
    for line in f:
         if(line.strip() and line[0]=='#'):
             continue 
         segments = line.split('|')
         if(len(segments)!=5):
             print "Wrong Input Line:", line 
             continue
         else:
             processList.append((int(segments[0]),\
                                 int(segments[1]),\
                                 int(segments[2]),\
                                 int(segments[3]),\
				 int(segments[4])))

    queueTypeList = ['FCFS', 'SRT', 'PWA']
  
    burst_num = 0
    for ptuple in processList:
        burst_num += ptuple[2]

    for qtype in queueTypeList: 
        cpu = CPU(queuetype=qtype)
        for ptuple in processList:
            cpu.addProcess(ProcessInfo(*ptuple)) 
        cpu.run()
        print cpu.burstTimeSum, cpu.turnaroundTimeSum, cpu.contentSwitchSum 
        with open("simout.txt", "a") as outfile:
            print "Algorithm %s", qtype
            print "-- average CPU burst time: %.2f ms" % (1.0 * cpu.burstTimeSum/burst_num) 
            print "-- average wait time: None ms" 
            print "-- average  turnaround time: %.2f ms" % (1.0 * cpu.turnaroundTimeSum/cpu.n)
            print "-- total number of context switches: %d" % cpu.contentSwitchSum 




    
