from __future__ import annotations
import time
from sim_environ.cost_functions import *
from common import *
import math
from mcts4py_new.MDP import *
import os


class BunkeringAction():
    def __init__(self, speed, refuel_amount, next_port):
        self.speed, self.refuel_amount, self.next_port = speed, refuel_amount, next_port

    def __str__(self) -> str:
        return f"Speed: {self.speed}, Ref: {self.refuel_amount}, NextPort: {self.next_port}, 'Speed : {self.speed}"

    def __eq__(self, __o):
        if isinstance(__o, BunkeringAction):
            return __o.speed == self.speed and __o.refuel_amount == self.refuel_amount and __o.next_port == \
                   self.next_port
        return False

    def __hash__(self) -> int:
        return hash(self.__str__())

    @property
    def name(self):
        # return f"Rf_{self.refuel_amount}_S{self.speed}"
        return f"{self.refuel_amount}"


class BunkeringState():
    def __init__(self, port: int, fuel_amount, arrival_time, speed=INITIAL_SPEED, price_perc=1, price=None, is_terminal=False, fixed_bunkering_cost=None):
        self.port = port
        self.fuel_amount = fuel_amount
        self.speed = speed
        self.price = price
        self.price_perc = price_perc
        self.fixed_bcost = fixed_bunkering_costs(port, fixed_bunkering_cost)
        self.arrival_time = arrival_time
        self.departure_time = self.arrival_time + get_port_time(self.port)
        self.is_terminal = is_terminal

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, BunkeringState):
            return __o.port == self.port and __o.fuel_amount == self.fuel_amount and __o.speed == self.speed and \
                   __o.arrival_time == self.arrival_time and __o.price == self.price
        return False

    def __str__(self) -> str:
        return f'Port: {self.port}, Fuel Amount: {self.fuel_amount}, Arrival Time: {self.arrival_time}, ' \
               f'Speed: {self.speed}, Price: {self.price}'

    def is_action_valid(self, action: BunkeringAction, dist_mat, route_schedule, fuel_capacity, k1, k2) -> bool:
        if action.refuel_amount + self.fuel_amount <= fuel_capacity:
            if not self.is_terminal:
                if action.next_port == route_schedule[self.port]:
                    if self.fuel_amount + action.refuel_amount >= fuel_consume_const_func(
                            dist_mat[self.port, route_schedule[self.port]], action.speed, k1, k2):
                        return True
        return False

    def resolve_action(self, action: BunkeringAction, dist_mat, route_schedule, arrival_time, fuel_capacity,
                       price_percentages_or_stds, k1, k2, is_terminal, fuel_price_list, fixed_bunkering_cost, price_distribution) -> Optional[BunkeringState]:
        if self.is_action_valid(action, dist_mat, route_schedule, fuel_capacity, k1, k2):
            new_price, new_perc = general_fuel_price_function(n=route_schedule[self.port], stds_or_percentages=price_percentages_or_stds, means=fuel_price_list, price_distribution=price_distribution,
                                                              previous_perc=self.price_perc)
            return BunkeringState(port=route_schedule[self.port],
                                  fuel_amount=self.fuel_amount + action.refuel_amount - fuel_consume_const_func(dist_mat[self.port, route_schedule[self.port]], action.speed, k1, k2),
                                  speed=action.speed, arrival_time=arrival_time, price=new_price, price_perc=new_perc, is_terminal=is_terminal,
                                  fixed_bunkering_cost=fixed_bunkering_cost)

    def calculate_reward(self, refuel_amount, exp_arriv_time_ring=None):
        reward = 0
        reward -= refuel_amount * self.price
        reward -= self.fixed_bcost if refuel_amount > 0 else 0

        # SPEED AND ARRIVAL TIME CONSIDERATIONS ##
        if os.getenv('USE_SPEED') == 'True':
            upper_arrival_time_dif = max(0, self.arrival_time - exp_arriv_time_ring[self.port][1])
            # lower_arrival_time_dif = max(0, EXP_ARRIV_TIME_RNG[self.port][0] - self.arrival_time)
            reward -= pow(upper_arrival_time_dif, KAPPA) * LATE_ARRIVAL_PENALTY
            # reward -= pow(lower_arrival_time_dif, KAPPA) * EARLY_ARRIVAL_PENALTY
        # SPEED AND ARRIVAL TIME CONSIDERATIONS ##

        # FUEL REMAINING CONSIDERATIONS ##
        # if self.fuel_amount < MIN_FUEL_ALLOWANCE:
        #   reward -= (MIN_FUEL_ALLOWANCE - self.fuel_amount) * KAPPA2
        reward = math.inf if self.fuel_amount + refuel_amount < 0 else reward

        return reward


