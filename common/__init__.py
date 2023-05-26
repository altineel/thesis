from datetime import datetime
import numpy as np
from itertools import product, repeat
from operator import mul

FILENAME_LP = "output/lp_sol.pkl"
FILENAME_SP = "output/sp_sol.pkl"
FILENAME_DM = "output/dist_mat.pkl"
BIG_NUMBER = 9e99
COMP_THRESH = 1e-3
EPSILON = 0.001
FUEL_SAFETY_FACTOR = 1
LAST_ITERATIONS_NUMBER = 100
MCTS_DISCRETE_CARDINAL = 15
MIN_ITERATION = 500
MIN_FUEL_ALLOWANCE = 0
NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
#POLICY_LIBRARY = False
#PRICE_STD = [50, 50, 50, 50, 50]
SIMULATION_DEPTH_LIMIT = 15
SMALL_NUMBER = 1e-5

verbose = False
#DECREASING_EXPLORATION_FACTOR = 0.95


#ACTION_METHOD = 'PW'

import os
import pandas as pd
import json
def parser(now, path,simulation_name=None):
    # path = locals()['__file__']
    # path = path[:path.find('common')]
    if simulation_name:
        path = path + f'/runs/{now[:10]}/{simulation_name}'
    else:
        path = path + f'/runs/{now[:10]}/{now}'
    files = os.listdir(path)
    configs_jsons = []
    simulations_jsons = []
    dataframe = pd.DataFrame()
    numbers = []
    for f in files:
        if f.startswith('config'):
            number = f.split('_')[1]
            numbers.append(number.split('.')[0])
            with open(os.path.join(path, f)) as json_file:
                configs_jsons.append(json.load(json_file))
            with open(os.path.join(path, f'simulations_{number}')) as json_file:
                simulations_jsons.append(json.load(json_file))
    total_simulations = len(simulations_jsons)
    different_configs = []
    for keys in configs_jsons[0]:
        for configs in configs_jsons:
            try:
                if configs_jsons[0][keys] != configs[keys]:
                    different_configs.append(keys)
            except:
                continue
    for t in range(total_simulations):
        local_dataframe = pd.DataFrame({'Simulation number': numbers[t]}, index=[0])
        for dif in different_configs:
            if dif =='run_time':
                value = int(configs_jsons[t][dif])
                local_dataframe[dif] = value
            else:
                try:
                    local_dataframe[dif] = configs_jsons[t][dif]
                except:
                    local_dataframe[dif] = None
        total_runs = 0
        total_cost = 0
        total_time_penalty_cost = 0
        total_fuel_cost = 0
        for i in simulations_jsons[t]:
            if i.startswith('----- Simulation'):
                total_cost += simulations_jsons[t][f'{int(numbers[t])*100+total_runs}_FINAL COST']
                total_time_penalty_cost += simulations_jsons[t][f'{int(numbers[t])*100+total_runs}_TIME PENALTY COSTS']
                total_fuel_cost += simulations_jsons[t][f'{int(numbers[t])*100+total_runs}_FUEL COSTS']
                total_runs += 1
        local_dataframe['Average_Cost'] = round(total_cost / total_runs)
        local_dataframe['Total_Time_Penalty_Cost'] = round(total_time_penalty_cost / total_runs)
        local_dataframe['Total_Fuel_Cost'] = round(total_fuel_cost / total_runs)
        dataframe = dataframe.append(local_dataframe, ignore_index=True)
    print('SIMULATION RESULT: ',  total_cost / total_runs)
    dataframe.to_csv(path + '/results.csv', index=False)

from copy import copy
locals = copy(locals())
_path = locals['__file__']
_index = _path.find('common')
PATH = _path[:_index]


