
#!/usr/bin/python

"""A taskset generator for experiments with real-time task sets

Copyright 2010 Paul Emberson, Roger Stafford, Robert Davis. 
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, 
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation 
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESS 
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO 
EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are 
those of the authors and should not be interpreted as representing official 
policies, either expressed or implied, of Paul Emberson, Roger Stafford or 
Robert Davis.

Includes Python implementation of Roger Stafford's randfixedsum implementation
http://www.mathworks.com/matlabcentral/fileexchange/9700
Adapted specifically for the purpose of taskset generation with fixed
total utilisation value

Please contact paule@rapitasystems.com or robdavis@cs.york.ac.uk if you have 
any questions regarding this software.
"""

import numpy
import optparse
import sys
import textwrap



import math
import random
import matplotlib.pyplot

import matplotlib.pyplot as ptl
import matplotlib.pyplot as ptl_error
import QPA_FUNC
import QPA_FUNC_2



#Number of Tasks
nTask = 60


nTask_Start  = nTask
nTask_End    = nTask
nTask_Step   = 5

nTask_Counter= 0

#How many differents groups will be generated
nGroups = "1"
nGroup_Loop = 30

nGroup_File_Name = 1

# CPU Utilization 
UCpu = 0.0

Fator_ms_us = 1 # 1 - ms , 100 - us

U_Start  = 0.50
U_End    = 0.50
U_Step   = 0.80


# Period interval
PeriodMin  = "10"
PeriodMax  = "1000"
PeriodGran = "1"

# Enable/Disable calculate with aproximation  
ApxEn = True

#Choose output file to task set generated
EDF_QUEUE = 1
RM        = 2
ALL       = 255

OUTPUT_CHOOSE = ALL


TaskSet =[]


def Calc_HyperPeriod_Taskset(TaskSet):
    Len     = len(TaskSet) - 1
    LcmResult = TaskSet[0][2]
    LcmIndex = 0

    while LcmIndex < Len:
        LcmResult = lcm(LcmResult, TaskSet[LcmIndex + 1][2]   )     
        LcmIndex = LcmIndex + 1

    return LcmResult


def GetDivisors( n ) : 
    i = 1
    Divisors=[ ]

    while i <= n : 
        if (n % i==0) : 
           Divisors.append(i)

        i = i + 1

    return Divisors

def lcm(x, y):
 
 if x > y:
   greater = x
 else:
   greater = y
 
 while(True):
   if((greater % x == 0) and (greater % y == 0)):
     lcm = greater
     break
   greater += 1
 
 return lcm

def Demand_Bound_Function(TaskGroup, t):
    Ht = 0
    t_aux = 0

    while t_aux < t:
        Ht = 0
        t_aux = t_aux + 1

        for element in TaskGroup:
            x = (1 + math.floor((t_aux-element[1])/element[2]) )*element[0]
            Ht = Ht + x

        if t_aux >= Ht:
           continue 
        else:
            #return "NO : "+ str(t_aux)
            return 0
    return 1

def Calc_Task_Utz(TaskGroup):
    # Calculate TaskUtilization total 
    TaskUtilization = 0
    BiggestDeadline = 0
    for element in TaskSet:
            #Sum of Ci/Ti 
      TaskUtilization = TaskUtilization + element[0]/element[2]
   
      if BiggestDeadline <= element[1]: 
         BiggestDeadline = element[1]

    return TaskUtilization





