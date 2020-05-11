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

P_constant = 1

def calculate_p_rate(x, y):
    return (x - y) / x * P_constant

def calculate_target_rate(market_price, target_price):
    return calculate_p_rate(market_price, target_price)

def update_target_rate(_g, step, sL, s, input):
    target_rate = calculate_target_rate(s['market_price'], s['target_price'])
    return ('target_rate', target_rate)

def update_target_price(_g, step, sL, s, input):
    target_price = s['target_price'] + s['target_rate']
    return ('target_price', target_price)

def update_market_price(_g, step, sL, s, input):
    add_to_market_price = 0
    if (s['timestep'] < 5):
        add_to_market_price = 0
    elif (s['timestep'] >= 5 and s['timestep'] < 10):
        add_to_market_price = 0.1
    else:
        add_to_market_price = 0
    return ('market_price', s['market_price'] + add_to_market_price)

def update_timestep(_g, step, sL, s, input):
    return ('timestep', s['timestep'] + 1)

# Initial States
genesis_states = {
    'timestep': 0,
    'target_rate': 0, 
    'target_price': 1,
    'market_price': 1
}

exogenous_states = {
    #'time': time_model
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
