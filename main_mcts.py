import os

from sim_environ.simulation_classes import *
from sim_environ.cost_functions import *
from sim_environ.simulator import *
from common import *
import itertools
import time
from policies.policy_mcts import policy_mcts_stateful
from tqdm import tqdm
import random
from common import save_config


def statefulsolver(name, simulation_name, dist_mat, schedule, stoch_probs, stoch_bunkering_costs, price_scenarios, price_stds, expected_prices, fixed_bunkering_cost, reg_speed, teu, speed_model, price_distribution,
                   simulation_number, exp_arr_time_rng, late_arrival_penalty, early_arrival_penalty, **kwargs):
    start_time = time.time()
    simulations = {}
    nbsimulations = simulation_number
    for i in tqdm(range(nbsimulations), desc='Run', position=0):
        mariSimLP = MaritimeSim(dist_mat=dist_mat,
                                fuel_price_func_callback=fuel_price_func,
                                fuel_consume_func_callback=fuel_consume_const_func,
                                stoch_params=[stoch_probs, stoch_bunkering_costs, price_scenarios],
                                expected_prices=expected_prices,
                                fixed_bunkering_cost=fixed_bunkering_cost,
                                route_schedule=schedule,
                                dyn_vel_fuel=1,
                                reg_speed=reg_speed,
                                price_stds=price_stds,
                                exp_arrival_time_ranges=exp_arr_time_rng,
                                late_arriv_penalty=late_arrival_penalty,
                                early_arriv_penalty=early_arrival_penalty,
                                seed=i + 1, teu=teu, speed_model=speed_model, price_distribution=price_distribution
                                )
        simulations[f'{i}{i}{i}{i}'] = 'STARTED'
        simulations[f'----- Simulation {i} -----'] = name * 100 + i
        simulations[f'{name * 100 + i}_FUEL PRICES '] = mariSimLP.cur_fuel_prices

        final_cost_lp, _ = simulate(mariSimLP, schedule=schedule, dist_mat=dist_mat, print_bool=False,
                                    policy=policy_mcts_stateful,
                                exp_arriv_time_rng=exp_arr_time_rng,
                                late_time_penalty=late_arrival_penalty,
                                early_time_penalty=early_arrival_penalty,simulation_saver_dict=simulations, simulation_number=name * 100 + i)
        print(f'Cost Solution Stateful: {final_cost_lp}')
    run_time = (time.time() - start_time)
    print("--- %s seconds ---" % run_time)
    kwargs['number_of_simulations'] = nbsimulations
    save_config(simulations, name=f'simulations_{name}', path=PATH, now=NOW, simulation_name=simulation_name)
    return run_time