def StaffordRandFixedSum(n, u, nsets):

    #deal with n=1 case
    if n == 1:
        return numpy.tile(numpy.array([u]),[nsets,1])
    
    k = numpy.floor(u)
    s = u
    step = 1 if k < (k-n+1) else -1
    s1 = s - numpy.arange( k, (k-n+1)+step, step )
    step = 1 if (k+n) < (k-n+1) else -1
    s2 = numpy.arange( (k+n), (k+1)+step, step ) - s

    tiny = numpy.finfo(float).tiny
    huge = numpy.finfo(float).max

    w = numpy.zeros((n, n+1))
    w[0,1] = huge
    t = numpy.zeros((n-1,n))

    for i in numpy.arange(2, (n+1)):
        tmp1 = w[i-2, numpy.arange(1,(i+1))] * s1[numpy.arange(0,i)]/float(i)
        tmp2 = w[i-2, numpy.arange(0,i)] * s2[numpy.arange((n-i),n)]/float(i)
        w[i-1, numpy.arange(1,(i+1))] = tmp1 + tmp2;
        tmp3 = w[i-1, numpy.arange(1,(i+1))] + tiny;
        tmp4 = numpy.array( (s2[numpy.arange((n-i),n)] > s1[numpy.arange(0,i)]) )
        t[i-2, numpy.arange(0,i)] = (tmp2 / tmp3) * tmp4 + (1 - tmp1/tmp3) * (numpy.logical_not(tmp4))

    m = nsets
    x = numpy.zeros((n,m))
    rt = numpy.random.uniform(size=(n-1,m)) #rand simplex type
    rs = numpy.random.uniform(size=(n-1,m)) #rand position in simplex
    s = numpy.repeat(s, m);
    j = numpy.repeat(int(k+1), m);
    sm = numpy.repeat(0, m);
    pr = numpy.repeat(1, m);

    for i in numpy.arange(n-1,0,-1): #iterate through dimensions
        e = ( rt[(n-i)-1,...] <= t[i-1,j-1] ) #decide which direction to move in this dimension (1 or 0)
        sx = rs[(n-i)-1,...] ** (1/float(i)) #next simplex coord
        sm = sm + (1-sx) * pr * s/float(i+1)
        pr = sx * pr
        x[(n-i)-1,...] = sm + pr * e
        s = s - e
        j = j - e #change transition table column if required

    x[n-1,...] = sm + pr * s
    
    #iterated in fixed dimension order but needs to be randomised
    #permute x row order within each column

    v1 = range(0,m)

    for i in v1:
        x[...,i] = x[numpy.random.permutation(n),i]

    return numpy.transpose(x);

def gen_periods(n, nsets, min, max, gran, dist):

    if dist == "logunif":
        periods = numpy.exp(numpy.random.uniform(low=numpy.log(min), high=numpy.log(max+gran), size=(nsets,n)))
    elif dist == "unif":
        periods = numpy.random.uniform(low=min, high=(max+gran), size=(nsets,n))
    else:
        return None
    periods = numpy.floor(periods / gran) * gran

    return periods

def gen_tasksets(options):
    x = StaffordRandFixedSum(options.n, options.util, options.nsets)
    periods = gen_periods(options.n, options.nsets, options.permin, options.permax, options.pergran, options.perdist)
    #iterate through each row (which represents utils for a taskset)
    for i in range(numpy.size(x, axis=0)):
        C = x[i] * periods[i]
        if options.round_C:
            C = numpy.round(C, decimals=0)
        
        taskset = numpy.c_[x[i], C / periods[i], periods[i], C]

        print_taskset(taskset, options.format)
    print ("")   
    

def Generate_File_EDF_Queue(taskset):
    cpuTot = 0.0

    file1 = open( "EDF\\TQ_" + nTask + "_Num_" + str(nGroup_File_Name) + "_edf_queue.txt","w") 
    d = []
    
    for t in range(numpy.size(taskset,0)):
        data = { 'Ugen' : taskset[t][0], 'U' : taskset[t][1], 'T' : taskset[t][2], 'C' : taskset[t][3] }
        d.append(data) 

    NewtaskSet =  sorted(d, key = lambda i: i['T']) 

    for t in range(numpy.size(NewtaskSet,0))  :
        print (NewtaskSet[t])
        
        cpuTot = cpuTot + NewtaskSet[t]['U']
        
        s = "PeriodTask" + str(t+1) + "="  + str( NewtaskSet[t]['T'] ) +";"  
        file1.write(s)

        s = "CostTask" + str(t+1) + "="  +  str(NewtaskSet[t]['C']*Fator_ms_us) + ";"
        file1.write(s)

        s =  "MsFreeRTOS_CreateTask(  MyTask_Func"+ str(t+1) + ", " + chr(34) + "Task" + str(t+1) + chr(34) + ", stack_task, (void*) &CostTask"   + str(t+1) + " , 2 , NULL  , PeriodTask" + str(t+1) + ",PeriodTask" + str(t+1) + ", CostTask" + str(t+1) + " );   \r\n"

        file1.write(s)

    s = " /*CPU utilization: "  + str(cpuTot)  + "*/"

    file1.write(s)

    return None 