class BunkeringMDP(MDP[BunkeringState, BunkeringAction]):
    def __init__(self, dist_matrix, schedule, max_speed=MAX_SPEED, fuel_capacity=None, price_percentages=None,
                 state=None, fuel_price_list=None, price_distribution=None, price_stds=None, fixed_bunkering_cost=None, teu=7000, min_set_size_speed=1):
        self.fuel_price_list = fuel_price_list
        self.price_distribution = price_distribution
        self.price_stds = price_stds
        if self.price_distribution == 'discrete_normal':
            assert price_stds is not None
        elif self.price_distribution == 'multinomial':
            assert price_percentages is not None
        self.dist_mat = dist_matrix
        self.route_schedule = schedule
        self.fixed_bunkering_cost = fixed_bunkering_cost
        self.min_fuel_allowance = MIN_FUEL_ALLOWANCE
        self.starting_state = state
        self.k1, self.k2 = k_coefficients(teu)
        self.time = 0
        self.max_speed = max_speed
        self.fuel_capacity = fuel_capacity
        self.price_percentages = price_percentages
        self.min_set_size_speed = min_set_size_speed
        self.min_set_size_refuel = int(os.getenv('MIN_SET_SIZE', 0))
        self.min_set_size = self.min_set_size_refuel * self.min_set_size_speed

    def is_terminal(self, state: BunkeringState) -> bool:
        return state.is_terminal

    def initial_state(self) -> BunkeringState:
        return self.starting_state

    def reward(self, current_state: Optional[BunkeringState], action: Optional[BunkeringAction]) -> float:
        return current_state.calculate_reward(action.refuel_amount)

    def get_terminal_state(self, departure_time, port):  # change where it is used to use this function
        if departure_time != 1:
            return port == self.route_schedule[-1]
        else:
            return False

    def transition(self, state: BunkeringState, action: BunkeringAction) -> BunkeringState:
        if state.is_terminal:
            return state
        travel_time = travel_time_function(self.dist_mat[state.port, self.route_schedule[state.port]], action.speed)
        is_terminal = self.get_terminal_state(state.departure_time + travel_time, action.next_port)
        if self.price_distribution == 'multinomial':
            target_state = state.resolve_action(action, self.dist_mat, self.route_schedule,
                                                state.departure_time + travel_time, self.fuel_capacity,
                                                self.price_percentages, self.k1, self.k2, is_terminal, fuel_price_list=self.fuel_price_list, fixed_bunkering_cost=self.fixed_bunkering_cost,
                                                price_distribution=self.price_distribution)
        else:
            target_state = state.resolve_action(action, self.dist_mat, self.route_schedule,
                                                state.departure_time + travel_time, self.fuel_capacity,
                                                self.price_stds, self.k1, self.k2, is_terminal, fuel_price_list=self.fuel_price_list, fixed_bunkering_cost=self.fixed_bunkering_cost,
                                                price_distribution=self.price_distribution)
        return state if target_state is None else target_state

    def actions(self, state: BunkeringState, number_of_visits: int, iteration_number: int = None,
                max_iteration_number: int = None, dpw_exploration: dict = None, dpw_alpha: dict = None,
                min_action=False, simulate=False) -> list[
        TAction]:
        if os.getenv('HEURISTIC') == 'True':
            if state.port == self.route_schedule[-2]:
                speed, distance = 1, self.dist_mat[state.port][self.route_schedule[state.port]]
                ref_amount = distance - state.fuel_amount if distance > state.fuel_amount else 0
                return [BunkeringAction(speed, ref_amount, self.route_schedule[state.port])]
        actions = list()

        if state.is_terminal:
            return actions

        if os.getenv('ALGORITHM') == 'NAIVE':
            possible_actions = self.get_all_actions()
        else:
            possible_actions = self.dpw_actions(number_of_visits, dpw_exploration, dpw_alpha)
        for a in possible_actions:
            if state.is_action_valid(BunkeringAction(a[0], a[1], self.route_schedule[state.port]), self.dist_mat,
                                     self.route_schedule, self.fuel_capacity, self.k1, self.k2):
                actions.append(BunkeringAction(a[0], a[1], self.route_schedule[state.port]))
        return actions

    def get_min_action(self, act):
        return act[1]

    def get_all_actions(self):
        possible_fuel_actions = set(np.linspace(0, self.fuel_capacity, num=self.fuel_capacity).astype(int))
        possible_speed_actions = [1]
        possible_actions = [(x, y) for x in possible_speed_actions for y in possible_fuel_actions]
        return possible_actions

    # REDUNDANT
    def dpw_actions_dif(self, nVisits, dpw_exploration_refuel, dpw_alpha_refuel, dpw_exploration_speed,
                        dpw_alpha_speed):
        possible_speed_actions = set(np.linspace(1, self.max_speed, num=int(self.min_set_size_speed)).astype(int))
        possible_fuel_actions = set(np.linspace(0, self.fuel_capacity, num=int(self.min_set_size_refuel)).astype(int))
        if nVisits == 0:
            return [(x, y) for x in possible_speed_actions for y in possible_fuel_actions]
        kSpeed = dpw_exploration_speed * (nVisits ** dpw_alpha_speed)
        set_size_speed = math.ceil(kSpeed)
        if set_size_speed <= self.min_set_size_speed:
            new_speed_actions = set(
                np.linspace(MIN_SPEED, self.max_speed, num=int(self.min_set_size_speed)).astype(np.uint64))
        elif set_size_speed < self.min_set_size_refuel * 2:
            possible_speed_actions = set(
                np.linspace(MIN_SPEED, self.fuel_capacity, num=int(self.min_set_size_speed)).astype(np.uint64))
            new = set(
                np.linspace(MIN_SPEED, self.fuel_capacity, num=int(self.min_set_size_speed * 2 - 1)).astype(np.uint64))
            dif = new.difference(possible_speed_actions)
            dif = list(dif)
            dif.sort()
            addition = dif[:int(set_size_speed - self.min_set_size_speed)]
            new_speed_actions = set(list(possible_speed_actions) + addition)
        else:
            self.min_set_size_speed = self.min_set_size_speed * 2 - 1
            new_speed_actions = set(
                np.linspace(MIN_SPEED, self.max_speed, num=int(self.min_set_size_speed * 2 - 1)).astype(np.uint64))

        kFuel = dpw_exploration_refuel * (nVisits ** dpw_alpha_refuel)
        set_size_fuel = math.ceil(kFuel)
        if set_size_fuel <= self.min_set_size_refuel:
            new_fuel_actions = set(
                np.linspace(0, self.fuel_capacity, num=int(self.min_set_size_refuel)).astype(np.uint64))
        elif set_size_fuel < self.min_set_size_refuel * 2:
            possible_fuel_actions = set(
                np.linspace(0, self.fuel_capacity, num=int(self.min_set_size_refuel)).astype(np.uint64))
            new = set(np.linspace(0, self.fuel_capacity, num=int(self.min_set_size_refuel * 2 - 1)).astype(np.uint64))
            dif = new.difference(possible_fuel_actions)
            dif = list(dif)
            dif.sort()
            addition = dif[:int(set_size_fuel - self.min_set_size_refuel)]
            new_fuel_actions = set(list(possible_fuel_actions) + addition)

            # print(f'IF TIME: {(time.time() - start) * 1000}')
        else:
            start = time.time()
            # print('MIN SET SIZE:' , self.min_set_size_refuel)
            self.min_set_size_refuel = self.min_set_size_refuel * 2 - 1
            new_fuel_actions = set(
                np.linspace(0, self.fuel_capacity, num=int(self.min_set_size_refuel * 2 - 1)).astype(np.uint64))

            # print(f'ELSE TIME: {(time.time() - start) * 1000}')

        new_actions = [(x, y) for x in new_speed_actions for y in new_fuel_actions]
        return new_actions

    def dpw_actions(self, nVisits, dpw_exploration, dpw_alpha):
        if os.getenv('USE_SPEED') == 'True':
            possible_speed_actions = set(
                np.linspace(1, self.max_speed, num=int(self.min_set_size_speed)).astype(int))
            possible_fuel_actions = set(
                np.linspace(0, self.fuel_capacity, num=int(self.min_set_size_refuel)).astype(int))
            if nVisits == 0:
                return [(x, y) for x in possible_speed_actions for y in possible_fuel_actions]
            k = dpw_exploration * (nVisits ** dpw_alpha)
            set_size = math.ceil(k)
            if set_size <= self.min_set_size:
                return [(x, y) for x in possible_speed_actions for y in possible_fuel_actions]
            else:  # set_size < min_set_size * 2:
                new = set(
                    np.linspace(1, self.max_speed, num=int(self.min_set_size_speed * 2 - 1)).astype(np.uint64))
                min_set_size_speed = self.min_set_size_speed * 2 - 1
                dif = new.difference(possible_speed_actions)
                dif = list(dif)
                dif.sort()
                addition_speed = dif[:int(set_size - self.min_set_size)]
                new = set(
                    np.linspace(0, self.fuel_capacity, num=int(self.min_set_size_refuel * 2 - 1)).astype(np.uint64))
                min_set_size_refuel = self.min_set_size_refuel * 2 - 1
                dif = new.difference(possible_fuel_actions)
                dif = list(dif)
                dif.sort()
                addition_refuel = dif[:int(set_size - self.min_set_size)]
                t = len(possible_fuel_actions) * len(possible_speed_actions)
                i = 0
                while t < set_size:
                    t = (len(possible_fuel_actions) + 1) * (len(possible_speed_actions) + 1)
                    if t < set_size:
                        try:
                            possible_fuel_actions.add(addition_refuel[i])
                        except IndexError:
                            new = set(np.linspace(0, self.fuel_capacity, num=int(min_set_size_refuel * 2 - 1)).astype(
                                np.uint64))
                            min_set_size_refuel = min_set_size_refuel * 2 - 1
                            dif = new.difference(possible_fuel_actions)
                            dif = list(dif)
                            dif.sort()
                            addition_refuel = dif[:int(set_size - self.min_set_size)]
                        try:
                            possible_speed_actions.add(addition_speed[i])
                        except:
                            new = set(
                                np.linspace(1, self.max_speed, num=int(min_set_size_speed * 2 - 1)).astype(np.uint64))
                            min_set_size_speed = min_set_size_speed * 2 - 1
                            dif = new.difference(possible_speed_actions)
                            dif = list(dif)
                            dif.sort()
                            addition_speed = dif[:int(set_size - self.min_set_size)]
                    elif (len(possible_fuel_actions) + 1) * (len(possible_speed_actions)) < set_size:
                        try:
                            possible_fuel_actions.add(addition_refuel[i])
                        except:
                            new = set(np.linspace(0, self.fuel_capacity, num=int(min_set_size_refuel * 2 - 1)).astype(
                                np.uint64))
                            min_set_size_refuel = min_set_size_refuel * 2 - 1
                            dif = new.difference(possible_fuel_actions)
                            dif = list(dif)
                            dif.sort()
                            addition_refuel = dif[:int(set_size - self.min_set_size)]
                    i += 1
                return [(x, y) for x in possible_fuel_actions for y in possible_speed_actions]
        else:
            set_size = math.ceil(dpw_exploration * pow(nVisits, dpw_alpha))
            MIN_SET_SIZE_REFUEL = int(os.getenv('MIN_SET_SIZE'))
            if set_size < MIN_SET_SIZE_REFUEL:
                set_size = MIN_SET_SIZE_REFUEL
            if set_size <= self.min_set_size_refuel:
                new_fuel_actions = set(
                    np.linspace(0, self.fuel_capacity, num=self.min_set_size_refuel).astype(int))
            elif set_size < self.min_set_size_refuel * 2:
                possible_fuel_actions = set(
                    np.linspace(0, self.fuel_capacity, num=self.min_set_size_refuel).astype(int))
                new = set(np.linspace(0, self.fuel_capacity, num=self.min_set_size_refuel * 2).astype(int))
                dif = new.difference(possible_fuel_actions)
                dif = list(dif)
                dif.sort()
                new_fuel_actions = list(possible_fuel_actions) + dif[:set_size - self.min_set_size_refuel]
            else:
                self.min_set_size_refuel = self.min_set_size_refuel * 2
                new_fuel_actions = list(
                    np.linspace(0, self.fuel_capacity, num=self.min_set_size_refuel * 2).astype(int))

            new_speed_actions = [1]  ####### !!!
            new_fuel_actions = set(new_fuel_actions)
            new_actions = [(x, y) for x in new_speed_actions for y in new_fuel_actions]
            return new_actions
