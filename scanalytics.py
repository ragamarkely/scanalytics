import numpy as np
import operator
from IPython.display import display
import pandas as pd
from pulp import *

#Clarke-Wright Savings Algorithm
class CWSA(object):
    '''
    argument:
    create an object with 'distances' attributes.
    self.distances[(from_node,to_node)] = distance
    output:
    '''
    def __init__(self):
        self.distances = {}

    def add_dist(self, from_node,to_node,distance):
        if from_node != 'DC' and to_node != 'DC':
            if from_node < to_node:
                self.distances[(from_node,to_node)] = distance
            else:
                self.distances[(to_node,from_node)] = distance
        elif from_node == 'DC':
            self.distances[(to_node,from_node)] = distance
        elif to_node == 'DC':
            self.distances[(from_node,to_node)] = distance

def CWSA_dist_matrix(cwsa):
    '''
    argument: cwsa object

    output:
    CWSA_mtx (numpy array): rows = from_node
                            columns = to_node
                            entries = distance (above diagonal element)
                                      diagonal and below diagonal elements are 0
    '''
    from_list = []
    dist_dict = cwsa.distances
    for from_node,to_node in dist_dict:
        if from_node not in from_list:
            from_list.append(from_node)
    from_list.sort()
    CWSA_mtx = np.zeros((len(from_list),len(from_list)+1))

    for from_node,to_node in dist_dict:
        if to_node != 'DC':
            CWSA_mtx[from_node-1,to_node-1] = dist_dict[(from_node,to_node)]
        else:
            CWSA_mtx[from_node-1,-1] = dist_dict[(from_node,to_node)]
    return CWSA_mtx

def CWSA_savings(cwsa):
    '''
    Given cwsa object, provide savings and distance table of
    argument:
    (object): cwsa object with complete distances attribute added by add_dist
              function
    output:
    CWSA_dict(dataframe): 1st column   = index
                          2nd column   = (from_node,to_node)
                          3rd column   = distance/cost saving for these nodes
    CWSA_mtx (dataframe): distance/cost (above diagonal element) and
                          saving (below diagonal element) of each pair of nodes
    '''
    CWSA_mtx = CWSA_dist_matrix(cwsa)
    CWSA_dict = {}
    for i in range(np.shape(CWSA_mtx)[0]):
        for j in range(i+1,np.shape(CWSA_mtx)[0]):
            saving = CWSA_mtx[i,-1] + CWSA_mtx[j,-1] - CWSA_mtx[i,j]
            CWSA_mtx[j,i] = saving
            CWSA_dict[(i+1,j+1)] = saving
    CWSA_list = sorted(CWSA_dict.items(),key=operator.itemgetter(1),
                       reverse=True)
    CWSA_savings_df = pd.DataFrame(CWSA_list)
    CWSA_df = pd.DataFrame(CWSA_mtx)
    return CWSA_df,CWSA_savings_df

