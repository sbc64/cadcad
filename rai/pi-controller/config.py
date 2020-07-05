# import libraries
from decimal import Decimal
import numpy as np
from datetime import timedelta
from cadCAD.configuration import append_configs
from cadCAD.configuration.utils import bound_norm_random, ep_time_step, config_sim

seeds = {
}

sim_config = config_sim({
    'T': range(50), #number of discrete iterations in each experiement
    'N': 1 #number of times the simulation will be run (Monte Carlo runs)
})


# define the time deltas for the discrete increments in the model
# ts_format = '%Y-%m-%d %H:%M:%S'
# t_delta = timedelta(days=0, minutes=1, seconds=0)
# def time_model(_g, step, sL, s, _input):
#     y = 'time'
#     x = ep_time_step(s, dt_str=s['time'], fromat_str=ts_format, _timedelta=t_delta)
#     return (y, x)

# Behaviors

# Mechanisms

BLOCKTIME = 15
P_constant = 0.01
I_constant = 0.001

# helpers
def calculate_p_rate(input, setpoint):
    return (setpoint - input) / input * P_constant

def calculate_i_rate(time_since_deviation):
    return time_since_deviation * I_constant

def calculate_target_rate(market_price, target_price, time_since_deviation):
    return calculate_p_rate(market_price, target_price)
    # return calculate_p_rate(market_price, target_price) + calculate_i_rate(time_since_deviation)

def did_deviation_update(target_price, market_price, latest_devation_type):
    deviation = target_price - market_price
    if (deviation >= 0 and latest_devation_type == -1):
        return False
    elif (deviation < 0 and latest_devation_type == 1):
        return False
    else:
        return True

# setters
def update_target_rate(_g, step, sL, s, input):
    target_rate = calculate_target_rate(s['market_price'], s['target_price'], s['time_since_deviation'])
    return ('target_rate', target_rate)

def update_target_price(_g, step, sL, s, input):
    target_price = s['target_price'] + (BLOCKTIME * s['target_rate'])
    if (target_price < 0):
        target_price = 0
    return ('target_price', target_price)

def update_market_price(_g, step, sL, s, input):
    add_to_market_price = 0
    if (s['timestep'] < 5):
        add_to_market_price = 0
    elif (s['timestep'] >= 5 and s['timestep'] < 10):
        add_to_market_price = 0.1
    else:
        delta = s['target_price'] - s['market_price']
        add_to_market_price = delta * 0.8
    return ('market_price', s['market_price'] + add_to_market_price)

def update_timestep(_g, step, sL, s, input):
    return ('timestep', s['timestep'] + 1)

def update_latest_deviation_type(_g, step, sL, s, input):
    deviation_type = 0
    deviation = s['target_price'] - s['market_price']
    if (deviation > 0):
        deviation_type = 1
    elif (deviation < 0):
        deviation_type = -1
    return ('latest_deviation_type', deviation_type)

def update_time_since_deviation(_g, step, sL, s, input):
    result = 0
    if (not did_deviation_update(s['target_price'], s['market_price'], s['latest_deviation_type'])):
        result = s['time_since_deviation'] + BLOCKTIME
    return ('time_since_deviation', result)

# Initial States
genesis_states = {
    'timestep': 0,
    'latest_deviation_type': 0,
    'time_since_deviation': 0,
    'target_rate': 0,
    'target_price': 1,
    'market_price': 1
}

exogenous_states = {
    # 'time': time_model
}

env_processes = {
}

#build mechanism dictionary to "wire up the circuit"
mechanisms = [
    { 
        'policies': { 
        },
        'variables': { # The following state variables will be updated simultaneously
            'timestep': update_timestep,
            'latest_deviation_type': update_latest_deviation_type,
            'time_since_deviation': update_time_since_deviation,
            'target_rate': update_target_rate,
            'target_price': update_target_price,
            'market_price': update_market_price
        }
    }
]

append_configs(
    sim_configs=sim_config,
    initial_state=genesis_states,
    seeds=seeds,
    raw_exogenous_states=exogenous_states,
    env_processes=env_processes,
    partial_state_update_blocks=mechanisms
)
