import os

import numpy as np
from common import *
from math import floor



# designed to support dynamic/stochastic fuel prices
def fuel_price_func(n, fuel_price_list=None):
    assert fuel_price_list is not None
    fuel_price = fuel_price_list[n]
    return fuel_price


def general_fuel_price_function(n, stds_or_percentages, means, price_distribution, seed=None, previous_perc=1):
    """

    :param n:
    :param seed: To make sure when we iterate over the nodes, we get the same fuel prices
    :param stds:
    :param means:
    :param previous_perc: If previous perc =1 then we are in the medium market and we use the medium prices otherwise
    we adjust the prices according to the previous perc
    :return:
    """
    if seed:
        np.random.seed(floor(seed))
    if price_distribution == 'multinomial':
        new_perc = np.random.choice(stds_or_percentages)
        new_price = means[n] * new_perc
        return new_price, new_perc
    elif price_distribution == 'discrete_normal':
        mean = means[n]
        prices_std = stds_or_percentages[n]
        new_price =np.random.choice((np.random.normal(mean, prices_std, 1000)).astype(int)) * previous_perc
        return new_price, new_price/mean


def fuel_consume_const_func(travel_distance, speed=1, k1=1000, k2=1000,
                            dyn_vel_fuel_cons=1, regular_speed =None):
    # fuel_loss = fuel_consume_rate * travel_distance
    assert os.getenv('FUEL_COST_METHOD') in ['NONLINEAR', 'SIMPLE']
    if os.getenv('FUEL_COST_METHOD') =='NONLINEAR':
        fuel_loss = (k1 * pow(speed, 3) + k2) * travel_distance / 24
    elif os.getenv('FUEL_COST_METHOD') == 'SIMPLE':
        fuel_loss = travel_distance * dyn_vel_fuel_cons
    return fuel_loss


def fixed_bunkering_costs(n, fixed_bunk_costs=None):
    assert fixed_bunk_costs is not None
    fixed_bunker_cost = fixed_bunk_costs[n]
    return fixed_bunker_cost


def fuel_consumption_function(distance, speed, k1, k2, dy_vel_fuel_consum_const):  # tons per day
    assert os.getenv('FUEL_COST_METHOD') in ['NONLINEAR', 'SIMPLE']
    if os.getenv('FUEL_COST_METHOD') =='NONLINEAR':
        consumption_per_day = k1 * pow(speed, 3) + k2
        total_consumption = consumption_per_day * (distance / speed) / 24
    elif os.getenv('FUEL_COST_METHOD') == 'SIMPLE':
        total_consumption = distance * dy_vel_fuel_consum_const
    return total_consumption


def travel_time_function(distance, speed):
    #randomness = np.random.normal(1, 0.05)
    randomness = 1
    # WEATHER CONDITIONS CAN BE ADDED HERE
    return round((randomness * distance) / speed)


def get_port_time(port):
    # SET RANDOMIZED PORT TIME DEPENDING ON PORT
    return 1
