def get_config():
    config = dict([
        ("mac_addr_short","65:02"), # MAC addr, the last 5 characters        
        ("simulate_beacon",False), # do I simulate the beacon
        ("sim_speedup",True) # this one applies only if the above setting is set to true
    ])
    return(config)   