def Generate_File_RM(taskset):
    cpuTot = 0.0
    
    file1 = open( "RM\\U_"+str(UCpu)+""  + "TQ_" + nTask + "_Num_" + str(nGroup_File_Name) + ".txt","w") 
    
    d = []
    
    MaxPriority = 0

    for t in range(numpy.size(taskset,0)):
        data = { 'Ugen' : taskset[t][0], 'U' : taskset[t][1], 'T' : taskset[t][2], 'C' : taskset[t][3] }
        d.append(data) 
        MaxPriority = MaxPriority + 1
        
    NewtaskSet =  sorted(d, key = lambda i: i['T']) 
    
    print ("RM TASK SET")

    for t in range(numpy.size(NewtaskSet,0))  :
        
        cpuTot = cpuTot + NewtaskSet[t]['U']
        s = "#define  T" + str(t+1) + "_P  "  + str( NewtaskSet[t]['T']     ) + "\r\n" 
        file1.write(s)
        s = "#define  T" + str(t+1) + "_C  "  +  str(NewtaskSet[t]['C'] *Fator_ms_us) + "\r\n"
        file1.write(s)

    for t in range(numpy.size(NewtaskSet,0))  :
       s = "PeriodTask" + str(t+1) + "="  + str( NewtaskSet[t]['T'] ) +";"  
       file1.write(s)

       s = "CostTask" + str(t+1) + "="  +  str(NewtaskSet[t]['C']*Fator_ms_us) + ";"
       file1.write(s)

       s =  "MsFreeRTOS_CreateTask(  MyTask_Func"+ str(t+1) + ", " + chr(34) + "Task" + str(t+1) + chr(34) + ", stack_task, (void*) &CostTask"   + str(t+1) + " , " + str(MaxPriority-t)+ " , NULL  , PeriodTask" + str(t+1) + ",PeriodTask" + str(t+1) + ", CostTask" + str(t+1) + " );   \r\n"

           # Task Model (Ci,Di,Ti) 
       TaskSet.append (   ( int( NewtaskSet[t]['C']*Fator_ms_us)  , int (NewtaskSet[t]['T'])  , int(NewtaskSet[t]['T']) ) )
       #TaskSet.append (   ( ( NewtaskSet[t]['C']*Fator_ms_us)  , (NewtaskSet[t]['T'])  , (NewtaskSet[t]['T']) ) )
       #TaskSet.append( (0,0,0)  )

#       s =  "xTaskCreate(  MyTask_Func"+ str(t+1) + ", " + chr(34) + "Task" + str(t+1) + chr(34) + ", 100, (void*) 0"  + " ," + str(MaxPriority-t)+ " , NULL );" + "\r\n"
       file1.write(s)

    s = " /*CPU utilization: "  + str(cpuTot)  + "*/"

    file1.write(s)

    print(s)


    return None



def Add_ES_Task(C,D,P,Us):
    cpuTot = 0.0
    t= -1
    # PeriodTask7=60000.0  ; CostTask7=000.0 ;  MsFreeRTOS_CreateEnergySavingTask(   "Es Task", stack_task, (void*) &CostTask7 , NULL  , PeriodTask7,DeadlineEsTask, CostTask7 );

    file1 = open( "RM\\U_"+str(Us)+""  + "TQ_" + nTask + "_Num_" + str(nGroup_File_Name) + ".txt","a") 
    
    s = "\r\n"
    file1.write(s)

    s = "DeadlineEsTask = " + str(D) + ";" + "\r\n"
    file1.write(s)

    s = "PeriodTask" + str(t+1) + "="  + str(P) +";"  
    file1.write(s)

    s = "CostTask" + str(t+1) + "="  +  str(C*Fator_ms_us) + ";"
    file1.write(s)

    s =  "MsFreeRTOS_CreateEnergySavingTask(  " + chr(34) + "Es Task"  + chr(34) + ", stack_task, (void*) &CostTask"   + str(t+1) + " ,  NULL  , PeriodTask" + str(t+1) + ",DeadlineEsTask" + ", CostTask" + str(t+1) + " );   \r\n"

    # Append 'hello' at the end of file
    file1.write(s)

    # Close the file
    file1.close()

    return None


