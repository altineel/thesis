from common.PORT7.properties7 import *

import random
import time
import os
simulation_name = '7PORT_Normal_2'
param_values = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [False, True],
    'EXP_CONST': [25000, 50000, 100000, 250000, 500000, 1000000],
    'MAX_ITERATION': [50, 100, 200, 500, 1000],
    'EXP_CONST_DECAY': [0.9998, 0.999],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6, 11],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [6, 8],
    'HEURISTIC': [False, True],
    'FUEL_CAPACITY': 150,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [True, False]
}
EXPECTED_BUNKERING_COSTS = [5000, 6000, 2000, 5500, 8000, 4500, 3500]
FIXED_BUNKERING_COSTS = [14000, 10000, 2000, 7000, 4000, 3000, 2000]
PRICE_DISTRIBUTION = 'discrete_normal'
STOCH_PROBS = None
STOCH_BUNKERING_COSTS = None
PRICE_PERCENTAGES = None
PRICE_STD = [1250, 1250, 675, 1250, 1250, 1150,1050]
#, 500, 1000, 2000, 3000, 6000, 10000
#MIN_REWARD_SOME_VISITED
