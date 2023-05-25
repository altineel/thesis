from common import *

# THESE ARE FOR FUTURE CONFIGURATIONS #
USE_SPEED = False
SPEED_POWER_COEF = 1.0
TEU = 7000
MIN_SET_SIZE_SPEED = 1
EXP_ARRIV_TIME_RNG = None
# MIN_SET_SIZE = MIN_SET_SIZE_SPEED * MIN_SET_SIZE_REFUEL
USE_TEU = False
REGULAR_SPEED = 1
DYN_VEL_FUEL_CONSUM_CONST = 1.0  # 0.04
#################


ROUTE_SCHEDULE = [0, 1, 2, 3, 4, 5, 6, 0]  # first value does not matter.
FUEL_COST_METHOD = 'SIMPLE'  # NONLINEAR
FUEL_CAPACITY = 150
DIST_MAT = np.array([[0, 30, 7, 15, 100, 100, 100],  # , 100, 100, 100, 100, 100, 100],
                     [30, 0, 25, 8, 100, 100, 100],  # , 100, 100, 100, 100, 100, 100],
                     [7, 25, 0, 30, 100, 100, 100],  # , 100, 100, 100, 100, 100, 100],
                     [15, 8, 30, 0, 40, 100, 100],  # , 100, 100, 100, 100, 100, 100],
                     [10, 8, 30, 10, 0, 44, 100],
                     [13, 8, 30, 20, 100, 0, 75],
                     [20, 8, 30, 20, 100, 0, 100]])




def dist_matrix(start, end):
    if start == (len(DIST_MAT) - 1) and end == (len(DIST_MAT)):
        return DIST_MAT[start, 0]
    return DIST_MAT[start, end]


def save_configs(name, simulation_name=None, **kwargs):
    variables = {}
    variables['DIST_MAT'] = DIST_MAT
    # variables['EARLY_STOP'] = EARLY_STOP
    variables['EPSILON'] = EPSILON
    variables['FUEL_CAPACITY'] = FUEL_CAPACITY
    variables['LAST_ITERATIONS_NUMBER'] = LAST_ITERATIONS_NUMBER
    variables['MIN_ITERATION'] = MIN_ITERATION
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


# save_config(locals(), 0, NOW)
if USE_SPEED:
    assert len(EXP_ARRIV_TIME_RNG) == len(ROUTE_SCHEDULE) - 1, "Assert: ensure there are enough time constraints per port in the schedule."
