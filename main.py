import time

start = time.time()
from sim_environ.simulation_classes import *
from sim_environ.cost_functions import *
from sim_environ.simulator import *
import pickle as pkl
from policies.policy_lp import *
from solver.mip_stoch_solve import *
from solver.mip_fixv_stoch_solver import *
from solver.mip_deter_solve import *
from policies.policy_sp import *

from sim_environ.mdp import *
from policies.policy_mcts import *

dist_mat = DIST_MAT
# with open(FILENAME_DM, 'rb') as f:
#     dist_mat = pkl.load(f)

schedule = ROUTE_SCHEDULE[1:]

#from solver.mip_stoch_solve_with_speed import solve_mip_stoch
#start = time.time()
solve_mip_stoch()
end = time.time()
print(f'Stochastic MIP time: {end - start}')
#solve_mip_deter()

costs_sp = []
costs_lp = []

for i in range(25):
    mariSimSP = MaritimeSim(dist_mat=dist_mat,
                            fuel_price_func_callback=fuel_price_func,
                            fuel_consume_func_callback=fuel_consume_const_func,
                            stoch_params=[properties.STOCH_PROBS, properties.STOCH_BUNKERING_COSTS, properties.PRICE_SCENARIOS], seed=(i+1))

    # mariSimLP = MaritimeSim(dist_mat=dist_mat,
    #                         fuel_price_func_callback=fuel_price_func,
    #                         fuel_consume_func_callback=fuel_consume_const_func,
    #                         stoch_params=[properties.STOCH_PROBS, properties.STOCH_BUNKERING_COSTS])

    final_cost_sp, _ = simulate(mariSimSP, schedule=properties.ROUTE_SCHEDULE[1:], dist_mat=properties.DIST_MAT,
                                policy=policy_sp, print_bool=True)
    #final_cost_lp, _ = simulate(mariSimLP, schedule=properties.ROUTE_SCHEDULE[1:], dist_mat=properties.DIST_MAT,
     #                           policy=policy_lp)
    costs_sp.append(final_cost_sp)
    print(final_cost_sp)
    #costs_lp.append(final_cost_lp)

mean_costs_sp = np.mean(costs_sp)
mean_costs_lp = np.mean(costs_lp)
print(f'Expected Cost Solution: {mean_costs_lp}')
print(f'Stochastic Progrmming solution: {mean_costs_sp}')
print(f'Stochastic MIP time: {end - start}')
#[1000, 1500.0, 1000.0, 2062.5, 1406.25, 2109.375, 3796.875, 4746.09375]