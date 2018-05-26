import os
import re
import docplex.cp.utils_visu as visu
from docplex.cp.model import CpoModel, CpoStepFunction, INTERVAL_MIN, INTERVAL_MAX
import functools
import math
minutes_in_day = 480
number_of_employers = 3
numdetails = 12
WorkerNames = ["worker1", "worker2", "worker3"]
TaskNames = ["obtain_parts", "repair", "delivery"]
# minutes_on_repair - число минут, которые тратит работник на починку девайса
minutes_on_repair = [140, 80, 160, 120, 160, 120, 130, 100, 40, 140, 160, 60]
# minutes_on_obtain_parts - число минут, которые тратит работник на поиск запчастей
minutes_on_obtain_parts = [20, 30, 40, 50, 100, 10, 20, 40, 100, 10, 50, 20]
# minutes_on_delivery - число минут, которое уходит на доставку can be done in parallel
minutes_on_delivery = [120, 150, 170, 100, 140, 100, 150, 230, 100, 90, 180, 280]
# euro_penalty - число евро, составляющие штраф за откладку на день
euro_penalty = [100, 80, 120, 100, 80, 120, 120, 90, 100, 80, 150, 13]
mdl = CpoModel()
details = [mdl.interval_var(name="Detail{}".format(i + 1)) for i in range(numdetails)]
TaskNames_ids = {}
itvs_1 = {}
itvs_2 = {}
itvs_3 = {}
itvs = {}
#zadadim treh
for d in range(numdetails):
        _name = "obtain_parts1_{}".format(d + 1)
        itvs_1[(d, 0)] = mdl.interval_var(size=minutes_on_obtain_parts[d], name=_name, optional=True)
for d in range(numdetails):
        _name = "repair1_{}".format(d + 1)
        itvs_1[(d, 1)] = mdl.interval_var(size=minutes_on_repair[d], name=_name, optional=True)

for d in range(numdetails):
        _name = "obtain_parts2_{}".format(d + 1)
        itvs_2[(d, 0)] = mdl.interval_var(size=minutes_on_obtain_parts[d], name=_name, optional=True)
for d in range(numdetails):
        _name = "repair2_{}".format(d + 1)
        itvs_2[(d, 1)] = mdl.interval_var(size=minutes_on_repair[d], name=_name, optional=True)

for d in range(numdetails):
        _name = "obtain_parts3_{}".format(d + 1)
        itvs_3[(d, 0)] = mdl.interval_var(size=minutes_on_obtain_parts[d], name=_name, optional=True)
for d in range(numdetails):
        _name = "repair3_{}".format(d + 1)
        itvs_3[(d, 1)] = mdl.interval_var(size=minutes_on_repair[d], name=_name, optional=True)
#zadadim obshie
for d in range(numdetails):
        _name = "obtain_parts{}".format(d + 1)
        itvs[(d, 0)] = mdl.interval_var(size=minutes_on_obtain_parts[d], name=_name)
for d in range(numdetails):
        _name = "repair{}".format(d + 1)
        itvs[(d, 1)] = mdl.interval_var(size=minutes_on_repair[d], name=_name)
for d in range(numdetails):
        _name = "delivery{}".format(d + 1)
        itvs[(d, 2)] = mdl.interval_var(size=minutes_on_delivery[d], name=_name)
 #альтернатива между работниками
for i in range(numdetails):
    for j in range(2):
        mdl.add(mdl.alternative(itvs[(i, j)], [itvs_3[(i, j)], itvs_2[(i, j)], itvs_1[(i, j)]]))
#навесим последовательность TO DO для 1,2,3
#for h in range(numdetails):
#        mdl.add(mdl.end_before_start(itvs[(h, 1)], itvs[(h, 2)]))
#for h in range(numdetails):
#        mdl.add(mdl.end_before_start(itvs[(h, 0)], itvs[(h, 1)]))
#навесим последовательность жестко
for h in range(numdetails):
        mdl.add(mdl.end_before_start(itvs[(h, 1)], itvs[(h, 2)]))
