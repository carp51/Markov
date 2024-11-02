import itertools


# parameters = {
#     "T": 20,
#     "M_HP_max": 10,
#     "M_A_max": 30,
#     "M_B_max": 30,
#     "M_I_max": 30,
#     "T_A": 10,
#     "T_B": 10,
#     "T_I": 10,
#     "E_A": 25,
#     "E_B": 25,
#     "E_I": 25,
#     'Beta': 0.95
# }

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

# actions = {
#     1: [1, 90, 0, 2, 0, 0],
#     2: [1, 90, 0, 0, 2, 0],
#     3: [1, 90, 0, 0, 0, 2],
#     4: [3, 70, 0, 4, 0, 0],
#     5: [3, 70, 0, 0, 4, 0],
#     6: [3, 70, 0, 0, 0, 4],
#     7: [1, 20, 0, 4, 4, 0],
#     8: [1, 20, 0, 0, 4, 4],
#     9: [1, 20, 0, 4, 0, 4],
#     10: [3, 20, 0, 4, 4, 4],
#     11: [3, 20, 0, 4, 4, 4],
#     12: [3, 20, 0, 4, 0, 4],
#     13: [5, 90, 0, 1, 1, 1],
#     14: [5, 60, 0, 2, 2, 2],
#     15: [5, 30, 0, 3, 3, 3],
#     16: [0, 90, 3, 0, 0, 0],
#     17: [0, 60, 6, 0, 0, 0],
#     18: [0, 30, 9, 0, 0, 0],
#     19: [0, 0, 0, 0, 0, 0]
# }

actions = {
    # 攻撃・防御・賢さを上げる特訓
    1: [1, 85, 0, 2, 0, 0],    # 初級の攻撃特化、成功しやすいが効果は控えめ
    2: [1, 80, 0, 0, 3, 0],    # 初級の防御特化、やや成功しやすい
    3: [1, 90, 0, 0, 0, 2],    # 初級の賢さ特化、成功率が高く手軽
    4: [3, 60, 0, 4, 1, 0],    # 中級の攻撃特化、高リスクで攻撃力アップ
    5: [3, 65, 0, 1, 4, 0],    # 中級の防御特化、失敗しやすいが効果大
    6: [3, 70, 0, 0, 0, 5],    # 中級の賢さ特化、安定感あり
    7: [2, 50, 0, 5, 3, 0],    # 上級の攻撃・防御強化、成功すれば大きく成長
    8: [2, 55, 0, 0, 4, 4],    # 上級の防御・賢さ特化、失敗しやすいが効果大
    9: [2, 45, 0, 4, 0, 5],    # 上級の攻撃・賢さ特化、バランスが良い
    10: [4, 35, 0, 6, 2, 0],   # 最上級の攻撃特化、成功すれば劇的な効果
    11: [4, 35, 0, 0, 6, 2],   # 最上級の防御特化、リスク高め
    12: [4, 40, 0, 3, 3, 3],   # バランス型特訓、やや失敗しやすい
    13: [2, 85, 0, 2, 2, 2],   # 基礎を固めるトレーニング、低リスク
    14: [3, 65, 0, 3, 3, 3],   # バランス型中級、成功すればそこそこ効果
    15: [5, 40, 0, 4, 4, 4],   # 高リスク・高リターンのバランス型、上級者向け

    # 体力を回復させるアクション
    16: [0, 90, 1, 0, 0, 0],  # 簡単な休息、体力を少し回復
    17: [0, 60, 3, 0, 0, 0],   # 体力回復メインの休憩、しっかりと休む
    18: [0, 30, 5, 0, 0, 0],   # がっつりとした休憩、リスクはあるが体力を大幅回復
    19: [0, 0, 0, 0, 0, 0]     # 何もしない
}

rewards = {
    'RmorningA': 1000,
    'RmorningB': 200,
    'RmorningC': 200,
    'RnightA': 100,
    'RnightB': 10,
    'RnightC': 10,
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
    range(parameters['M_I_max'] + 1), range(4), range(3))} for _ in range(parameters['T'] + 1)]

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
    policies[-1][state] = 19

    for i, action in actions.items():
        stamina_consumption, success_rate, delta_stamina, delta_attack, delta_defense, delta_intelligence = action
        
        success_rate = success_rate / 100
        
        if HP < stamina_consumption:continue
        
        if Evo == 0:
            if 1 <= i < 16:
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
            
            success_rate = success_rate / 100
            
            if HP < stamina_consumption:continue
            
            if 1 <= i < 16:
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

            elif 16 <= i < 19:
                next_state = (min(HP + delta_stamina, parameters['M_HP_max']), At, Bl, In, Evo, MN)
                new_value = success_rate * (parameters['Beta'] * states[t + 1][next_state]) + (1 - success_rate) * (parameters['Beta'] * states[t + 1][state])
                
            elif i == 19:
                new_value = rewards['Rnothing'] + parameters['Beta'] * states[t + 1][state]
                
            # 利得が最大であればポリシーと利得を更新
            if new_value > states[t][state]:
                states[t][state] = new_value
                policies[t][state] = i  # 最適行動を記録
            
    
print(states[1][(parameters['M_HP_max'], 0, 0, 0, 0, 0)])
# for p in policies:
#     print(p)
print(policies[1][(parameters['M_HP_max'], 0, 0, 0, 0, 0)])
print(states[1][(parameters['M_HP_max'], 7, 8, 9, 0, 0)])
print(policies[1][(parameters['M_HP_max'], 7, 8, 9, 0, 0)])