def MPS_MILP(demand_forecast,setup_cost,holding_cost,init_inventory):
    '''
    MPS using Mixed Integer Linear Programming
    argument:
    demand_forecast (list): demand for each time period
    setup_cost (float): fixed cost of setting up manufacturing
    holding_cost (float): fixed cost of init_inventory
    init_inventory(float): initial inventory
    output:
    status (string): status of mixed integer linear programming
    inventory (list): inventory for each time period
    prod_schedule (list): production schedule for each time period
    total_cost (float): total cost of manufacturing and inventory
    '''

    #Problem statement
    prob = LpProblem('project',LpMinimize)

    #Variables
    prod_vars = ['Z'+str(i) for i in range(len(demand_forecast))]
    prod_vars_lp = LpVariable.dicts('Var',prod_vars,0,1,LpInteger)
    prod_qty_vars = ['Q'+str(i) for i in range(len(demand_forecast))]
    prod_qty_vars_lp = LpVariable.dicts('Var',prod_qty_vars,0,None)
    inventory_vars = ['I'+str(i) for i in range(len(demand_forecast))]
    inventory_vars_lp = LpVariable.dicts('Var',inventory_vars,0,None)

    # The objective function
    total_setup_cost = []
    for i in range(len(demand_forecast)):
        total_setup_cost.append(prod_vars_lp['Z'+str(i)]*setup_cost)

    total_holding_cost = []
    for i in range(len(demand_forecast)):
        total_holding_cost.append((inventory_vars_lp['I'+str(i)])*holding_cost)

    total_cost = total_setup_cost + total_holding_cost
    prob += lpSum(total_cost), 'Total Cost'

    #Inventory balance
    for i in range(1,len(demand_forecast)):
        prob += lpSum(prod_qty_vars_lp['Q'+str(i)]
                      -demand_forecast[i]
                      +inventory_vars_lp['I'+str(i-1)]
                      -inventory_vars_lp['I'+str(i)]) == 0

    prob += lpSum(prod_qty_vars_lp['Q0']
                  -demand_forecast[0]
                  +init_inventory
                  -inventory_vars_lp['I0']) == 0

    #Linking constraint
    M = np.sum(demand_forecast)
    for i in range(0,len(demand_forecast)):
        prob += M*prod_vars_lp['Z'+str(i)]-prod_qty_vars_lp['Q'+str(i)] >= 0

    #prob += prod_vars_lp['Z'+str(4)] == 1

    #Demand constraint
    for i in range(1,len(demand_forecast)):
        prob += prod_qty_vars_lp['Q'+str(i)]\
                +inventory_vars_lp['I'+str(i-1)]\
                -demand_forecast[i] >= 0

    prob += prod_qty_vars_lp['Q0']\
            +init_inventory\
            -demand_forecast[0] >= 0

    prob.writeLP('MPS MILP.lp')
    prob.solve()

    inventory = [0 for i in range(len(demand_forecast))]
    prod_schedule = [0 for i in range(len(demand_forecast))]
    for v in prob.variables():
        if v.name[4] == 'I': inventory[int(v.name[5:])] = v.varValue
        if v.name[4] == 'Q': prod_schedule[int(v.name[5:])] = v.varValue

    status = LpStatus[prob.status]
    total_cost = value(prob.objective)
    return status,inventory,prod_schedule,total_cost

def MPS_onetime(demand_forecast,setup_cost,holding_cost,init_inventory):
    '''
    MPS using One Time strategy
    argument:
    demand_forecast (list): demand for each time period
    setup_cost (float): fixed cost of setting up manufacturing
    holding_cost (float): fixed cost of init_inventory
    init_inventory(float): initial inventory
    output:
    inventory (list): inventory for each time period
    quantity (list): quantity of product manufactured for each time period
    total_cost (float): total cost of manufacturing and inventory
    '''
    prod_qty = (np.sum(demand_forecast)-init_inventory)
    prod_schedule = [0 for i in range(len(demand_forecast))]
    prod_schedule[0] = prod_qty
    inventory = []
    for time in range(len(demand_forecast)):
        if time == 0: inventory.append(init_inventory+prod_schedule[time]-demand_forecast[time])
        else:
            inventory.append(inventory[time-1]+prod_schedule[time]-demand_forecast[time])

    total_setup_cost = 0
    for i in prod_schedule:
        if i > 0: total_setup_cost += setup_cost

    total_holding_cost = 0
    for i in inventory:
        if i > 0: total_holding_cost += i*holding_cost

    total_cost = total_setup_cost + total_holding_cost

    return inventory,prod_schedule,total_cost

def MPS_chase(demand_forecast,setup_cost,holding_cost,init_inventory):
    '''
    MPS using Chase strategy.
    argument:
    demand_forecast (list): demand for each time period
    setup_cost (float): fixed cost of setting up manufacturing
    holding_cost (float): fixed cost of init_inventory
    init_inventory(float): initial inventory
    output:
    inventory (list): inventory for each time period
    quantity (list): quantity of product manufactured for each time period
    total_cost (float): total cost of manufacturing and inventory
    '''

    prod_schedule = []
    inventory = []

    #First check how many time period the current inventory can hold
    init_prod = 0
    while init_prod in range(len(demand_forecast)):
        if np.sum(demand_forecast[:init_prod + 1]) <= init_inventory:
            init_prod += 1
        else: break

    #Add 0 as the production during this period of using current inventory
    for idx in range(init_prod):
        if idx == 0:
            prod_schedule.append(0)
            inventory.append(init_inventory - demand_forecast[idx])
        else:
            prod_schedule.append(0)
            inventory.append(inventory[idx-1] - demand_forecast[idx])

    for idx in range(init_prod,len(demand_forecast)):
        if not inventory:
            prod_schedule.append(demand_forecast[idx])
            inventory.append(0)
        elif inventory[idx-1] > 0:
            prod_schedule.append(demand_forecast[idx] - inventory[idx-1])
            inventory.append(0)
        else:
            prod_schedule.append(demand_forecast[idx])
            inventory.append(0)

    total_setup_cost = 0
    for i in prod_schedule:
        if i > 0: total_setup_cost += setup_cost

    total_holding_cost = 0
    for i in inventory:
        if i > 0: total_holding_cost += i*holding_cost

    total_cost = total_setup_cost + total_holding_cost

    return inventory,prod_schedule,total_cost

