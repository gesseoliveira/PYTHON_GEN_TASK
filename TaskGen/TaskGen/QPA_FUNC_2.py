import numpy as np
import pandas as pd
import random
import math

utilization=[]
U=0;

existing_analysis_count_list=[]
qpa_count_list=[]

def UUniFastDiscard(n, u, nsets):
    sets = []
    while len(sets) < nsets:
        # Classic UUniFast algorithm:
        utilizations = []
        sumU = u
        for i in range(1, n):
            nextSumU = sumU * random.random() ** (1.0 / (n - i))
            utilizations.append(sumU - nextSumU)
            sumU = nextSumU
        utilizations.append(sumU)

        # If no task utilization exceeds 1:
        if all(ut <= 1 for ut in utilizations):
            sets.append(utilizations)
    print(sets)
#     return sets


def gen_ripoll(nsets, compute, deadline, period, target_util):
    """
    Ripoll et al. tasksets generator.
    Args:
        - `nsets`: Number of tasksets to generate.
        - `compute`: Maximum computation time of a task.
        - `deadline`: Maximum slack time.
        - `period`: Maximum delay after the deadline.
        - `target_util`: Total utilization to reach.
    """
    sets = []
    for i in range(nsets):
        task_set = []
        total_util = 0.0
        while total_util < target_util:
            c = random.randint(1, compute)
            a=0
            if c<10:
                a=c
            elif c<100:
                a=2*c
            elif c<1000:
                a=3*c
            else:
                a=4*c
#             d = c + random.randint(0, deadline)
#             print(a,c)
            p = random.randint(0, period)
            if(math.ceil(1.2*p)<a):
                continue
            d = random.randint(a, math.ceil(1.2*p))
#             p = random.randint(0, period)
            task_set.append([c, d, p])
            total_util += float(c) / p
        sets.append(task_set)
#         print(task_set)
#         print("---")
    return sets


def upper_bound_L_a(task):
    L_a=0;
    for i in range(len(task)):
        L_a=max(L_a,task[i][1])
    value=0
    for i in range(len(task)):
        value+=(task[i][2]-task[i][1])*utilization[i]
    # print(value)
    L_a=max(L_a,value/(1-U))
    return L_a


#upper_bound L_b
def upper_bound_L_b(task):
    w_0=0
    for i in range(len(task)):
        w_0+=task[i][0]
    
    # w_1=0
#     print(w_0)
    while True:
        val=0
        for i in range(len(task)):
            try:
                x=math.ceil(w_0/task[i][2])*task[i][0]
                val+=x
            except:
                print(val)
        if(val==w_0):
            return val
        w_0=val
    


def h_function(task,t):
    result=0
    for i in range(len(task)):
        factor=max(0,1+(math.floor((t-task[i][1])/task[i][2])))*task[i][0]
        result+=factor
    return result


def check_absolute_deadlines(task,x):
    count=set()
#     count.add(0)
    for i in range(len(task)):
        k=0
        while(True):
            d_i=k*task[i][2]+task[i][1]
            if d_i<x and h_function(task,d_i)<=d_i:
#                 print(h_function(task,d_i), d_i)
                k+=1
                count.add(d_i)
#                 print(d_i)
            else:
                break
#         print(count)
#     print(sorted(count))
    return count



def calculate_d_delta(task,deadlines):
    d_delta=0
    for deadline in deadlines:
        if h_function(task,deadline)>deadline:
            d_delta=max(d_delta,deadline)
    return d_delta



def qpa(task,starting_value,absolute_deadline,d_min):
    t=starting_value
    count=0
    while h_function(task,t)<t and h_function(task,t)>d_min:
        if h_function(task,t)<t:
            t=h_function(task,t)
        else:
            t=0
            for ad in absolute_deadline:
                if ad<t:
                    t=max(ad,t)
        count+=1
    if(h_function(task,t)<d_min):
        print("Schedulable")
        return count+1
    else:
        print("Not schedulable")
        return -1


def QPA_FUNC_2(task):
        U=0;
        
        for i in range(len(task)):
            utilization.append(task[i][0]/task[i][2])
            U+=task[i][0]/task[i][2]
        if(U>1):
            print("Not schedulable")
            return -1;
        L_a=upper_bound_L_a(task)
        L_b=upper_bound_L_b(task)
        print("L_a : ",L_a)
        print("L_b: ",L_b)
        if(L_b is None):
            L_b=L_a
        deadlines=check_absolute_deadlines(task,L_a)
        existing_analysis_count=len(deadlines)
        deadlines=check_absolute_deadlines(task,L_b)
        existing_analysis_count=min(existing_analysis_count,len(deadlines))
        L=0
        if U==1:
            L=L_b
        else:
            L=min(L_a,L_b)
        d_min=task[0][1]
        
        for i in range(len(task)):
            d_min=min(d_min,task[i][1])
        absolute_deadlines=check_absolute_deadlines(task,L)
        d_delta=calculate_d_delta(task,absolute_deadlines)
        starting_value=0
        for i in range(len(task)):
            k=0
            while(True):
                d_i=k*task[i][2]+task[i][1]
                if d_i>=L:
                    break
                starting_value=max(starting_value,d_i)
                k+=1
        qpa_count=qpa(task,starting_value,absolute_deadlines,d_min)
        print("QPA Analysis count: ",qpa_count)
        print("Previous Analysis Count:",existing_analysis_count)
        qpa_count_list.append(qpa_count)
        existing_analysis_count_list.append(existing_analysis_count)
        return 0

