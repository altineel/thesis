import random
import time
import os
from common.PORT7.properties7 import *
simulation_name = '7PORT'

param_values = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [False, True],
    'EXP_CONST': [25000, 50000, 100000, 500000,750000, 1000000, 25000000],
    'MAX_ITERATION': [20, 50, 100, 200, 500, 1000],
    'EXP_CONST_DECAY': [0.9998, 0.9990],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [6],
    'HEURISTIC': [True],
    'FUEL_CAPACITY': 150,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [True, False]
}
FIXED_BUNKERING_COSTS = [14000, 10000, 2000, 7000, 4000, 3000, 2000]
EXPECTED_BUNKERING_COSTS = [3500, 6000, 4200, 5100, 6300, 5700, 4800]
PRICE_PERCENTAGES = [0.70, 0.85, 1, 1.15, 1.3]
PRICE_DISTRIBUTION = 'multinomial'
STOCH_BUNKERING_COSTS, PRICE_SCENARIOS = generate_prices_n_scenarios(p0=EXPECTED_BUNKERING_COSTS,s0=[1], sn=PRICE_PERCENTAGES)
STOCH_PROBS = [1 / len(STOCH_BUNKERING_COSTS)] * len(STOCH_BUNKERING_COSTS)

PRICE_STD = None
#, 500, 1000, 2000, 3000, 6000, 10000
#MIN_REWARD_SOME_VISITED

param_values2 = {
    'DECREASING_ITER' : [False],
    'EARLY_STOP': [True],
    'EXP_CONST': [25000, 50000, 100000, 500000,750000, 1000000, 25000000],
    'MAX_ITERATION': [3000],
    'EXP_CONST_DECAY': [0.9998, 0.9990],
    'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE': [6],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [6],
    'HEURISTIC': [True],
    'FUEL_CAPACITY': 150,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [True, False]
}