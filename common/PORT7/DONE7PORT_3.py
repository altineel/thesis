import random
import time
import os
from common.PORT7.properties7 import *
simulation_name = '7PORT_3'

param_values = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [False, True],
    'EXP_CONST': [500000,750000],
    'MAX_ITERATION': [500, 1000],
    'EXP_CONST_DECAY': [0.9998, 0.9980],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6, 11],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [4, 8],
    'HEURISTIC': [True],
    'FUEL_CAPACITY': 150,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [True]
}
FIXED_BUNKERING_COSTS = [14000, 10000, 2000, 7000, 4000, 3000, 2000]
EXPECTED_BUNKERING_COSTS = [4300, 6500, 4600, 4900, 6000, 6200, 4800]
PRICE_PERCENTAGES = [0.70, 0.9, 1, 1.1, 1.3]
PRICE_DISTRIBUTION = 'multinomial'
STOCH_BUNKERING_COSTS, PRICE_SCENARIOS = generate_prices_n_scenarios(p0=EXPECTED_BUNKERING_COSTS,s0=[1], sn=PRICE_PERCENTAGES)
STOCH_PROBS = [1 / len(STOCH_BUNKERING_COSTS)] * len(STOCH_BUNKERING_COSTS)

PRICE_STDS = None
#, 500, 1000, 2000, 3000, 6000, 10000
#MIN_REWARD_SOME_VISITED

param_values2 = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [True],
    'EXP_CONST': [500000,750000],
    'MAX_ITERATION': [1000, 3000],
    'EXP_CONST_DECAY': [0.9998, 0.9990],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [6],
    'HEURISTIC': [True],
    'FUEL_CAPACITY': 150,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [False]
}

param_values3 = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [True],
    'EXP_CONST': [1000000],
    'MAX_ITERATION': [3000],
    'EXP_CONST_DECAY': [0.9987],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [6],
    'HEURISTIC': [True],
    'FUEL_CAPACITY': 150,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [False]
}