def run_configs(run_id, simulation_name, dist_mat, schedule, stoch_probs, stoch_bunkering_costs, price_scenarios, price_stds, expected_prices,
                fixed_bunkering_cost, reg_speed,teu, speed_model, price_distribution, simulation_number, exp_arr_time_rng, late_arrival_penalty,
                early_arrival_penalty, kwargs):
    os.environ['SIMULATION_NAME'] = simulation_name
    os.environ['FUEL_CAPACITY'] = str(kwargs['FUEL_CAPACITY'])
    i = run_id * 100

    for decreasing_iter in kwargs['DECREASING_ITER']:
        for early_stop in kwargs['EARLY_STOP']:
            for exp_const in kwargs['EXP_CONST']:
                for max_iter in kwargs['MAX_ITERATION']:
                    for expl_const_decay in kwargs['EXP_CONST_DECAY']:
                        for alg in kwargs['ALGORITHM']:
                            for opt_act in kwargs['OPT_ACT']:
                                for heuritic in kwargs['HEURISTIC']:
                                    os.environ['HEURISTIC'] = str(heuritic)
                                    os.environ['ALGORITHM'] = alg
                                    os.environ['EARLY_STOP'] = str(early_stop)
                                    os.environ['EXPLORATION_CONSTANT'] = str(exp_const)
                                    os.environ['MAX_ITERATION'] = str(max_iter)
                                    os.environ['DECREASING_ITER'] = str(decreasing_iter)
                                    os.environ['OPTIMAL_ACTION_POLICY'] = str(opt_act)
                                    os.environ['EXP_CONST_DECAY'] = str(expl_const_decay)

                                    if alg =='NAIVE':
                                        i += 1
                                        print(decreasing_iter, early_stop, exp_const, max_iter, expl_const_decay,alg, opt_act, heuritic)
                                        run_time = statefulsolver(i, simulation_name, dist_mat, schedule,
                                                                  stoch_probs, stoch_bunkering_costs,
                                                                  price_scenarios, price_stds, expected_prices,
                                                                  fixed_bunkering_cost, reg_speed, teu, speed_model,
                                                                  price_distribution,simulation_number, exp_arr_time_rng, late_arrival_penalty, early_arrival_penalty, **os.environ)
                                        save_configs(run_time=run_time, name=i,
                                                     simulation_name=simulation_name, **os.environ)
                                    if alg != 'NAIVE':
                                        for min_set_size_refuel in kwargs['MIN_SET_SIZE_REFUEL']:
                                            for dpw_alpha in kwargs['DPW_ALPHA']:
                                                for dpw_exp in kwargs['DPW_EXP']:
                                                    for min_set_size_speed in kwargs['MIN_SET_SIZE_SPEED']:
                                                        os.environ['MIN_SET_SIZE_SPEED'] = str(min_set_size_speed)
                                                        os.environ['DPW_EXPLORATION'] = str(dpw_exp)
                                                        os.environ['DPW_ALPHA'] = str(dpw_alpha)
                                                        os.environ['MIN_SET_SIZE_REFUEL'] = str(min_set_size_refuel)
                                                        if alg =='DPWSolver':
                                                            for probabilistic in kwargs['DPW_PROBABILISTIC']:
                                                                print(decreasing_iter, early_stop, exp_const, max_iter, expl_const_decay, alg, opt_act, min_set_size_refuel, heuritic, dpw_alpha, dpw_exp, probabilistic)
                                                                os.environ['DPW_PROBABILISTIC'] = str(probabilistic)
                                                                i += 1
                                                                run_time = statefulsolver(i, simulation_name, dist_mat, schedule,
                                                                                          stoch_probs, stoch_bunkering_costs,
                                                                                          price_scenarios, price_stds, expected_prices,
                                                                                          fixed_bunkering_cost, reg_speed, teu, speed_model,
                                                                                          price_distribution, simulation_number, exp_arr_time_rng, late_arrival_penalty, early_arrival_penalty, **os.environ)
                                                                save_configs(run_time=run_time, name=i, simulation_name=simulation_name, **os.environ)
                                                        else:
                                                            print(decreasing_iter, early_stop, exp_const, max_iter, expl_const_decay, alg, opt_act, min_set_size_refuel, heuritic, dpw_alpha, dpw_exp)
                                                            i += 1
                                                            run_time = statefulsolver(i, simulation_name, dist_mat, schedule,
                                                                                      stoch_probs, stoch_bunkering_costs,
                                                                                      price_scenarios, price_stds, expected_prices,
                                                                                      fixed_bunkering_cost, reg_speed, teu, speed_model,
                                                                                      price_distribution, simulation_number, exp_arr_time_rng, late_arrival_penalty, early_arrival_penalty, **os.environ)
                                                            save_configs(run_time=run_time, name=i, simulation_name=simulation_name, **os.environ)