for h in range(numdetails):
       mdl.add(mdl.end_before_start(itvs[(h, 0)], itvs[(h, 1)]))
for h in range(numdetails):
        mdl.add(mdl.start_at_end(itvs[(h, 1)], itvs[(h, 0)]))
#навесим принадлежность
for h in range(numdetails):
    mdl.add(mdl.span(details[h], [itvs[(h, t)] for t in range(3)]))
workers = {}
workers1 = {"worker1": mdl.sequence_var([itvs_1[(h, t)] for h in range(numdetails) for t in range(2)], types=[t for h in range(numdetails) for t in range(2)], name="worker1")}
workers.update(workers1)
workers2 = {"worker2": mdl.sequence_var([itvs_2[(h, t)] for h in range(numdetails) for t in range(2)], types=[t for h in range(numdetails) for t in range(2)], name="worker2")}
workers.update(workers2)
workers3 = {"worker3": mdl.sequence_var([itvs_3[(h, t)] for h in range(numdetails) for t in range(2)], types=[t for h in range(numdetails) for t in range(2)], name="worker3")}
workers.update(workers3)
deliveryworker = {"deliveryworker": mdl.sequence_var([itvs[(h, 2)] for h in range(numdetails)], types=[h for h in range(numdetails)], name="deliveryworker")}
workers.update(deliveryworker)
for w in WorkerNames:
    mdl.add(mdl.no_overlap(workers[w]))
mdl.add(mdl.minimize(mdl.sum(euro_penalty[i] * mdl.float_div(mdl.max([mdl.end_of(itvs[(i, 2)]) - 480, 0]), mdl.end_of(itvs[(i, 2)]) - 480 + mdl.equal(mdl.end_of(itvs[(i, 2)]) - 480, 0) )  for i in range(numdetails))))
#mdl.add(mdl.minimize(mdl.sum(euro_penalty[i] * mdl.float_div(mdl.max([mdl.end_of(itvs[(i, 2)]) - 480, 0]),mdl.max([mdl.end_of(itvs[(i, 2)]) - 480)) for i in range(numdetails)))))

#mdl.add(mdl.minimize(mdl.sum(euro_penalty[i] * mdl.max([mdl.step_at(mdl.end_of(itvs[(i, 2)]) - 480,1), 0]) for i in range(numdetails))))

#mdl.add(mdl.minimize(mdl.sum(euro_penalty[i] * mdl.float_div(mdl.max([mdl.exponent(mdl.end_of(itvs[(i, 2)]) - 480)-1, 0]), mdl.exponent(mdl.end_of(itvs[(i, 2)]) - 480)) for i in range(numdetails))))
#mdl.add(mdl.minimize(mdl.sum(euro_penalty[i] * mdl.float_div(mdl.max([mdl.exponent(mdl.power(mdl.end_of(itvs[(i, 2)]) - 480, 0.33))-1, 0]), mdl.exponent(mdl.power(mdl.end_of(itvs[(i, 2)]) - 480, 0.33))) for i in range(numdetails))))

#mdl.add(mdl.minimize(mdl.sum(euro_penalty[i] * mdl.presence_of(itvs[(i, 2)]) for i in range(numdetails))))
print("Solving model....")
msol = mdl.solve(FailLimit=100000, TimeLimit=10)
print("Solution: ")
msol.print_solution()

def compact(name):
    # Example: A31_M1_TP1 -> 31
    task, foo = name.split('_', 1)
    return task[1:]

