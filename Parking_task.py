from docplex.cp.model import CpoModel
import docplex.cp.utils_visu as visu
import random
e_x,e_y = [5],[0]
SIZE_X = 10
SIZE_Y = 10
Nblack =  544
NWhite = SIZE_X * SIZE_Y - Nblack - 1
calc_white = 0
EXITS_X = list(e_x)
EXITS_Y = list(e_y)
mdl = CpoModel()
mass_v_str = []
mass_v = []
for i in range(SIZE_X):
    for j in range(SIZE_Y):
        if [i,j] != [*EXITS_X, *EXITS_Y]:
            v = mdl.integer_var(domain=(0,1), name='sq_' + str(i) + '_' + str(j))
        else:
            v = mdl.integer_var(domain=(0,0), name='sq_' + str(i) + '_' + str(j))
        mass_v_str.append(v)
    mass_v.append(mass_v_str)
    mass_v_str = []
def checkin(indexes, mas):
    try:
      ind =  mas.index(indexes)
      return 0
    except:
      return 1
def get_neigh(mass,  i, j):
    Y_SIZE = len(mass[0])
    X_SIZE = len(mass)
    Result = []
    i_use1 = i + 1
    j_use1 = j + 1
    i_use2 = i - 1
    j_use2 = j - 1
    if i - 1 < 0:
        i_use2 = i + 1  
    if i + 1 >= X_SIZE:
        i_use1 = i - 1 
    if j + 1 >= Y_SIZE:
        j_use1 = j - 1
    if j - 1 < 0:
        j_use2 = j + 1  
    if j_use2 != j_use1:
            Result.append(mass[i][j_use2])
            Result.append(mass[i][j_use1])
    else:
            Result.append(mass[i][j_use1])
    if i_use1 != i_use2:
            Result.append(mass[i_use1][j])
            Result.append(mass[i_use2][j])
    else:
            Result.append(mass[i_use2][j])
    return Result
def get_or_on_neigh(neigh):
    if len(neigh) == 2:
        return (mdl.equal(neigh[0],0) | mdl.equal(neigh[1],0))
    elif len(neigh) == 3:
        return (mdl.equal(neigh[0],0) | mdl.equal(neigh[1],0) | mdl.equal(neigh[2],0))
    elif len(neigh) == 4:
        return (mdl.equal(neigh[0],0) | mdl.equal(neigh[1],0) | mdl.equal(neigh[2],0) | mdl.equal(neigh[3],0))
    else:
       raise IndexError('Что-то пошло не так') 
        
for i in range(SIZE_X):
    for j in range(SIZE_Y):
        neigh = get_neigh(mass_v,  i, j)
        expr = mdl.if_then(mdl.equal(mass_v[i][j],1), get_or_on_neigh(neigh))
        mdl.add(expr)
        
def get_neighbours_with_checked(mass, i, j, checked):
    Y_SIZE = len(mass[0])
    X_SIZE = len(mass)
    Result = []
    i_use1 = i + 1
    j_use1 = j + 1
    i_use2 = i - 1
    j_use2 = j - 1
    if i - 1 < 0:
        i_use2 = i + 1  
    if i + 1 >= X_SIZE:
        i_use1 = i - 1 
    if j + 1 >= Y_SIZE:
        j_use1 = j - 1
    if j - 1 < 0:
        j_use2 = j + 1  
    check_j_use2 = checkin([i, j_use2], checked)
    check_j_use1 = checkin([i, j_use1], checked)
    check_i_use1 = checkin([i_use1, j], checked)
    check_i_use2 = checkin([i_use2, j], checked)
    if i == X_SIZE - 2 and j == Y_SIZE -2:
        Result.append(mass[i+1][j])
    elif i == X_SIZE - 1 and j == Y_SIZE -1:
        Result.append(mass[i-1][j])
    elif i == X_SIZE - 1 and j == Y_SIZE -2:
        Result.append(mass[i][j+1])
    elif i == X_SIZE - 2 and j == Y_SIZE -1:
        Result.append(mass[i][j-1])
    else:
        if j_use2 != j_use1:
            if check_j_use2:
                Result.append(mass[i][j_use2])
            if check_j_use1:
                Result.append(mass[i][j_use1])
        else:
            if check_j_use1:
                Result.append(mass[i][j_use1])
        if i_use1 != i_use2:
            if check_i_use1:
                Result.append(mass[i_use1][j])
            if check_i_use2:
                Result.append(mass[i_use2][j])
        else:
            if check_i_use2:
                Result.append(mass[i_use2][j])
    return Result  
def get_or_on_neigh_with_checked(neigh):
    if len(neigh) == 1:
        return mdl.equal(neigh[0],0)
    elif len(neigh) == 2:
        return mdl.equal(neigh[0],0) | mdl.equal(neigh[1],0)
    else:
       raise IndexError('Что-то пошло не так')      
checked = []
expr_all = 0
for i in range(SIZE_X):
    for j in range(SIZE_Y):
        neigh = get_neighbours_with_checked(mass_v,  i, j, checked)
        checked.append([i,j])
        if len(neigh) != 0:
            expr = mdl.if_then(mdl.equal(mass_v[i][j],0), get_or_on_neigh_with_checked(neigh))
            expr_all = mdl.sum([mdl.logical_not(expr), expr_all])
        
mdl.add(mdl.less_or_equal(expr_all, 1))
        
mdl.maximize(mdl.sum([mass_v[i][j] for i in range(SIZE_X) for j in range(SIZE_Y)]))
#mdl.add(mdl.equal(mdl.sum([mass_v[i][j] for i in range(SIZE_X) for j in range(SIZE_Y)]), Nblack))
msol = mdl.solve(FailLimit=100000000, TimeLimit=10, LogVerbosity="Terse",  # use "Quiet" or "Terse"
                 RandomSeed=random.randint(1, 1000))
#msol.print_solution()

print(msol.get_solver_log())
if msol and visu.is_visu_enabled():
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from matplotlib.patches import Polygon
    fig, ax = plt.subplots()
    for i in range(SIZE_X):
        for j in range(SIZE_Y):
            # plt.plot((0, 0), (0, SIZE_Y), (min([SIZE_X, SIZE_Y]),min([SIZE_X, SIZE_Y])), (SIZE_X, 0))
            plt.plot([i, i, min([i + 1, SIZE_X]), min([i + 1, SIZE_X])],
                     [j, min([j + 1, SIZE_Y]), min([j + 1, SIZE_Y]), j])
            val = msol.get_var_solution(mass_v[i][j]).get_value()
            if val == 0:
                fc1 = '0.8'
            else:
                fc1 = '0.2'
            poly = Polygon([(i, j), (i, j+1), (i+1, j+1), (i+1, j)], fc = fc1)
            ax.add_patch(poly)
   # ax.add_patch(poly)
    plt.margins(0)
    plt.show()  
