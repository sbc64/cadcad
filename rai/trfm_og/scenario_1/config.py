# import libraries
from decimal import Decimal
import numpy
from datetime import timedelta
from cadCAD.configuration import append_configs
from cadCAD.configuration.utils import bound_norm_random, ep_time_step, config_sim

# references
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html?highlight=normal#numpy.random.normal

seeds = {
}

sim_config = config_sim({
    'T': range(720), #number of discrete iterations in each experiement
    'N': 1 #number of times the simulation will be run (Monte Carlo runs)
})

# Globals

price_spread_sensitivity = 0.05

equilibrium_redemption_rate = 3
redemption_rate_sensitivity = 0.05

noise_mean = 0
noise_standard_deviation = 1

timesteps_per_day = 24 # 1 hr timesteps

# Behaviors

# Mechanisms

def update_market_price(_g, step, sL, s, input):
    price_error_factor = get_price_error_factor(s['market_price'], s['redemption_price'])
    redemption_rate_factor = get_redemption_rate_factor(s['redemption_rate'])
    market_noise_factor = get_market_noise_factor()
    market_shocks_factor = get_market_shocks_factor(s['timestep'])
    return ('market_price', s['market_price'] + price_error_factor + redemption_rate_factor + market_noise_factor + market_shocks_factor)

def update_redemption_price(_g, step, sL, s, input):
    return ('redemption_price', s['redemption_price'] * (1 + get_instaneous_redemption_rate(s['redemption_rate'])))
        
def update_timestep(_g, step, sL, s, input):
    return ('timestep', s['timestep'] + 1)

# Helpers

def get_price_error_factor(market_price, redemption_price):
    return price_spread_sensitivity * (redemption_price - market_price)

def get_redemption_rate_factor(redemption_rate):
    return redemption_rate_sensitivity * (redemption_rate - equilibrium_redemption_rate)
 
def get_market_noise_factor():
    return 0

def get_market_shocks_factor(timestep):
    if (timestep == 120):
        return 0.15
    else:
        return 0

def get_instaneous_redemption_rate(redemption_rate):
    return redemption_rate / (365 * timesteps_per_day)
    
# Initial States
genesis_states = {
    'timestep': 0,
    'redemption_rate': 3,
    'redemption_price': 0.71,
    'market_price': 0.71
}

#build mechanism dictionary to "wire up the circuit"
mechanisms = [
    { 
        'policies': { 
        },
        'variables': { # The following state variables will be updated simultaneously
            'timestep': update_timestep,
            'redemption_price': update_redemption_price,
            'market_price': update_market_price
        }
    }
]



append_configs(
    sim_configs=sim_config,
    initial_state=genesis_states,
    seeds=seeds,
    partial_state_update_blocks=mechanisms
)