def XML_TASKS(taskGroup):

    file1 = open( "XML_TEST.txt","w") 
    i = 1
    for element in taskGroup:       
       s = "\r\n"
       file1.write(s)
       #\
       s="<task ACET= " + chr(34) + "0.0" + chr(34)  +  " WCET=" + chr(34) +  str(element[0] )  +  chr(34)  +     " abort_on_miss=" +  chr(34) + "yes" +  chr(34)  +  " activationDate=\"0.0\" " +  " base_cpi=\"1.0\" " + "deadline=\"" + str(element[1]) +"\"" + " et_stddev=\"0.0\" " +  " id=\"" + str(i) +"\"" +  " instructions=\"0\" " + "list_activation_dates=\"\" mix=\"0.5\" " +  " name=\"T" + str(i) + "\" " + " period=\"" + str(element[2]) + "\" " +  " preemption_cost=\"0\" task_type=\"Periodic\"/>"

       #<task ACET="0.0" WCET="2.0" abort_on_miss="yes" activationDate="0.0" base_cpi="1.0" deadline="18.0" et_stddev="0.0" id="1" instructions="0" list_activation_dates="" mix="0.5" name="TASK T1" period="18.0" preemption_cost="0" task_type="Periodic"/>
       i = i + 1
       file1.write(s)

    
    # Append 'hello' at the end of file
    #file1.write(s)

    # Close the file
    file1.close()

    return None


def print_taskset(taskset, format):
    global nGroup_File_Name

    if OUTPUT_CHOOSE == EDF_QUEUE:
        Generate_File_EDF_Queue(taskset)
    elif OUTPUT_CHOOSE == RM:
        Generate_File_RM(taskset)
    elif OUTPUT_CHOOSE == ALL:
        Generate_File_EDF_Queue(taskset)
        Generate_File_RM(taskset)
    else:
        print("FAIL OUTPUT FILE !")
    
    


