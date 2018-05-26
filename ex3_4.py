# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 18:31:28 2018

@author: VedMedk0
"""

import re
import os
import re
import random
import docplex.cp.utils_visu as visu
from docplex.cp.model import CpoModel, CpoStepFunction, INTERVAL_MIN, INTERVAL_MAX
import functools
import math
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# now, to clear the screen
cls()
players_compositions=[[1,1,0,1,0,1,1,0,1],
                      [1,1,0,1,1,1,0,1,0],
                      [1,1,0,0,0,0,1,1,0],
                      [1,0,0,0,1,1,0,0,1],
                      [0,0,1,0,1,1,1,1,0]]
compositions_players=[[1,1,1,1,0],
                      [1,1,1,0,0],
                      [0,0,0,0,1],
                      [1,1,0,0,0],
                      [0,1,0,1,1],
                      [1,1,0,1,1],
                      [1,0,1,0,1],
                      [0,1,1,0,1],
                      [1,0,0,1,0]]
waittimes=[2,4,1,3,3,2,5,7,6]

mdl = CpoModel()

numplayers=5
numcompositions=9
def sumcol(ind,mtrx,numcols):
    return sum([mtrx[i][ind] for i in range(numplayers)])
def checksymmetries(mtrx, numcols):
    sum_col = []
    checked_cur = []
    checked = []
    ind_col = []
    for i in range(numcols):
        pr = sumcol(i,mtrx,numcols)
        try:
            ind = sum_col.index(pr)
        except:
            ind = -1
        if ind != -1:
            checked_cur = [ind_col[ind],i]
            checked.append(checked_cur)
            sum_col.pop(ind)
            ind_col.pop(ind)
        else:
            sum_col.append(pr)
            ind_col.append(i)
    print('found symmetries: ')
    print(checked)
    print('without symmetry: ')
    print(ind_col)
    return checked

#list of intervals
compositions=[mdl.interval_var(size=waittimes[i], end = [0,33], start=[0,33], name="song_"+str(i+1)) for i in range(numcompositions)]
domain=mdl.sequence_var([compositions[i] for i in range(numcompositions)], types=[t for t in range(numcompositions)], name="domain")
mdl.add(mdl.no_overlap(domain))
checked = checksymmetries(players_compositions, 9)

for i,c in enumerate(checked):
    if i ==2:
        mdl.add(mdl.start_before_start(compositions[c[1]],compositions[c[0]]))
    else:
        mdl.add(mdl.start_before_start(compositions[c[0]],compositions[c[1]]))
ENDS = []
STARTS = []
WAITNESS=[]
for k in range(numplayers):
    for j in range(numcompositions):
        print(players_compositions[k][j])
        #print(mdl.name_of(songs[k][j]))
        ENDS.append(mdl.end_of(compositions[j])*players_compositions[k][j])
        #STARTS.append(mdl.sum([mdl.times(mdl.start_of(songs[k][j] ),mdl.sum([100*mdl.equal(players_compositions[k][j],0),players_compositions[k][j]]) ), 100*mdl.times(mdl.equal(mdl.start_of(songs[k][j]),0),mdl.equal(players_compositions[k][j],0))]))
        STARTS.append(mdl.times(mdl.start_of(compositions[j] ),1000*mdl.equal(players_compositions[k][j],0)+ players_compositions[k][j]))
    MAX=mdl.max(ENDS)
    MIN=mdl.min(STARTS)
    print(-sum([waittimes[i]*players_compositions[k][i] for i in range(numcompositions)]))
    WAITNESS.append(mdl.sum([MAX,-MIN,-sum([waittimes[i]*players_compositions[k][i] for i in range(numcompositions)])]))
EXPR=mdl.sum(WAITNESS)
    
    
#mdl.add(mdl.minimize(EXPR))
mdl.add(mdl.minimize(mdl.sum([*[ mdl.max([ mdl.end_of(compositions[i])*players_compositions[k][i] for i in range(numcompositions)]) for k in range (numplayers)],
                              *[-mdl.min([mdl.times(mdl.start_of(compositions[j]),1000*mdl.equal(players_compositions[k][j],0)+ players_compositions[k][j]) + 100*mdl.times(mdl.equal(mdl.start_of(compositions[j]),0),mdl.equal(players_compositions[k][j],0)) for j in range(numcompositions)]) for k in range (numplayers)],
                              -92])))
        #[mdl.max(ENDS) for k in range(numplayers)]
        

mdl.write_information()
print("Solving model....")
#mdl.run_seeds(3)

msol = mdl.solve(FailLimit=100000000, TimeLimit=30, LogVerbosity="Terse", # use "Quiet" or "Terse"
                 RandomSeed=random.randint(1, 1000), OptimalityTolerance=1.0, RelativeOptimalityTolerance=1.0)
print(msol.get_solver_log())
print("Solution: ")
msol.print_solution()




def showsequence(s,name):
    vs = s.get_value()
    starts=[]
    ends=[]
    nms=[]
    colors = []
    print(name)
    for i,v in enumerate(vs):
            starts.append(v.start)
            ends.append(v.end)
            nms.append(v.get_name())
            colors.append(i)
            
    visu.sequence(name=name,intervals=[(st,ends[i],colors[i],nms[i]) for i,st in enumerate(starts) ])  		
    for j in range(numplayers):
        starts2=[]
        ends2=[]
        nms2=[]
        colors2 = []
        for i,v in enumerate(vs):
            if players_compositions[j][int(nms[i][-1])-1] != 0:
                starts2.append(v.start)
                ends2.append(v.end)
                nms2.append(v.get_name())
                colors2.append(colors[i])
        visu.sequence(name='musician' + str(j+1),intervals=[(st,ends2[i],colors2[i],nms2[i]) for i,st in enumerate(starts2) ])
if msol and visu.is_visu_enabled():
    mas2 = []
    #visu.sequence(name='Machine1',intervals=[(0,10,1,'Job1'),(15,35,2,'Job2')],transitions=[(10,13)])    
    showsequence(msol.get_var_solution(domain),"songs order")
    #showsequence(msol.get_var_solution(workers["deliveryworker"]),"deliveryworker")    
    #visu.interval(starts)
    visu.show()



