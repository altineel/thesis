import random
import time
import os
from common.PORT4.properties4 import *
FIXED_BUNKERING_COSTS  = [3200,7400,3800,4100]
PRICE_PERCENTAGES = [0.75,0.85, 1,1.15, 1.25]
EXPECTED_BUNKERING_COSTS = [1500,950,1800,2300]
STOCH_BUNKERING_COSTS, PRICE_SCENARIOS = generate_prices_n_scenarios(p0=EXPECTED_BUNKERING_COSTS,
                                                       s0=[1],
                                                       sn=PRICE_PERCENTAGES)
STOCH_PROBS = [1 / len(STOCH_BUNKERING_COSTS)] * len(STOCH_BUNKERING_COSTS)
PRICE_STDS = None
simulation_name = '4PORT'
param_values = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [False, True],
    'EXP_CONST': [1000, 10000, 25000, 50000, 100000, 500000, 1000000],
    'MAX_ITERATION': [20, 50, 100, 200, 500, 1000],
    'EXP_CONST_DECAY': [0.9998, 0.9990],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [4],
    'HEURISTIC': [True, False],
    'FUEL_CAPACITY': 50,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [True, False]
}
param_values2 = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [True],
    'EXP_CONST': [1000, 10000, 25000, 50000, 100000, 500000, 1000000],
    'MAX_ITERATION': [3000],
    'EXP_CONST_DECAY': [0.9998, 0.9990],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [4],
    'HEURISTIC': [True, False],
    'FUEL_CAPACITY': 50,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [True, False]
}