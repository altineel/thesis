import random
import time
import os
from common.PORT7.properties7 import *
simulation_name = '7PORT_1'

# param_values = {
#     'DECREASING_ITER' : [False],
#     'EARLY_STOP': [True],
#     'EXP_CONST': [25000, 50000, 100000, 500000,750000, 1000000, 25000000],
#     'MAX_ITERATION': [50, 100, 200, 500, 1000],
#     'EXP_CONST_DECAY': [0.9998, 0.9990],
#     'ALGORITHM': ['DPWSolver', 'NAIVE', 'ProgressiveWideningSolver'],
#     'OPT_ACT': ['MIN_REWARD'],
#     'MIN_SET_SIZE': [6],
#     'DPW_ALPHA': [0.4],
#     'DPW_EXP': [6],
#     'HEURISTIC': [True],
#     'FUEL_CAPACITY': 150,
#     'SIMULATION_NUMBER': 20,
#     'DPW_PROBABILISTIC': [False]
# }

param_values = {
    'DECREASING_ITER' : [True],
    'EARLY_STOP': [False],
    'EXP_CONST': [100000, 500000,750000],
    'MAX_ITERATION': [500],
    'EXP_CONST_DECAY': [0.9998, 0.9990],
    'ALGORITHM': ['DPWSolver'],
    'OPT_ACT': ['MIN_REWARD', 'MIN_REWARD_SOME_VISITED'],
    'MIN_SET_SIZE': [6],
    'DPW_ALPHA': [0.4, 0.8],
    'DPW_EXP': [10],
    'HEURISTIC': [True],
    'FUEL_CAPACITY': 150,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [False, True]
}
FIXED_BUNKERING_COSTS = [7000, 5000, 1000, 3500, 2000, 1500, 1000]
EXPECTED_BUNKERING_COSTS = [5000, 6000, 2000, 5500, 8000, 4500, 3500]
PRICE_PERCENTAGES = [0.70, 0.85, 1, 1.15, 1.3]
PRICE_DISTRIBUTION = 'multinomial'
STOCH_BUNKERING_COSTS, PRICE_SCENARIOS = generate_prices_n_scenarios(p0=EXPECTED_BUNKERING_COSTS,s0=[1], sn=PRICE_PERCENTAGES)
STOCH_PROBS = [1 / len(STOCH_BUNKERING_COSTS)] * len(STOCH_BUNKERING_COSTS)
PRICE_STDS = None

#, 500, 1000, 2000, 3000, 6000, 10000
#MIN_REWARD_SOME_VISITED