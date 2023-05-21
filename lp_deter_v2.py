from solver.mip_deter_solve import *
from sim_environ.simulator import simulate
from sim_environ.simulation_classes import MaritimeSim
solve_mip_deter()

################################################################ Test LP
from policies.policy_lp import *

# dist_mat = DIST_MAT
with open(FILENAME_DM, 'rb') as f:
    dist_mat = pkl.load(f)

schedule = ROUTE_SCHEDULE[1:]

print("######### SS Policy: ################")
mariSim = MaritimeSim(dist_mat = dist_mat, 
    fuel_price_func_callback = fuel_price_func,
    fuel_consume_func_callback = fuel_consume_const_func)

# run simulation given schedule and policy
# bunker_amt, _ = policy_ss(mariSim)
# print(bunker_amt)

# mariSim.refuelAtPort(8, mariSim.current_n)
# bunker_amt, _ = policy_ss(mariSim)
# print(bunker_amt)

# print(mariSim.cum_fuel_cost)

final_cost, fuel_costs, _ = simulate(mariSim, schedule)
print(fuel_costs)

## Tests

print("######### LP SOL: ################")
mariSim = MaritimeSim(dist_mat = dist_mat, 
    fuel_price_func_callback = fuel_price_func,
    fuel_consume_func_callback = fuel_consume_const_func)

final_cost, fuel_costs, _ = simulate(mariSim, schedule, policy = policy_lp)
print(fuel_costs)