def MPS_silvermeal(demand_forecast,setup_cost,holding_cost,init_inventory):
    '''
    MPS using Silver Meal strategy.
    argument:
    demand_forecast (list): demand for each time period
    setup_cost (float): fixed cost of setting up manufacturing
    holding_cost (float): fixed cost of init_inventory
    init_inventory(float): initial inventory
    output:
    inventory (list): inventory for each time period
    quantity (list): quantity of product manufactured for each time period
    total_cost (float): total cost of manufacturing and inventory
    '''

    prod_schedule = []
    inventory = []

    #First check how many time period the current inventory can hold
    init_prod = 0
    while init_prod in range(len(demand_forecast)):
        if np.sum(demand_forecast[:init_prod + 1]) <= init_inventory:
            init_prod += 1
        else: break

    #Add 0 as the production during this period of using current inventory
    for idx in range(init_prod):
        if idx == 0:
            prod_schedule.append(0)
            inventory.append(init_inventory - demand_forecast[idx])
        else:
            prod_schedule.append(0)
            inventory.append(inventory[idx-1] - demand_forecast[idx])

    ix = init_prod

    while ix in range(init_prod,len(demand_forecast)):
        cost = setup_cost
        if ix+1 == len(demand_forecast):
            prod_schedule.append(demand_forecast[ix])
            inventory.append(0)
            break
        next_cost = (setup_cost + demand_forecast[ix+1]*holding_cost)/2
        inventory_factor = [1*holding_cost]
        ix2 = 1
        while next_cost <= cost and ix+ix2 < len(demand_forecast):
            cost = next_cost
            ix2 += 1
            inventory_factor.append(ix2*holding_cost)
            next_cost = ((setup_cost + sum(i[0] * i[1]
                         for i in zip(demand_forecast[ix+1:ix+ix2+1],inventory_factor)))/(1+ix2))
        ix += ix2
        if not inventory:
            production = sum(demand_forecast[ix-ix2:ix])
            inventory.append(production-demand_forecast[ix-ix2])
        else:
            production = sum(demand_forecast[ix-ix2:ix])-inventory[-1]
            inventory.append(inventory[-1]+production-demand_forecast[ix-ix2])

        prod_schedule.append(production)

        for i in range(ix2-1):
            prod_schedule.append(0)
            inventory.append(inventory[-1]-demand_forecast[ix-ix2+i+1])

    total_setup_cost = 0
    for i in prod_schedule:
        if i > 0: total_setup_cost += setup_cost

    total_holding_cost = 0
    for i in inventory:
        if i > 0: total_holding_cost += i*holding_cost

    total_cost = total_setup_cost + total_holding_cost

    return inventory,prod_schedule,total_cost

