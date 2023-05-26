from common.PORT7.properties7 import *

import random
import time
import os

simulation_name = '7PORT_Speed_Normal_1'

EXPECTED_BUNKERING_COSTS = [50, 60, 20, 55, 80, 45, 35]
FIXED_BUNKERING_COSTS = [14, 10, 20, 70, 40, 30, 20]
PRICE_DISTRIBUTION = 'discrete_normal'
STOCH_PROBS = None
STOCH_BUNKERING_COSTS = None
PRICE_PERCENTAGES = None
FUEL_COST_METHOD = 'NONLINEAR'
PRICE_STD = [3, 5, 7, 9, 4, 8, 5]
USE_SPEED = True
param_values = {
    'DECREASING_ITER': [False],
    'EARLY_STOP': [True],
    'EXP_CONST': [20, 50, 100, 500, 1000, 5000, 10000],
    'MAX_ITERATION': [20, 50, 100, 200, 500, 1000],
    'EXP_CONST_DECAY': [0.9998, 0.9990],
    'ALGORITHM': ['DPWSolver', 'ProgressiveWideningSolver'],
    'OPT_ACT': ['MIN_REWARD'],
    'MIN_SET_SIZE_REFUEL': [6],
    'MIN_SET_SIZE_SPEED': [5, 8],
    'DPW_ALPHA': [0.2, 0.4],
    'DPW_EXP': [6],
    'HEURISTIC': [True, False],
    'FUEL_CAPACITY': 1500,
    'SIMULATION_NUMBER': 20,
    'DPW_PROBABILISTIC': [True]
}

REGULAR_SPEED = 10
EXP_TRAVEL_TIME = np.array([DIST_MAT[i][i + 1] if i < len(DIST_MAT) - 1 else DIST_MAT[i][0] for i in range(len(DIST_MAT))]) / REGULAR_SPEED
CUM_TRAVEL_TIME = np.cumsum(EXP_TRAVEL_TIME)
REL_TIME_DIFFS = np.array(
    [[-0.5, 1.5], [-0.5, 1], [-3, 2], [-3, 2], [-3, 2], [-3, 2], [-3, 2]])
EXP_ARRIV_TIME_RNG = [[x[0] + x[1][0], x[0] + x[1][1]] for x in zip(CUM_TRAVEL_TIME, REL_TIME_DIFFS)]
INITIAL_SPEED = 1

EARLY_ARRIVAL_PENALTY = 0
MAX_SPEED = 30
LATE_ARRIVAL_PENALTY = 50.0
MIN_SPEED = 1

if USE_SPEED:
    assert len(EXP_ARRIV_TIME_RNG) == len(ROUTE_SCHEDULE) - 1, "Assert: ensure there are enough time constraints per port in the schedule."


def save_configs(name, simulation_name=None, **kwargs):
    variables = {}
    variables['DIST_MAT'] = DIST_MAT
    # variables['EARLY_STOP'] = EARLY_STOP
    variables['EPSILON'] = EPSILON
    variables['FUEL_CAPACITY'] = FUEL_CAPACITY
    variables['LAST_ITERATIONS_NUMBER'] = LAST_ITERATIONS_NUMBER
    variables['MIN_ITERATION'] = MIN_ITERATION
    variables['PRICE_DISTRIBUTION'] = PRICE_DISTRIBUTION
    variables['SIMULATION_DEPTH_LIMIT'] = SIMULATION_DEPTH_LIMIT
    variables['USE_SPEED'] = USE_SPEED
    if USE_SPEED:
        variables['SPEED_POWER_COEF'] = SPEED_POWER_COEF
        variables['TEU'] = TEU
        variables['MIN_SET_SIZE_SPEED'] = MIN_SET_SIZE_SPEED
        variables['USE_TEU'] = USE_TEU
    # variables['DECREASING_EXPLORATION_FACTOR'] = DECREASING_EXPLORATION_FACTOR
    for m in kwargs:
        variables[m] = kwargs[m]
    if simulation_name:
        save_config(variables, name=f'config_{name}', path=PATH, now=NOW, simulation_name=simulation_name)
    else:
        save_config(variables, name=f'config_{name}', path=PATH, now=NOW)
