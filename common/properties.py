import numpy as np
from itertools import product, repeat
from operator import mul
import datetime
import time
import os
import json
import pandas as pd

FILENAME_LP = "output/lp_sol.pkl"
FILENAME_SP = "output/sp_sol.pkl"
FILENAME_DM = "output/dist_mat.pkl"
# Speed variables
REGULAR_SPEED = 1
DYN_VEL_FUEL_CONSUM_CONST = 1.0  # 0.04
STOCH_PROBS = []