def showsequence(s,name):
    vs = s.get_value()
    starts=[]
    ends=[]
    nms=[]
    for i,v in enumerate(vs):
        if v.end<minutes_in_day:
            starts.append(v.start)
            ends.append(v.end)
            nm=v.get_name().replace("1_","").replace("2_","").replace("3_","")
            nms.append(nm)
          
    for i,s in enumerate(starts):
        if msol.get_var_solution("delivery"+re.findall('(\d+)', nms[len(starts)-1])[0]).get_end() > 480:
            nms.pop()
            ends.pop()
            starts.pop()    
    visu.sequence(name=name,intervals=[(s,ends[i],i,nms[i]) for i,s in enumerate(starts) ])  

def showdelivery():
    starts=[]
    ends=[]
    nms=[]
    color = []
    intervals=[(msol.get_var_solution("delivery"+str(i+1)).get_start(), msol.get_var_solution("delivery"+str(i+1)).get_end(), i, msol.get_var_solution("delivery"+str(i+1)).get_name()) for i in range(numdetails) if msol.get_var_solution("delivery"+str(i+1)).get_end()<minutes_in_day]
    for i,interval in enumerate(intervals):
        starts.append(interval[0])   
        ends.append(interval[1])
        color.append(interval[2])
        nms.append(interval[3])
    n = 1 
    while n < len(starts):
      for i in range(len(starts)-n):
          if starts[i] > starts[i+1]:
               starts[i],starts[i+1] = starts[i+1],starts[i]
               ends[i],ends[i+1] = ends[i+1],ends[i]
               color[i],color[i+1] = color[i+1],color[i]
               nms[i],nms[i+1] = nms[i+1],nms[i]
      n += 1
    starts_res=[starts[0]]
    ends_res=[ends[0]]
    nms_res=[nms[0]]
    color_res = [color[0]]
    used = [starts[0]]
    p = 0
    for y,t in enumerate(starts):
        for i,s in enumerate(starts):
            k = len(ends_res)
            for j,r in enumerate(ends_res):
                if s >= r:
                    p = p + 1
            if  (p == k) & (not (i in used)):
                starts_res.append(s)
                ends_res.append(ends[i])
                nms_res.append(nms[i])
                color_res.append(color[i])
                used.append(s)
                p = 0
        print(starts_res, ends_res, nms_res)
        print('----')    
        visu.sequence(name='delivery',intervals=[(starts_res[i],ends_res[i],color_res[i],nms_res[i]) for i,s in enumerate(starts_res) ])
        if len(used) == len(starts):
            break            
        
        for e,w in enumerate(starts):
              if not (w in used):
                  print(used)
                  starts_res=[starts[e]]
                  ends_res=[ends[e]]
                  nms_res=[nms[e]]
                  color_res = [color[e]]
                  used.append(w)
                  break
    
    
    
    
    #visu.sequence(name = 'Delivery1',intervals = intervals ) #if msol.get_var_solution("delivery"+str(i+1)).get_end() <= 480])
#if msol.get_var_solution("delivery"+str(i+1)).get_end() <= 480])
    #print(sum([euro_penalty[i] * max([msol.get_var_solution("delivery"+str(i+1)).get_end() - 480, 0]) for i in range(numdetails)]))
    #print(sum([euro_penalty[i] * max([math.exp(msol.get_var_solution("delivery"+str(i+1)).get_end() - 480) - 1, 0])/math.exp(msol.get_var_solution("delivery"+str(i+1)).get_end() - 480) for i in range(numdetails)]))
    #for i in range(12):
        #print(1*(msol.get_var_solution("delivery"+str(i+1)).get_end() - 480))
    
    
if msol and visu.is_visu_enabled():
    
    #visu.sequence(name='Machine1',intervals=[(0,10,1,'Job1'),(15,35,2,'Job2')],transitions=[(10,13)])    
    showdelivery()
    showsequence(msol.get_var_solution(workers["worker1"]),"worker1")
    showsequence(msol.get_var_solution(workers["worker2"]),"worker2")
    showsequence(msol.get_var_solution(workers["worker3"]),"worker3")
    #showsequence(msol.get_var_solution(workers["deliveryworker"]),"deliveryworker")    
    #visu.interval(starts)
    visu.show()
    
    
    