# scanalytics

![Plot](scanalytics%20wallpaper.png)

scanalytics is a Python implementation of several analyses used in Supply Chain
Analytics & Design. I wrote this program to programmatically
solve problems encountered in some Supply Chain Analytics and Design class
assignments, thus minimizing tedious manual work on spreadsheet.

# Table of Content
* Clarke-Wright Savings Algorithm for Vehicle Routing Problem
* Mixed Integer Linear Programming for Master Production Schedule
* One Time Run for Master Production Schedule
* Lot for Lot (Chase) for Master Production Schedule
* Silver Meal for Master Production Schedule
* Fixed Order Quantity (FOQ) for Master Production Schedule
* Periodic Order Quantity (POQ) for Master Production Schedule


## Clarke-Wright Savings Algorithm

#### Example

```
from scanalytics import *
from IPython.display import display
cwsa = CWSA()
cwsa.add_dist(1,2,16.3)
cwsa.add_dist(1,3,16.5)
cwsa.add_dist(1,4,20)
cwsa.add_dist(1,5,19.6)
cwsa.add_dist(1,6,17.9)
cwsa.add_dist(1,7,9.3)
cwsa.add_dist(1,'DC',12.7)
cwsa.add_dist(2,3,7.2)
cwsa.add_dist(2,4,14.9)
cwsa.add_dist(2,5,16.6)
cwsa.add_dist(2,6,16.6)
cwsa.add_dist(2,7,12.7)
cwsa.add_dist(2,'DC',11.5)
cwsa.add_dist(3,4,8.9)
cwsa.add_dist(3,5,10.1)
cwsa.add_dist(3,6,11)
cwsa.add_dist(3,7,10.8)
cwsa.add_dist(3,'DC',9.8)
cwsa.add_dist(4,5,7.3)
cwsa.add_dist(4,6,13.4)
cwsa.add_dist(4,7,19.1)
cwsa.add_dist(4,'DC',17.5)
cwsa.add_dist(5,6,12.9)
cwsa.add_dist(5,7,16.4)
cwsa.add_dist(5,'DC',16.1)
cwsa.add_dist(6,7,9.4)
cwsa.add_dist(6,'DC',17.4)
cwsa.add_dist(7,'DC',3.6)

CWSA_df, CWSA_savings_df = CWSA_savings(cwsa)
display(CWSA_df)
display(CWSA_savings_df)
```

## Mixed Integer Linear Programming for Master Production Schedule

#### Example

```
from scanalytics import *
from IPython.display import display

demand_forecast = [1040,240,480,400,1600,4400,1440,1120,480,400,800,2000]
setup_cost = 1822.5
holding_cost = 0.3375
init_inventory = 0

status,inventory,prod_schedule,total_cost = MPS_MILP(demand_forecast,setup_cost,holding_cost,init_inventory)
```

## One Time Run for Master Production Schedule

#### Example

```
from scanalytics import *
from IPython.display import display

demand_forecast = [1040,240,480,400,1600,4400,1440,1120,480,400,800,2000]
setup_cost = 1822.5
holding_cost = 0.3375
init_inventory = 0

inventory,prod_schedule,total_cost = MPS_onetime(demand_forecast,setup_cost,holding_cost,init_inventory)
```

## Lot for Lot (Chase) for Master Production Schedule

#### Example

```
from scanalytics import *
from IPython.display import display

demand_forecast = [1040,240,480,400,1600,4400,1440,1120,480,400,800,2000]
setup_cost = 1822.5
holding_cost = 0.3375
init_inventory = 0

inventory,prod_schedule,total_cost = MPS_chase(demand_forecast,setup_cost,holding_cost,init_inventory)
```

## Silver Meal for Master Production Schedule

#### Example

```
from scanalytics import *
from IPython.display import display

demand_forecast = [1040,240,480,400,1600,4400,1440,1120,480,400,800,2000]
setup_cost = 1822.5
holding_cost = 0.3375
init_inventory = 0

inventory,prod_schedule,total_cost = MPS_silvermeal(demand_forecast,setup_cost,holding_cost,init_inventory)
```

## Fixed Order Quantity for Master Production Schedule

#### Example

```
from scanalytics import *
from IPython.display import display

demand_forecast = [1040,240,480,400,1600,4400,1440,1120,480,400,800,2000]
setup_cost = 1822.5
holding_cost = 0.3375
init_inventory = 0
Q = 3600

inventory,prod_schedule,total_cost = MPS_FOQ(Q, demand_forecast,setup_cost,holding_cost,init_inventory)
```

# Requirement
* Python 3
* NumPy
* Pandas
* PuLP

Alternatively, if you are using Anaconda, activate the environment in
command prompt or terminal as follows.

```
conda env create -f scanalytics.yaml
source activate scanalytics
```

# Installation
Clone this repository as follows.

`git clone https://github.com/ragamarkely/scanalytics.git`

# Notes
This is by no means a complete collection of all analyses. There are other
repositories that cover Python implementation other analyses, e.g. [Dijkstra's Algorithm](https://gist.github.com/econchick/4666413).