def save_config(args, name, path, now, simulation_name=None):
    from copy import copy

    keys = copy(list(args.keys()))
    for i in keys:
        if i.startswith('__'):
            del args[i]
        elif callable(args[i]):
            del args[i]
        elif isinstance(args[i], type(np)):
            del args[i]
    if simulation_name:
        path = f"{path}/runs/{now[:10]}/{simulation_name}/"
    else:
        path = f"{path}/runs/{now[:10]}/{now}/"
    if not os.path.exists(path):
        os.makedirs(path)
    pathrunconfig = path + name + '.json'
    with open(pathrunconfig, 'w') as fp:
        json.dump(args, fp, indent=4, cls=NpEncoder)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if callable(obj):
            return obj.__name__
        return super(NpEncoder, self).default(obj)


def parser(now, path,simulation_name=None):
    # path = locals()['__file__']
    # path = path[:path.find('common')]
    if simulation_name:
        path = path + f'/runs/{now[:10]}/{simulation_name}'
    else:
        path = path + f'/runs/{now[:10]}/{now}'
    files = os.listdir(path)
    configs_jsons = []
    simulations_jsons = []
    dataframe = pd.DataFrame()
    numbers = []
    for f in files:
        if f.startswith('config'):
            number = f.split('_')[1]
            numbers.append(number.split('.')[0])
            with open(os.path.join(path, f)) as json_file:
                configs_jsons.append(json.load(json_file))
            with open(os.path.join(path, f'simulations_{number}')) as json_file:
                simulations_jsons.append(json.load(json_file))
    total_simulations = len(simulations_jsons)
    different_configs = []
    for keys in configs_jsons[0]:
        for configs in configs_jsons:
            try:
                if configs_jsons[0][keys] != configs[keys]:
                    different_configs.append(keys)
            except:
                continue
    for t in range(total_simulations):
        local_dataframe = pd.DataFrame({'Simulation number': numbers[t]}, index=[0])
        for dif in different_configs:
            if dif =='run_time':
                value = int(configs_jsons[t][dif])
                local_dataframe[dif] = value
            else:
                try:
                    local_dataframe[dif] = configs_jsons[t][dif]
                except:
                    local_dataframe[dif] = None
        total_runs = 0
        total_cost = 0
        total_time_penalty_cost = 0
        total_fuel_cost = 0
        for i in simulations_jsons[t]:
            if i.startswith('----- Simulation'):
                total_cost += simulations_jsons[t][f'{int(numbers[t])*100+total_runs}_FINAL COST']
                total_time_penalty_cost += simulations_jsons[t][f'{int(numbers[t])*100+total_runs}_TIME PENALTY COSTS']
                total_fuel_cost += simulations_jsons[t][f'{int(numbers[t])*100+total_runs}_FUEL COSTS']
                total_runs += 1
        local_dataframe['Average_Cost'] = round(total_cost / total_runs)
        local_dataframe['Total_Time_Penalty_Cost'] = round(total_time_penalty_cost / total_runs)
        local_dataframe['Total_Fuel_Cost'] = round(total_fuel_cost / total_runs)
        dataframe = dataframe.append(local_dataframe, ignore_index=True)
    print('SIMULATION RESULT: ',  total_cost / total_runs)
    dataframe.to_csv(path + '/results.csv', index=False)





def k_coefficients(teu):
    if teu <= 1000:
        k1 = 0.004476
        k2 = 6.17
    elif teu <= 2000:
        k1 = 0.004595
        k2 = 16.42
    elif teu <= 3000:
        k1 = 0.004501
        k2 = 29.28
    elif teu <= 4000:
        k1 = 0.006754
        k2 = 32.23
    elif teu <= 5000:
        k1 = 0.006732
        k2 = 55.84
    elif teu <= 6000:
        k1 = 0.007297
        k2 = 71.4
    else:
        k1 = 0.006705
        k2 = 87.71
    return k1, k2

def generate_prices_n_scenarios(p0, s0=[1], sn=[0.75, 1, 1.25]):
    l = len(p0)
    scenarios = list(product(s0, *repeat(sn, l - 1)))
    prices = []
    scc = []
    for s in scenarios:
        c = [1]
        for delta in s:
            c.append(c[-1] * delta)
        c.pop(0)
        p = list(map(mul, p0, c))
        p = [int(a) for a in p]
        sc = list(map(mul, [1 for i in p0], c))
        prices.append(p)
        scc.append(sc)

    return prices, scc