def main():

    print("Start Main: ")


    usage_str = "%prog [options]"

    description_str = "This is a taskset generator intended for generating data for experiments with real-time schedulability tests and design space exploration tools.  The utilisation generation is done using Roger Stafford's randfixedsum algorithm.  A paper describing this tool was published at the WATERS 2010 workshop. Copyright 2010 Paul Emberson, Roger Stafford, Robert Davis. All rights reserved.  Run %prog --about for licensing information."
            

    epilog_str = "Examples:"
 
    #don't add help option as we will handle it ourselves
    parser = optparse.OptionParser(usage=usage_str, 
                                   description=description_str,
                                   epilog=epilog_str,
                                   add_help_option=False,
                                   version="%prog version 0.1")
   
    parser.add_option("-h", "--help", action="store_true", dest="help",
                      default=False,
                      help="Show this help message and exit")

    parser.add_option("--about", action="store_true", dest="about",
                      default=False,
                      help="See licensing and other information about this software")
					  
    parser.add_option("-u", "--taskset-utilisation",
                      metavar="UTIL", type="float", dest="util",
                      default=UCpu,
                      help="Set total taskset utilisation to UTIL [%default]")
    parser.add_option("-n", "--num-tasks",
                      metavar="N", type="int", dest="n",
                      default=nTask,
                      help="Produce tasksets of size N [%default]")
    parser.add_option("-s", "--num-sets",
                      metavar="SETS", type="int", dest="nsets",
                      default=nGroups,
                      help="Produce SETS tasksets [%default]")
    parser.add_option("-d", "--period-distribution",
                      metavar="PDIST", type="string", dest="perdist",
                      default="unif",
                      help="Choose period distribution to be 'unif' or 'logunif' [%default]")
    parser.add_option("-p", "--period-min",
                      metavar="PMIN", type="int", dest="permin",
                      default=PeriodMin,
                      help="Set minimum period value to PMIN [%default]")
    parser.add_option("-q", "--period-max",
                      metavar="PMAX", type="int", dest="permax",
                      default=PeriodMax,
                      help="Set maximum period value to PMAX [PMIN]")
    parser.add_option("-g", "--period-gran",
                      metavar="PGRAN", type="int", dest="pergran",
                      default=PeriodGran,
                      help="Set period granularity to PGRAN [PMIN]")
    
    parser.add_option("--round-C", action="store_true", dest="round_C",
                      default=ApxEn,
                      help="Round execution times to nearest integer [%default]")
    
    format_default = '%(Ugen)f %(U)f %(C).2f %(T)d\\n';
    format_help = "Specify output format as a Python template string.  The following variables are available: Ugen - the task utilisation value generated by Stafford's randfixedsum algorithm, T - the generated task period value, C - the generated task execution time, U - the actual utilisation equal to C/T which will differ from Ugen if the --round-C option is used.  See below for further examples.  A new line is always inserted between tasksets. [" + format_default + "]"
    parser.add_option("-f", "--output-format",
                      metavar="FORMAT", type="string", dest="format",
                      default = '%(Ugen)f %(U)f %(C).2f %(T)d\n',
                      help=format_help)

    (options, args) = parser.parse_args()

    if options.about:
        print (__doc__)
        return 0

    if options.help:
        print_help(parser)
        return 0

    if options.n < 1:
        print >>sys.stderr, "Minimum number of tasks is 1"
        return 1

    if options.util > options.n:
        print >>sys.stderr, "Taskset utilisation must be less than or equal to number of tasks"
        return 1

    if options.nsets < 1:
        print >>sys.stderr, "Minimum number of tasksets is 1"
        return 1

    known_perdists = ["unif", "logunif"]
    if options.perdist not in known_perdists:
        print >>sys.stderr, "Period distribution must be one of " + str(known_perdists)
        return 1

    if options.permin <= 0:
        print >>sys.stderr, "Period minimum must be greater than 0"
        return 1

    #permax = None is default.  Set to permin in this case
    if options.permax == None:
        options.permax = options.permin

    if options.permin > options.permax:
        print >>sys.stderr, "Period maximum must be greater than or equal to minimum"
        return 1

    #pergran = None is default.  Set to permin in this case
    if options.pergran == None:
        options.pergran = options.permin
        
    if options.pergran < 1:
        print >>sys.stderr, "Period granularity must be an integer greater than equal to 1"
        return 1

    if (options.permax % options.pergran) != 0:
        print >>sys.stderr, "Period maximum must be a integer multiple of period granularity"
        return 1

    if (options.permin % options.pergran) != 0:
        print >>sys.stderr, "Period minimum must be a integer multiple of period granularity"
        return 1
        
    options.format = options.format.replace("\\n", "\n")

    gen_tasksets(options)
    
    return 0
    
def print_help(parser):
    parser.print_help();

    print ("")
    
    example_desc = \
            "Generate 5 tasksets of 10 tasks with loguniform periods " +\
            "between 1000 and 100000.  Round execution times and output "+\
            "a table of execution times and periods."
    print (textwrap.fill(example_desc, 75))
    print ("    " +parser.get_prog_name() + " -s 5 -n 10 -p 1000 -q 100000 -d logunif --round-C -f \"%(C)d %(T)d\\n\"")

    print ("")

    example_desc = \
            "Print utilisation values from Stafford's randfixedsum " +\
            "for 20 tasksets of 8 tasks, with one line per taskset, " +\
            "rounded to 3 decimal places:"

    print (textwrap.fill(example_desc, 75))
    print ("    " + parser.get_prog_name() + " -s 20 -n 8 -f \"%(Ugen).3f\"")
    
 

