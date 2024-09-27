rules = {
    'team': {
        'time': 180,
        'pieces': 2000,
    },
    'pair_final': {
        'time': 120,
        'pieces': 1000,
    },
    'pair': {
        'time': 75,
        'pieces': 500,
    },
    'individual': {
        'time': 90,
        'pieces': 500
    }
}

def hour_stamp_to_sec(stamp, competiton):
    if not stamp:
        return
    if ':' in stamp :
        h,m,s = stamp.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    else: # using the mpp to estimate the time
        stamp = stamp.replace('.','')
        sec = rules[competiton]['time'] * 60  
        sec += (rules[competiton]['pieces'] - int(stamp)) * (rules[competiton]['time'] / int(stamp))
        return sec
    