def MPS_FOQ(Q,demand_forecast,setup_cost,holding_cost,init_inventory):
    '''
    MPS using Fixed Order Quantity strategy.
    argument:
    Q (float): economic order quantity
    demand_forecast (list): demand for each time period
    setup_cost (float): fixed cost of setting up manufacturing
    holding_cost (float): fixed cost of init_inventory
    init_inventory(float): initial inventory
    output:
    inventory (list): inventory for each time period
    quantity (list): quantity of product manufactured for each time period
    total_cost (float): total cost of manufacturing and inventory
    '''
    prod_schedule = []
    inventory = []

    #First check how many time period the current inventory can hold
    init_prod = 0
    while init_prod in range(len(demand_forecast)):
        if np.sum(demand_forecast[:init_prod + 1]) <= init_inventory:
            init_prod += 1
        else: break

    #Add 0 as the production during this period of using current inventory
    for idx in range(init_prod):
        if idx == 0:
            prod_schedule.append(0)
            inventory.append(init_inventory - demand_forecast[idx])
        else:
            prod_schedule.append(0)
            inventory.append(inventory[idx-1] - demand_forecast[idx])

    prod_schedule.append(Q)
    last_prod_time = init_prod
    if init_prod == 0:
        inventory.append(init_inventory+Q-demand_forecast[init_prod])
    else:
        inventory.append(inventory[-1]+Q-demand_forecast[init_prod])

    for time in range(init_prod+1,len(demand_forecast)):
        if inventory[-1] < demand_forecast[time]:
            prod_schedule.append(Q)
            inventory.append(inventory[-1]+Q-demand_forecast[time])
            last_prod_time = time
        else:
            prod_schedule.append(0)
            inventory.append(inventory[-1]-demand_forecast[time])

    if inventory[-1] > 0:
        prod_schedule[last_prod_time] -= inventory[-1]
        inventory[last_prod_time] = inventory[last_prod_time-1]+Q-inventory[-1]-demand_forecast[last_prod_time]
        for time in range(last_prod_time+1,len(demand_forecast)):
            inventory[time] = inventory[time-1]-demand_forecast[time]+prod_schedule[time]

    total_setup_cost = 0
    for i in prod_schedule:
        if i > 0: total_setup_cost += setup_cost

    total_holding_cost = 0
    for i in inventory:
        if i > 0: total_holding_cost += i*holding_cost

    total_cost = total_setup_cost + total_holding_cost
    return inventory,prod_schedule,total_cost

def MPS_POQ(t,demand_forecast,setup_cost,holding_cost,init_inventory):
    '''
    MPS using Periodic Order Quantity strategy.
    argument:
    t (float): interval time period between productions
    demand_forecast (list): demand for each time period
    setup_cost (float): fixed cost of setting up manufacturing
    holding_cost (float): fixed cost of init_inventory
    init_inventory(float): initial inventory
    output:
    inventory (list): inventory for each time period
    quantity (list): quantity of product manufactured for each time period
    total_cost (float): total cost of manufacturing and inventory
    '''

    prod_schedule = []
    inventory = []

    #First check how many time period the current inventory can hold
    init_prod = 0
    while init_prod in range(len(demand_forecast)):
        if np.sum(demand_forecast[:init_prod + 1]) <= init_inventory:
            init_prod += 1
        else: break

    #Add 0 as the production during this period of using current inventory
    for idx in range(init_prod):
        if idx == 0:
            prod_schedule.append(0)
            inventory.append(init_inventory - demand_forecast[idx])
        else:
            prod_schedule.append(0)
            inventory.append(inventory[idx-1] - demand_forecast[idx])

    Q = sum(demand_forecast[init_prod:init_prod+t])
    prod_schedule.append(Q)
    if init_prod == 0:
        inventory.append(init_inventory+Q-demand_forecast[init_prod])
    else:
        inventory.append(inventory[-1]+Q-demand_forecast[init_prod])
    last_prod_time = init_prod

    for time in range(init_prod+1,len(demand_forecast)):
        if time - last_prod_time < t:
            prod_schedule.append(0)
            inventory.append(inventory[-1]-demand_forecast[time])
        else:
            Q = sum(demand_forecast[time:time+t])
            prod_schedule.append(Q)
            inventory.append(inventory[-1]+Q-demand_forecast[time])
            last_prod_time = time

    if inventory[-1] > 0:
        prod_schedule[last_prod_time] -= inventory[-1]
        inventory[last_prod_time] = inventory[last_prod_time-1]+Q-inventory[-1]-demand_forecast[last_prod_time]
        for time in range(last_prod_time+1,len(demand_forecast)):
            inventory[time] = inventory.append(inventory[time-1]-demand_forecast[time])

    total_setup_cost = 0
    for i in prod_schedule:
        if i > 0: total_setup_cost += setup_cost

    total_holding_cost = 0
    for i in inventory:
        if i > 0: total_holding_cost += i*holding_cost

    total_cost = total_setup_cost + total_holding_cost
    return inventory,prod_schedule,total_cost