def Func_Exe_QPA_Gen_File():
      # Task Model (Ci,Di,Ti) 
        # Must create taskset here:

       #TaskSet = [ (14,36,36), (13,42,42),(1,1,242) ]
        #TaskSet = [ (5,20,20),(10,20,20)]
        #TaskSet = [ (1,7,7),(1,11,11),(3,50,50),(2,40,40),(1,30,30),(1,8,8),(2,12,12),(1,12,12),(1,23,23),(1,20,20) ]

        #TaskSet = [ (5,30,30),(5,40,40)]
        #19 , 19, 5190
       print(TaskSet )
       #modificado
       #LcmResult = Calc_HyperPeriod_Taskset(TaskSet)
  
       LcmResult = 1
       for element in TaskSet:
          LcmResult = LcmResult * element[1]
   
       #LcmResult  = 100000000000000
       

       print("HyperPeriod:" +  str(LcmResult) )


       #Energy Save Task 
       Len     = len(TaskSet) - 1
       TaskSet.append(  (0,0,0)  )
       TaskSet[Len+1] =  (1, 1, LcmResult )

       Len     = len(TaskSet) - 1
       SimP    = LcmResult

       #TaskSet = [ (14,36,36), (13,42,42),(1,1,242) ]

       TaskUtilization = Calc_Task_Utz(TaskSet)
       La  = QPA_FUNC.Algorithm_LA(TaskSet)
       print("La:" +  str(La) )

       Lb  = QPA_FUNC.Algorithm_LB(TaskSet)
       print("Lb:" +  str(Lb) )
       QPA = QPA_FUNC.Algorithm_QPA(TaskSet,La[3],Lb[1],TaskUtilization)

       if QPA == True:
            while QPA == True:
               TaskSet[Len] = (TaskSet[Len][0] +1 , TaskSet[Len][0] +1 , TaskSet[Len][2])
               TaskUtilization = Calc_Task_Utz(TaskSet)
               La  = QPA_FUNC.Algorithm_LA(TaskSet)
               Lb  = QPA_FUNC.Algorithm_LB(TaskSet)
               QPA = QPA_FUNC.Algorithm_QPA(TaskSet,La[3],Lb[1],TaskUtilization)

            TaskSet[Len] = (TaskSet[Len][0] -2 , TaskSet[Len][1]-2 , TaskSet[Len][2])
       else:
            while QPA == False:
               TaskSet[Len] = (TaskSet[Len][0] - 1 , TaskSet[Len][1]-1 , TaskSet[Len][2])
               TaskUtilization = Calc_Task_Utz(TaskSet)
               La  = QPA_FUNC.Algorithm_LA(TaskSet)
               Lb  = QPA_FUNC.Algorithm_LB(TaskSet)
               QPA = QPA_FUNC.Algorithm_QPA(TaskSet,La[3],Lb[1],TaskUtilization)
   
       print(TaskSet[Len] )

        # Figure outing the best value for Period
       #DivisorsList = GetDivisors(SimP) 

       DivisorsList = range(1,1000,5)

       SizeDivisors =  len (DivisorsList)
        #print(DivisorsList)
       i = 0
       #while i < SizeDivisors :
       while i < SizeDivisors :
              TaskSet[Len] = (TaskSet[Len][0] , TaskSet[Len][1] , DivisorsList[i] )
              #modificado
              #TaskSet[Len] = (TaskSet[Len][0] , TaskSet[Len][1] , i+1 )


              TaskUtilization = Calc_Task_Utz(TaskSet)
              La  = QPA_FUNC.Algorithm_LA(TaskSet)
              Lb  = QPA_FUNC.Algorithm_LB(TaskSet)
              QPA = QPA_FUNC.Algorithm_QPA(TaskSet,La[3],Lb[1],TaskUtilization)

              if QPA == True:
                  break;
              i = i + 1

       print(TaskSet[Len] )

       Add_ES_Task(TaskSet[Len][0] ,TaskSet[Len][1],TaskSet[Len][2], UCpu  )

       XML_TASKS(TaskSet)



if __name__ == "__main__":
   
   UCpu = U_Start 
   k = 0
   while UCpu <= U_End+0.01:
       nTask_Counter = nTask_Start

       while nTask_Counter <= nTask_End:
           nTask = str(nTask_Counter)
   
           k = 0
           while k < nGroup_Loop:
              main()
              Func_Exe_QPA_Gen_File()
              TaskSet = []
              k = k + 1
              nGroup_File_Name = nGroup_File_Name + 1
           
           nTask_Counter    = nTask_Counter + nTask_Step
           nGroup_File_Name = 1


       UCpu = UCpu + U_Step  





