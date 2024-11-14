import itertools


parameters = {
    'T': 10,
    'M_HP_max': 5,
    'M_A_max': 10,
    'M_B_max': 10,
    'M_I_max': 10,
    'T_A': 5,
    'T_B': 5,
    'T_I': 5,
    'E_A': 8,
    'E_B': 8,
    'E_I': 8,
    'Beta': 0.95
}

actions = {
    # 攻撃・防御・賢さを上げる特訓
    1: [1, 0.85, 0, 2, 0, 0],   # a1: 攻撃力+2
    2: [1, 0.80, 0, 0, 2, 0],   # a2: 防御力+2
    3: [1, 0.90, 0, 0, 0, 2],   # a3: 賢さ+2
    4: [3, 0.60, 0, 3, 1, 0],   # a4: 攻撃力+3、防御力+1
    5: [3, 0.65, 0, 0, 3, 1],   # a5: 防御力+3、賢さ+1
    6: [3, 0.70, 0, 1, 0, 3],   # a6: 賢さ+3、攻撃力+1
    7: [5, 0.6, 0, 2, 2, 2],   # a7: 攻撃・防御・賢さすべて+2
    8: [5, 0.3, 0, 4, 4, 4],    # a8: 攻撃・防御・賢さすべて+4

    # 体力を回復させるアクション
    9: [0, 0.9, 1, 0, 0, 0],  # 簡単な休息、体力を少し回復
    10: [0, 0.7, 3, 0, 0, 0],   # 体力回復メインの休憩、しっかりと休む
    11: [0, 0.5, 5, 0, 0, 0],   # がっつりとした休憩、リスクはあるが体力を大幅回復
    12: [0, 1, 0, 0, 0, 0]     # 何もしない
}

rewards = {
    'RmorningA': 1000,
    'RmorningB': 200,
    'RmorningC': 200,
    'RnightA': 100,
    'RnightB': 20,
    'RnightC': 20,
    'Rnothing': 1
}


def is_evolved(current_state, action, t=parameters['T']):
    if (current_state[1] >= parameters['E_A'] and current_state[2] >= parameters['E_B'] and current_state[1] >= parameters['E_I']):
        return [-1, 0]
    
    new_state = {
        'At': min(current_state[1] + action[3], parameters['M_A_max']),  # 攻撃力の増減
        'Bl': min(current_state[2] + action[4], parameters['M_B_max']),  # 防御力の増減
        'In': min(current_state[3] + action[5], parameters['M_I_max'])  # 知力の増減
    }
    
    next_state = list(current_state)
    next_state[0] = max(current_state[0] - action[0], 0)
    next_state[1] = new_state['At']
    next_state[2] = new_state['Bl']
    next_state[3] = new_state['In']
    
    if not (new_state['At'] >= parameters['T_A'] and new_state['Bl'] >= parameters['T_B'] and new_state['In'] >= parameters['T_I']):
        return [0, tuple(next_state)]
    
    if (new_state['In'] >= parameters['E_I']):
        next_state[4] = 3
        next_state[5] = (t + 1) % 2
        
        return [3, tuple(next_state)]
    elif (new_state['Bl'] >= parameters['E_B']):
        next_state[4] = 2
        next_state[5] = (t + 1) % 2
        
        return [2, tuple(next_state)]
    elif (new_state['At'] >= parameters['E_A']):
        next_state[4] = 1
        next_state[5] = (t + 1) % 2
        
        return [1, tuple(next_state)]
    else:
        return [0, tuple(next_state)]
    

# 状態空間を生成
states = [{ (HP, At, Bl, In, Evo, MN): 0 for HP, At, Bl, In, Evo, MN in itertools.product(range(parameters['M_HP_max'] + 1), range(parameters['M_A_max'] + 1), range(parameters['M_B_max'] + 1), range(parameters['M_I_max'] + 1), range(4), range(2))}  for _ in range(parameters['T'] + 1)]

# 最適行動を記録するためのポリシー辞書
policies = [{(HP, At, Bl, In, Evo, MN): None for HP, At, Bl, In, Evo, MN in itertools.product(
    range(parameters['M_HP_max'] + 1), range(parameters['M_A_max'] + 1), range(parameters['M_B_max'] + 1),
    range(parameters['M_I_max'] + 1), range(4), range(2))} for _ in range(parameters['T'] + 1)]

