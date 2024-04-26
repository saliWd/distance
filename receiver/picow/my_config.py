def get_config():
    config = dict([
        ("mac_addr_short","65:02"), # MAC addr, the last 5 characters
        ("beacon_name","widmedia.ch"), # name of the beacon
        ("simulate_beacon",False), # do I simulate the beacon
        ("real_life_speed",False) # this one applies only if the above setting is set to true
    ])
    return(config)   
