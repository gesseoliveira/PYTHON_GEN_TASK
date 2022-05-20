import math
import random
import matplotlib.pyplot

import matplotlib.pyplot as ptl
import matplotlib.pyplot as ptl_error

def Calculate_Deadline_Point_Quantity(TimeLimit,TaskGroup):
    k    = 0 
    i    = 0
    time = 0
    TimeVector = []

    for element in TaskGroup:
        k = math.ceil((TimeLimit-element[1])/element[2])  
    
        for KTimes in range(k):
            time = element[2]*KTimes + element[1]
            if( (time in TimeVector) == False):
                i = i + 1
                TimeVector.append(time)

    CheckPointQnt = i
    
    return CheckPointQnt

# Implementation Eq (1) on page 5.
def Demand_Bound_Function(TaskGroup, t):
    Ht = 0
    for element in TaskGroup:
        x = (1 + math.floor((t-element[1])/element[2]) )*element[0]
        if x < 0:
            x = 0
        Ht = Ht + x
    return Ht

def Algorithm_LA(TaskGroup):

    LaTot           = 0.0
    LaTotPerTask    = 0.0
    CheckPointLa    = 0.0 

    TaskUtilization = 0.0 
    BiggestDeadline = 0.0 


    # Calculate TaskUtilization total 
    for element in TaskGroup:
        #Sum of Ci/Ti 
        TaskUtilization = TaskUtilization + element[0]/element[2]
   
        if BiggestDeadline <= element[1]: 
           BiggestDeadline = element[1]

    #print("CPU Utilization:"  + str(TaskUtilization))
    #print("Biggest Deadline:" + str(BiggestDeadline))

    #Calculate La regarding task
    for element in TaskGroup:
        LaTot = LaTot + (element[2]- element[1])*(element[0]/element[2])
        LaTotPerTask  =  LaTot

    if TaskUtilization != 1:
       LaTotPerTask = LaTotPerTask/(1-TaskUtilization) 
       LaTot        = LaTot/(1-TaskUtilization) 

    #print("La Per Task:" + str(LaTotPerTask))

    #Define La by comparasion between La and biggest deadline 
    if LaTot <= BiggestDeadline:
      LaTot = BiggestDeadline

    #print("La Final:" + str(LaTot))

    p = Calculate_Deadline_Point_Quantity(LaTot,TaskGroup)

    #print("Deadline points quantity: " + str(p))

    Answer =[]
    Answer.append(p)
    Answer.append(LaTot)

    #---------------LA*-----------------------------------
    LaAst                      = 0.0
    BiggestDeadlineMinusPeriod = 0.0
    CheckPointLaAst            = 0.0

    # Calculate biggest difference between Dealine and Period
    for element in TaskGroup:
        if (element[1]-element[2]) >= BiggestDeadlineMinusPeriod:
            BiggestDeadlineMinusPeriod = (element[1]-element[2]) 

    # Define final value to La* (Max{BiggestDeadlineMinusPeriod,La})
    if LaTotPerTask >= BiggestDeadlineMinusPeriod:
        LaAst = (LaTotPerTask)
    else:
        LaAst = BiggestDeadlineMinusPeriod

    #print("LaAst:" +str(LaAst))

    p = Calculate_Deadline_Point_Quantity(LaAst,TaskGroup)
    Answer.append(p)
    Answer.append(LaAst)

    return Answer

def Algorithm_LB(TaskGroup):
    W0 = 0.0
    Wm = 0.0
    Lb = 0.0
    tryErr = 0

    #Calculate W0 (eq (4) on page 6)
    for element in TaskGroup:
        W0 = W0 + element[0]

    #Calculate Lb (eq (5) on page 6)
    Wm   = W0
    Wm_1 = 0
    Loop = True
    while Loop:
        tryErr = tryErr + 1
        for element in TaskGroup:
           try:
               Wm_1 = Wm_1 + math.ceil(Wm/element[2])*element[0]
           except:
               Loop = False
              # Wm_1 = Wm
               break
        if Wm_1 == Wm:
           break
        else:
           Wm   = Wm_1
           Wm_1 = 0
           if tryErr > 1000000:
               Wm   = Wm_1
               Loop = False
               break

    #print("Lb:" + str(Wm_1) )
    Lb = Wm_1
    p = Calculate_Deadline_Point_Quantity(Lb,TaskGroup)
    #print("Deadline points quantity: " + str(p))


    Answer = []
    Answer.append(p)
    Answer.append(Lb)
    return Answer

