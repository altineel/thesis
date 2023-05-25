import pandas as pd

from sim_environ.simulation_classes import *
from sim_environ.cost_functions import *
from sim_environ.mdp import *
from mcts4py_new.StatefulSolver import StatefulSolver
from mcts4py_new.ProgressiveWideningSolver import ProgressiveWideningSolver
from mcts4py_new.DPWSolver import DPWSolver
from mcts4py_new.PuctSolver import PuctSolver
from mcts4py_new.PuctWithDPWSolver import PuctWithDPWSolver
from sim_environ.BunkeringMDP import *
import datetime
import os
import random
import time

now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")


def policy_mcts(sim_env):
    print('EXPLORATION_CONSTANT: ', os.getenv('EXPLORATION_CONSTANT'))
    if sim_env.current_n == 0:
        return (50, 1)
    elif sim_env.current_n == 1:
        return (18, 1)
    elif sim_env.current_n == 2:
        return (36, 1)
    elif sim_env.current_n == 3:
        return (13, 1)


def policy_mcts_stateful(sim_env):
    random.seed(time.time())
    try:
        if False:  # POLICY_LIBRARY:
            policy_library = pd.read_csv('policies/policy_library.csv')
            refuel_amount = policy_library['refuel_amount'].to_numpy()[
                (policy_library['price'].to_numpy() == sim_env.getFuelPrice(sim_env.current_n)) & (
                        policy_library['port'].to_numpy() == sim_env.current_n) & (
                        policy_library['fuel_amount'].to_numpy() == sim_env.fuel_level)].item()
            speed = 1
            print('policy library hit: ',
                  f'port: {sim_env.current_n}, price: {sim_env.getFuelPrice(sim_env.current_n)}, fuel_amount: '
                  f'{sim_env.fuel_level}, refuel_amount: {refuel_amount} , refuel_amount: {refuel_amount}')
            return refuel_amount, speed
        else:
            raise Exception
    except:
        start_time = time.time()
        bunker_state = BunkeringState(port=sim_env.current_n, fuel_amount=sim_env.fuel_level,  arrival_time=0,
                                      price_perc=sim_env.price_percentages[sim_env.current_n],
                                      price=sim_env.cur_fuel_prices[sim_env.current_n], is_terminal=False,
                                      fixed_bunkering_cost=sim_env.fixed_bunkering_cost)
        if sim_env.price_distribution == 'multinomial':
            mdp = BunkeringMDP(dist_matrix=sim_env.dist_mat,schedule=sim_env.route_schedule, fuel_capacity=int(os.getenv('FUEL_CAPACITY')),
                               price_percentages=sim_env.stoch_params[2], state=bunker_state, fuel_price_list=sim_env.expected_prices,
                               price_distribution=sim_env.price_distribution, fixed_bunkering_cost=sim_env.fixed_bunkering_cost,
                               )
        elif sim_env.price_distribution =='discrete_normal':
            mdp = BunkeringMDP(dist_matrix=sim_env.dist_mat, schedule=sim_env.route_schedule, fuel_capacity=int(os.getenv('FUEL_CAPACITY')),
                               state=bunker_state, fuel_price_list=sim_env.expected_prices, price_distribution=sim_env.price_distribution,
                               price_stds=sim_env.price_stds, fixed_bunkering_cost=sim_env.fixed_bunkering_cost)

        exploration_constant = int(os.getenv('EXPLORATION_CONSTANT'))
        max_iteration = int(os.getenv('MAX_ITERATION'))
        sim_depth_limit = int(os.getenv('SIMULATION_DEPTH_LIMIT', SIMULATION_DEPTH_LIMIT))
        early_stop = True if os.getenv('EARLY_STOP') == 'True' else False
        early_stop_condition = {'min_iteration': max_iteration / 2, 'epsilon': 0.001,
                                'last_iterations_number': max_iteration / 4}
        decreasing_iter_numbers = True if os.getenv('DECREASING_ITER', ) == 'True' else False
        exploration_constant_decay = float(os.getenv('EXP_CONST_DECAY'))
        dpw_alpha = float(os.getenv('DPW_ALPHA',0 ))
        dpw_exploration = float(os.getenv('DPW_EXPLORATION',0 ))
        random.seed(time.time())
        if os.getenv('ALGORITHM') == 'PuctSolver':
            method = PuctSolver
            kwargs = {}
        elif os.getenv('ALGORITHM') in ('ProgressiveWideningSolver'):
            method = ProgressiveWideningSolver
            kwargs = {'dpw_alpha': dpw_alpha, 'dpw_exploration': dpw_exploration}
        elif os.getenv('ALGORITHM') in ('NAIVE'):
            method = StatefulSolver
            kwargs = {}
        elif os.getenv('ALGORITHM') == 'DPWSolver':
            method = DPWSolver
            if sim_env.price_distribution == 'multinomial':
                kwargs = {'dpw_alpha': dpw_alpha, 'dpw_exploration': dpw_exploration,
                          'max_random_states': len(sim_env.stoch_params[2]),
                          'probabilistic': os.getenv('DPW_PROBABILISTIC')}
            elif sim_env.price_distribution =='discrete_normal':
                kwargs = {'dpw_alpha': dpw_alpha, 'dpw_exploration': dpw_exploration,
                          'max_random_states': 1000,
                          'probabilistic': bool(os.getenv('DPW_PROBABILISTIC'))}
        elif os.getenv('ALGORITHM') == 'PuctWithDPWSolver':
            method = PuctWithDPWSolver
            kwargs = {'dpw_alpha': dpw_alpha, 'dpw_exploration': dpw_exploration}
        else:
            raise Exception('Wrong Algorithm')
        solver = method(
            mdp,
            simulation_depth_limit=sim_depth_limit,
            exploration_constant=exploration_constant,
            discount_factor=1,
            max_iteration=max_iteration,
            early_stop=early_stop,
            early_stop_condition=early_stop_condition,
            verbose=False,
            exploration_constant_decay=exploration_constant_decay,
            **kwargs
        )
        if decreasing_iter_numbers:
            m = 1 if sim_env.current_n == 0 else sim_env.current_n
            solver.run_search(int(max_iteration / (m + 0.5)))
        else:
            solver.run_search(max_iteration)
        if os.getenv('OPTIMAL_ACTION_POLICY') == 'MOST_VISITED':
            opt_act = solver.extract_most_visited_action().inducing_action
        elif os.getenv('OPTIMAL_ACTION_POLICY') == 'MIN_REWARD':
            opt_act = solver.extract_optimal_action().inducing_action
        elif os.getenv('OPTIMAL_ACTION_POLICY') == 'MIN_REWARD_SOME_VISITED':
            opt_act = solver.extract_min_reward_some_visited().inducing_action
        else:
            raise 'Wrong OPTIMAL POLICY'
        run_time = (time.time() - start_time)

        # dot = solver.visualize_tree()
        # dot.render(f"runs/{NOW[:10]}/{os.environ['simulation_name']}/tree_{sim_env.current_n}_{
        # exploration_constant}_{os.getenv('ALGORITHM')}_{dpw_exploration}_{dpw_alpha}", format='png')
        # solver.save_tree(SIMULATION_DEPTH_LIMIT, path=f'runs/{NOW[:10]}/{NOW}',
        #                  simulation_number=sim_env.current_n, run_time=run_time)
        # solver.display_tree()

        return opt_act.refuel_amount, opt_act.speed