if __name__ == '__main__':
    # from common.PORT4.multi_1 import param_values2, ROUTE_SCHEDULE, save_configs, simulation_name, STOCH_PROBS, \
    #     STOCH_BUNKERING_COSTS, PRICE_PERCENTAGES, FIXED_BUNKERING_COSTS, DIST_MAT, EXPECTED_BUNKERING_COSTS, \
    #     REGULAR_SPEED, USE_SPEED, TEU, FUEL_COST_METHOD, PRICE_DISTRIBUTION, PRICE_STDS
    #
    # parser(now=NOW, path=PATH, simulation_name=simulation_name)
    # os.environ['USE_SPEED'] = str(USE_SPEED)
    # os.environ['FUEL_COST_METHOD'] = FUEL_COST_METHOD
    # schedule = ROUTE_SCHEDULE[1:]
    # random.seed(time.time())
    # run_id = random.randint(0, 100000)
    # run_configs(run_id, simulation_name=simulation_name, dist_mat=DIST_MAT, schedule=schedule, stoch_probs=STOCH_PROBS,
    #             stoch_bunkering_costs=STOCH_BUNKERING_COSTS, price_scenarios=PRICE_PERCENTAGES, price_stds=PRICE_STDS,
    #             expected_prices=EXPECTED_BUNKERING_COSTS, fixed_bunkering_cost=FIXED_BUNKERING_COSTS,
    #             reg_speed=REGULAR_SPEED, teu=TEU, speed_model=USE_SPEED, price_distribution=PRICE_DISTRIBUTION, simulation_number=param_values2['SIMULATION_NUMBER'],
    #             kwargs=param_values2)
    # parser(now=NOW, path=PATH, simulation_name=simulation_name)

    # from common.PORT4.multi_2 import param_values2, ROUTE_SCHEDULE, save_configs, simulation_name, STOCH_PROBS, \
    #     STOCH_BUNKERING_COSTS, PRICE_PERCENTAGES, FIXED_BUNKERING_COSTS, DIST_MAT, EXPECTED_BUNKERING_COSTS, \
    #     REGULAR_SPEED, USE_SPEED, TEU, FUEL_COST_METHOD, PRICE_DISTRIBUTION, PRICE_STDS
    #
    # os.environ['USE_SPEED'] = str(USE_SPEED)
    # os.environ['FUEL_COST_METHOD'] = FUEL_COST_METHOD
    # schedule = ROUTE_SCHEDULE[1:]
    # random.seed(time.time())
    # run_id = random.randint(0, 100000)
    # run_configs(run_id, simulation_name=simulation_name, dist_mat=DIST_MAT, schedule=schedule, stoch_probs=STOCH_PROBS,
    #             stoch_bunkering_costs=STOCH_BUNKERING_COSTS, price_scenarios=PRICE_PERCENTAGES, price_stds=PRICE_STDS,
    #             expected_prices=EXPECTED_BUNKERING_COSTS, fixed_bunkering_cost=FIXED_BUNKERING_COSTS,
    #             reg_speed=REGULAR_SPEED, teu=TEU, speed_model=USE_SPEED, price_distribution=PRICE_DISTRIBUTION, simulation_number=param_values2['SIMULATION_NUMBER'],
    #             kwargs=param_values2)
    # parser(now=NOW, path=PATH, simulation_name=simulation_name)

    from common.PORT4.multi_2s import param_values, ROUTE_SCHEDULE, save_configs, simulation_name, STOCH_PROBS, \
        STOCH_BUNKERING_COSTS, PRICE_PERCENTAGES, FIXED_BUNKERING_COSTS, DIST_MAT, EXPECTED_BUNKERING_COSTS, \
        REGULAR_SPEED, USE_SPEED, TEU, FUEL_COST_METHOD, PRICE_DISTRIBUTION, PRICE_STDS
    if USE_SPEED:
        from common.PORT4.multi_2s import LATE_ARRIVAL_PENALTY, EARLY_ARRIVAL_PENALTY, EXP_ARRIV_TIME_RNG, MAX_SPEED, MIN_SPEED
    os.environ['USE_SPEED'] = str(USE_SPEED)
    os.environ['FUEL_COST_METHOD'] = FUEL_COST_METHOD
    os.environ['LATE_ARRIVAL_PENALTY'] = str(LATE_ARRIVAL_PENALTY)
    os.environ['EARLY_ARRIVAL_PENALTY'] = str(EARLY_ARRIVAL_PENALTY)
    os.environ['EXP_ARRIV_TIME_RNG'] = str(EXP_ARRIV_TIME_RNG)
    os.environ['MIN_SPEED'] = str(MIN_SPEED)
    os.environ['MAX_SPEED'] = str(MAX_SPEED)
    os.environ['REGULAR_SPEED'] = str(REGULAR_SPEED)
    schedule = ROUTE_SCHEDULE[1:]
    random.seed(time.time())
    run_id = random.randint(0, 100000)
    run_configs(run_id, simulation_name=simulation_name, dist_mat=DIST_MAT, schedule=schedule, stoch_probs=STOCH_PROBS,
                stoch_bunkering_costs=STOCH_BUNKERING_COSTS, price_scenarios=PRICE_PERCENTAGES, price_stds=PRICE_STDS,
                expected_prices=EXPECTED_BUNKERING_COSTS, fixed_bunkering_cost=FIXED_BUNKERING_COSTS,
                reg_speed=REGULAR_SPEED, teu=TEU, speed_model=USE_SPEED, price_distribution=PRICE_DISTRIBUTION, exp_arr_time_rng=EXP_ARRIV_TIME_RNG, late_arrival_penalty=LATE_ARRIVAL_PENALTY,
                early_arrival_penalty=EARLY_ARRIVAL_PENALTY, simulation_number=param_values['SIMULATION_NUMBER'], kwargs=param_values)
    parser(now=NOW, path=PATH, simulation_name=simulation_name)

    from common.PORT4.multi_2s import param_values2 as param_values, ROUTE_SCHEDULE, save_configs, simulation_name, STOCH_PROBS, \
        STOCH_BUNKERING_COSTS, PRICE_PERCENTAGES, FIXED_BUNKERING_COSTS, DIST_MAT, EXPECTED_BUNKERING_COSTS, \
        REGULAR_SPEED, USE_SPEED, TEU, FUEL_COST_METHOD, PRICE_DISTRIBUTION, PRICE_STDS
    if USE_SPEED:
        from common.PORT4.multi_2s import LATE_ARRIVAL_PENALTY, EARLY_ARRIVAL_PENALTY, EXP_ARRIV_TIME_RNG, MAX_SPEED, MIN_SPEED
    os.environ['USE_SPEED'] = str(USE_SPEED)
    os.environ['FUEL_COST_METHOD'] = FUEL_COST_METHOD
    os.environ['LATE_ARRIVAL_PENALTY'] = str(LATE_ARRIVAL_PENALTY)
    os.environ['EARLY_ARRIVAL_PENALTY'] = str(EARLY_ARRIVAL_PENALTY)
    os.environ['EXP_ARRIV_TIME_RNG'] = str(EXP_ARRIV_TIME_RNG)
    os.environ['MIN_SPEED'] = str(MIN_SPEED)
    os.environ['MAX_SPEED'] = str(MAX_SPEED)
    os.environ['REGULAR_SPEED'] = str(REGULAR_SPEED)
    schedule = ROUTE_SCHEDULE[1:]
    random.seed(time.time())
    run_id = random.randint(0, 100000)
    run_configs(run_id, simulation_name=simulation_name, dist_mat=DIST_MAT, schedule=schedule, stoch_probs=STOCH_PROBS,
                stoch_bunkering_costs=STOCH_BUNKERING_COSTS, price_scenarios=PRICE_PERCENTAGES, price_stds=PRICE_STDS,
                expected_prices=EXPECTED_BUNKERING_COSTS, fixed_bunkering_cost=FIXED_BUNKERING_COSTS,
                reg_speed=REGULAR_SPEED, teu=TEU, speed_model=USE_SPEED, price_distribution=PRICE_DISTRIBUTION, exp_arr_time_rng=EXP_ARRIV_TIME_RNG, late_arrival_penalty=LATE_ARRIVAL_PENALTY,
                early_arrival_penalty=EARLY_ARRIVAL_PENALTY, simulation_number=param_values['SIMULATION_NUMBER'], kwargs=param_values)
    parser(now=NOW, path=PATH, simulation_name=simulation_name)