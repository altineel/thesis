from __future__ import annotations
import time
from sim_environ.cost_functions import *
from common import *
import math
from mcts4py_new.MDP import *
from sim_environ.BunkeringMDP import BunkeringMDP, BunkeringAction,BunkeringState
import os

class BunkeringStateCont(BunkeringState):
    def __init__(self, port: int, fuel_amount, arrival_time, speed=INITIAL_SPEED, price_perc=1, price=None, is_terminal=False, fuel_price_list=None, fixed_bunkering_cost=None):
        super().__init__(port, fuel_amount, arrival_time, speed, price_perc, price, is_terminal, fuel_price_list, fixed_bunkering_cost)
        self.port = port
        self.fuel_amount = fuel_amount
        self.speed = speed
        self.price = general_fuel_price_function(port) * price_perc if price is None else price

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
                            dist_mat(self.port, route_schedule[self.port]), action.speed, k1, k2):
                        return True
        return False

    def resolve_action(self, action: BunkeringAction, dist_mat, route_schedule, arrival_time, fuel_capacity,
                       price_percentages, k1, k2) -> Optional[
        BunkeringState]:
        if self.is_action_valid(action, dist_mat, route_schedule, fuel_capacity, k1, k2):
            new_price_perc = self.price_perc * round(np.random.choice((np.random.normal(1, 0.2, 1000))), 2)
            return BunkeringState(port=route_schedule[self.port],
                                  fuel_amount=self.fuel_amount + action.refuel_amount - fuel_consume_const_func(
                                      dist_mat(self.port, route_schedule[self.port]), action.speed, k1, k2),
                                  speed=action.speed, arrival_time=arrival_time, price_perc=new_price_perc)



class BunkeringMDPCont(BunkeringMDP[BunkeringState, BunkeringAction]):
    def __init__(self, dist_matrix, schedule, max_speed=MAX_SPEED, fuel_capacity=None, price_percentages=None,
                 state=None, fuel_price_list=None, fixed_bunkering_cost=None, teu=7000, min_set_size_speed=1):
        super().__init__(dist_matrix, schedule, max_speed, fuel_capacity, price_percentages, state, fuel_price_list, fixed_bunkering_cost, teu, min_set_size_speed)

    def transition(self, state: BunkeringState, action: BunkeringAction) -> BunkeringState:
        if state.is_terminal:
            return state
        travel_time = travel_time_function(self.dist_mat(state.port, self.route_schedule[state.port]), action.speed)
        target_state = state.resolve_action(action, self.dist_mat, self.route_schedule,
                                            state.departure_time + travel_time, self.fuel_capacity,
                                            self.price_percentages, self.k1, self.k2)
        return state if target_state is None else target_state


