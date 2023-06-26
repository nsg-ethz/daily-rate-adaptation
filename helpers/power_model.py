# Variable and parameter for the power model of the Wedge switch

def load_exp_data():
    ##
    # Profiling power=f(Gbps)
    # - 16 ports set at 100G
    # - receiving power on 10 ports
    ##
    # Data
    Gbps  = [0, 10, 25, 50, 100]
    power = [133.11, 134.12, 135.61, 138.07, 144.53]
    return Gbps, power



def print_exp_data():
    # Data from Jackie's report (for 10 active ports)
    num_active_ports = 10
    # .. static power [W]
    measure_power_00_at_10G = 120.83 # W
    measure_power_10_at_10G = 122.19 # W
    measure_power_00_at_25G = 122.86 # W
    measure_power_25_at_25G = 126.14 # W
    # .. dynamic power [W/Gbps]
    dynamic_power_at_10G = ((
        measure_power_10_at_10G - measure_power_00_at_10G) / 10
        / num_active_ports)
    dynamic_power_at_25G = ((
        measure_power_25_at_25G - measure_power_00_at_25G) / 25
        / num_active_ports)
    # from the OLS interpolation (see plot_P=f(U))
    dynamic_power_at_100G = 0.11 / num_active_ports
    print("""Dynamic power values (in W/Gbps)
    - at 100G\t{:.3f} 
    - at 25G\t{:.3f}
    - at 10G\t{:.3f}
    """.format(
        dynamic_power_at_100G,
        dynamic_power_at_25G,
        dynamic_power_at_10G))

def power_model():
    idle_power = 108 # W
    port_power = {
        100: {
            'static_power': 1.57,   # W
            'dynamic_power': 0.011   # W/Gbps
        },
        25: {
            'static_power': 0.52,   # W
            'dynamic_power': 0.013   # W/Gbps
        },
        10: {
            'static_power': 0.31,   # W
            'dynamic_power': 0.014   # W/Gbps
        },
        0: {
            'static_power': 0,   # W
            'dynamic_power': 0   # W/Gbps
        },
    }
    return port_power, idle_power