def Algorithm_QPA(TaskGroup,LA_AST,LB,TaskUtilization):
    
    #Implementation based on Theorem 7 on page 11.

    #Is necessary define how is Dmin (Minimum Deadline among set task)
    Dmin = TaskGroup[0][1]

    for element in TaskGroup:
      if Dmin > element[1]:
        Dmin = element[1]
    #print("Deadline minimum:" + str(Dmin))

    #Is necessary define 'L' parameter (Refernce eq (7) on page 8)
    L = 0

    if TaskUtilization < 1:
        if LA_AST <= LB:
            L = math.ceil(LA_AST) 
        else:
            L = math.ceil(LB)
    else:
        return False
    #print("L Value:" + str(L))

    ##########################################################
    #               Begin QPA implementation
    ##########################################################
    t = L
    Ht= Demand_Bound_Function(TaskGroup,t)

    while True:
        #print("t:" + str(t) + " " + "H(t):" + str(Ht) )

        if Ht > t or Ht < Dmin:
            break;

        if Ht < t:
            t = Ht
            Ht = Demand_Bound_Function(TaskGroup,t)
        else:
            # implementation: max(Di|Di<t)    
            j = 1
            dtMax = 0
            while j < len(TaskGroup):
                if TaskGroup[j][1] < t:
                   dj = (math.floor( (t-TaskGroup[j][1])/TaskGroup[j][2] )*TaskGroup[j][2] ) + TaskGroup[j][1]
                   if dj == t :
                      dj = dj- TaskGroup[j][2]
                   if dj > dtMax:
                       dtMax = dj
                j = j + 1

            t = dtMax

            Ht = Demand_Bound_Function(TaskGroup,t)

    if Ht <= Dmin:
        #print("The task set is schedulable !")
        return True
    else:
        #print("The task set is not schedulable")
        return False


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

#Task Model (Ci,Di,Ti)

#First article example 
#TaskSet = [(3,4,9),(2,6,4),(4,2800,3100),(8,10170,10200),(3,406,430)]

#Example A
#TaskSet = [(6000,18000,31000),(2000,9000,9800),(1000,12000,17000),(90,3000,4200),(8,78,96),(2,16,12),(10,120,280),(26,160,660)]

#Example B

#taskset =[  (0.046017  , 1.419897   , 1.324642),
#            (0.103668  , 1.819094   , 1.665016),
#            (0.005133  , 0.341237   , 2.894035),
#            (0.867954  , 17.024084  , 14.970213),
#            (0.138762  , 37.186903  , 47.98906 ),
#            (4.374349  , 42.335452  , 90.746475),
#            (21.725475 , 287.330462 , 372.991594),
#            (18.601216 , 673.81609  , 847.449375),
#            (164.298311, 1874.27352 , 1762.311388),
#            (624.972457, 5915.216558, 5787.904261),
#            (1641.81716, 7625.959698, 15549.16986),
#            (1129.07592, 4560.327895, 46697.68032),
#            (13712.6729, 92575.63579, 80125.00202),
#            (12241.42  , 379004.064 , 439136.1428),
#            (24268.6361, 781900.4736, 715880.6276),
#            (48061.4305, 939573.2658, 1000000    ),]


#Example 1  on page 15.
#TaskSet =[ (8,11,60), (12,20,170),(6,26,120),(7,80,110)] 

#Example 2  on page 15.
#TaskSet =[ (8,10,60), (12,19,170),(10,30,210),(6,36,190),(8,70,280),(7,90,320), ] 

#TaskSet = [ (1,6,6) , (1,8,8),  (11,20,20) , (4,4,30)  ] 

#TaskUtilization = Calc_Task_Utz(TaskSet)


#print(TaskUtilization)

#La = Algorithm_LA(TaskSet)
#print("LA:" + str(La))

#Lb = Algorithm_LB(TaskSet)
#print("LB:" + str(Lb) )

#QPA = Algorithm_QPA(TaskSet,La[3],Lb[1],TaskUtilization)
#print("QPA:"+ str(QPA))