print(f"{parameters['T']}期目")
# T期目の処理
for state in states[-1]:
    HP, At, Bl, In, Evo, MN = state
    
    if ( (At >= parameters['T_A'] and Bl >= parameters['T_B'] and In >= parameters['T_I']) and (At >= parameters['E_A'] or Bl >= parameters['E_B'] or In >= parameters['E_I']) ) and Evo == 0:
        continue
    
    if not (At >= parameters['E_A'] and Bl >= parameters['T_B'] and In >= parameters['T_I']) and Evo == 1:
        continue
    
    if not (At >= parameters['T_A'] and Bl >= parameters['E_B'] and In >= parameters['T_I']) and Evo == 2:
        continue
    
    if not (At >= parameters['T_A'] and Bl >= parameters['T_B'] and In >= parameters['E_I']) and Evo == 3:
        continue
    
    states[-1][state] = rewards['Rnothing']
    policies[-1][state] = 12

    for i, action in actions.items():
        stamina_consumption, success_rate, delta_stamina, delta_attack, delta_defense, delta_intelligence = action
        
        if HP < stamina_consumption:continue
        
        if Evo == 0:
            if 1 <= i < 9:
                evolved_state, next_state = is_evolved(state, action)
                if evolved_state == 1:
                    if parameters['T'] % 2 != 0:
                        new_value = rewards['RmorningA'] * success_rate
                    else:
                        new_value = rewards['RnightA'] * success_rate
                elif evolved_state == 2:
                    if parameters['T'] % 2 != 0:
                        new_value = rewards['RmorningB'] * success_rate
                    else:
                        new_value = rewards['RnightB'] * success_rate
                elif evolved_state == 3:
                    if parameters['T'] % 2 != 0:
                        new_value = rewards['RmorningC'] * success_rate
                    else:
                        new_value = rewards['RnightC'] * success_rate
                elif evolved_state == 0:
                    new_value = 0

                # 利得が最大であればポリシーと利得を更新
                if new_value > states[-1][state]:
                    states[-1][state] = new_value
                    policies[-1][state] = i  # 最適行動を記録
                    
# t期目の処理
for t in range(parameters['T'] - 1, 0, -1):
    print(f"{t}期目")
    for state in states[t]:
        HP, At, Bl, In, Evo, MN = state
        
        if ( (At >= parameters['T_A'] and Bl >= parameters['T_B'] and In >= parameters['T_I']) and (At >= parameters['E_A'] or Bl >= parameters['E_B'] or In >= parameters['E_I']) ) and Evo == 0:
            continue
        
        if not (At >= parameters['E_A'] and Bl >= parameters['T_B'] and In >= parameters['T_I']) and Evo == 1:
            continue
        
        if not (At >= parameters['T_A'] and Bl >= parameters['E_B'] and In >= parameters['T_I']) and Evo == 2:
            continue
        
        if not (At >= parameters['T_A'] and Bl >= parameters['T_B'] and In >= parameters['E_I']) and Evo == 3:
            continue
        
        for i, action in actions.items():
            stamina_consumption, success_rate, delta_stamina, delta_attack, delta_defense, delta_intelligence = action
            
            if HP < stamina_consumption:continue
            
            if 1 <= i < 9:
                if Evo == 0:
                    evolved_state, next_state = is_evolved(state, action, t)
                    if evolved_state == 1:
                        if t % 2 != 0:
                            new_value = success_rate * (rewards['RmorningA'] + parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                        else:
                            new_value = success_rate * (rewards['RnightA'] + parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                    elif evolved_state == 2:
                        if t % 2 != 0:
                            new_value = success_rate * (rewards['RmorningB'] + parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                        else:
                            new_value = success_rate * (rewards['RnightB'] + parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                    elif evolved_state == 3:
                        if t % 2 != 0:
                            new_value = success_rate * (rewards['RmorningC'] + parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                        else:
                            new_value = success_rate * (rewards['RnightC'] + parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                    elif evolved_state == 0:
                        if t % 2 != 0:
                            new_value = success_rate * (parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                        else:
                            new_value = success_rate * (parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                else:
                    next_state = (min(HP + delta_stamina, parameters['M_HP_max']), 
                                  min(At + delta_stamina, parameters['M_A_max']), 
                                  min(Bl + delta_stamina, parameters['M_B_max']), 
                                  min(In + delta_stamina, parameters['M_I_max']), 
                                  Evo, MN)

                    new_value = success_rate * (parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])

            elif 9 <= i < 12:
                next_state = (min(HP + delta_stamina, parameters['M_HP_max']), At, Bl, In, Evo, MN)
                new_value = success_rate * (parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                
            elif i == 12:
                new_value = rewards['Rnothing'] + parameters['Beta'] * states[t + 1][state]
                
            # 利得が最大であればポリシーと利得を更新
            if new_value >= states[t][state]:
                states[t][state] = new_value
                policies[t][state] = i  # 最適行動を記録
            
    
print(states[1][(parameters['M_HP_max'], 0, 0, 0, 0, 0)])
print(policies[1][(parameters['M_HP_max'], 0, 0, 0, 0, 0)])

print(states[8][(0, 6, 6, 6, 0, 0)])
print(policies[8][(0, 6, 6, 6, 0, 0)])