import itertools


""" parameters = {
    "T": 20,
    "M_HP_max": 10,
    "M_A_max": 30,
    "M_B_max": 30,
    "M_I_max": 30,
    "T_A": 10,
    "T_B": 10,
    "T_I": 10,
    "E_A": 25,
    "E_B": 25,
    "E_I": 25
} """

parameters = {
    'T': 5,
    'M_HP_max': 5,
    'M_A_max': 10,
    'M_B_max': 10,
    'M_I_max': 10,
    'T_A': 5,
    'T_B': 5,
    'T_I': 5,
    'E_A': 8,
    'E_B': 8,
    'E_I': 8
}

actions = {
    1: [1, 90, 0, 2, 0, 0],
    2: [1, 90, 0, 0, 2, 0],
    3: [1, 90, 0, 0, 0, 2],
    4: [3, 70, 0, 4, 0, 0],
    5: [3, 70, 0, 0, 4, 0],
    6: [3, 70, 0, 0, 0, 4],
    7: [1, 40, 0, 4, 4, 0],
    8: [1, 40, 0, 0, 4, 4],
    9: [1, 40, 0, 4, 0, 4],
    10: [3, 30, 0, 4, 4, 4],
    11: [3, 30, 0, 4, 4, 4],
    12: [3, 30, 0, 4, 0, 4],
    13: [5, 90, 0, 1, 1, 1],
    14: [5, 60, 0, 3, 3, 3],
    15: [5, 30, 0, 5, 5, 5],
    16: [0, 90, 3, 0, 0, 0],
    17: [0, 60, 6, 0, 0, 0],
    18: [0, 30, 9, 0, 0, 0],
    19: [0, 0, 0, 0, 0, 0]
}

rewards = {
    'RmorningA': 300,
    'RmorningB': 100,
    'RmorningC': 100,
    'RnightA': 50,
    'RnightB': 30,
    'RnightC': 30,
    'Rnothing': 1
}


def is_evolved(current_state, action):
    new_state = {
        'At': min(current_state[1] + action[2], parameters['M_A_max']),  # 攻撃力の増減
        'Bl': min(current_state[2] + action[3], parameters['M_B_max']),  # 防御力の増減
        'In': min(current_state[3] + action[4], parameters['M_I_max'])  # 知力の増減
    }
    
    if not (new_state['At'] >= parameters['T_A'] and new_state['Bl'] >= parameters['T_B'] and new_state['In'] >= parameters['T_I']):
        return 0
    
    if (new_state['In'] >= parameters['E_I']):
        return 3
    elif (new_state['Bl'] >= parameters['E_B']):
        return 2
    elif (new_state['At'] >= parameters['E_A']):
        return 1
    else:
        return 0
    

# 状態空間を生成
states = [{ (HP, At, Bl, In, Evo, MN): 0 for HP, At, Bl, In, Evo, MN in itertools.product(range(parameters['M_HP_max'] + 1), range(parameters['M_A_max'] + 1), range(parameters['M_B_max'] + 1), range(parameters['M_I_max'] + 1), range(4), range(3))}  for _ in range(parameters['T'] + 1)]

# T期目の処理
for state in states[-1]:
    HP, At, Bl, In, Evo, MN = state
    states[-1][state] = rewards['Rnothing']
    
    for i, action in actions.items():
        stamina_consumption, success_rate, delta_stamina, delta_attack, delta_defense, delta_intelligence = action
        
        success_rate = success_rate / 100
        
        if HP < action[0]:continue
        
        if Evo == 0:
            if 1 <= i < 16:
                if is_evolved(state, action) == 1:
                    if parameters['T'] % 2 != 0:
                        states[-1][state] = max(states[-1][state], rewards['RmorningA'] * success_rate)
                    else:
                        states[-1][state] = max(states[-1][state], rewards['RnightA'] * success_rate)
                elif is_evolved(state, action) == 2:
                    if parameters['T'] % 2 != 0:
                        states[-1][state] = max(states[-1][state], rewards['RmorningB'] * success_rate)
                    else:
                        states[-1][state] = max(states[-1][state], rewards['RnightB'] * success_rate)
                elif is_evolved(state, action) == 3:
                    if parameters['T'] % 2 != 0:
                        states[-1][state] = max(states[-1][state], rewards['RmorningC'] * success_rate)
                    else:
                        states[-1][state] = max(states[-1][state], rewards['RnightC'] * success_rate)
                    
# t期目の処理
for t in range(parameters['T'] - 1, 0, -1):
    for state in states[t]:
        HP, At, Bl, In, Evo, MN = state
        for i, action in actions.items():
            stamina_consumption, success_rate, delta_stamina, delta_attack, delta_defense, delta_intelligence = action
            
            success_rate = success_rate / 100
            
            if HP < action[0]:continue
            
            
    
print(123)