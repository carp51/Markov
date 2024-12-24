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

# 状態空間を生成
states = [{ (HP, At, Bl, In, Evo, MN): 0 
            for HP, At, Bl, In, Evo, MN in itertools.product(range(parameters['M_HP_max'] + 1), 
                                                            range(parameters['M_A_max'] + 1), 
                                                            range(parameters['M_B_max'] + 1), 
                                                            range(parameters['M_I_max'] + 1), 
                                                            range(4), 
                                                            range(3))}  
            for _ in range(parameters['T'] + 1)]

# 最適行動を記録するための辞書
policies = [{(HP, At, Bl, In, Evo, MN): None 
            for HP, At, Bl, In, Evo, MN in itertools.product(range(parameters['M_HP_max'] + 1), 
                                                              range(parameters['M_A_max'] + 1), 
                                                              range(parameters['M_B_max'] + 1),
                                                              range(parameters['M_I_max'] + 1), 
                                                              range(4), 
                                                              range(3))} 
            for _ in range(parameters['T'] + 1)]


def is_state_null(state) -> bool:
    HP, At, Bl, In, Evo, MN = state
    if ( (At >= parameters['T_A'] and Bl >= parameters['T_B'] and In >= parameters['T_I']) and (At >= parameters['E_A'] or Bl >= parameters['E_B'] or In >= parameters['E_I']) ) and Evo == 0:
        return True

    if not (At >= parameters['E_A'] and Bl >= parameters['T_B'] and In >= parameters['T_I']) and Evo == 1:
        return True

    if not (At >= parameters['T_A'] and Bl >= parameters['E_B'] and In >= parameters['T_I']) and Evo == 2:
        return True

    if not (At >= parameters['T_A'] and Bl >= parameters['T_B'] and In >= parameters['E_I']) and Evo == 3:
        return True
    
    return False

def is_evolved(current_state, action):
    current_HP, current_At, current_Bl, current_In, current_Evo, current_MN = current_state
    delta_At, delta_Bl, delta_In = action[3:]

    if (current_At >= parameters['E_A'] and current_Bl >= parameters['E_B'] and current_In >= parameters['E_I']):
        return -1
    
    next_At = min(current_At + delta_At, parameters['M_A_max'])
    next_Bl = min(current_Bl + delta_Bl, parameters['M_B_max'])
    next_In = min(current_In + delta_In, parameters['M_I_max'])

    if not (next_At >= parameters['T_A'] and next_Bl >= parameters['T_B'] and next_In >= parameters['T_I']):
        return 0
    
    if (next_In >= parameters['E_I']):
        return 3
    elif (next_Bl >= parameters['E_B']):
        return 2
    elif (next_At >= parameters['E_A']):
        return 1
    else:
        return 0


def get_next_state(current_state, action, t = parameters["T"]):
    current_HP, current_At, current_Bl, current_In, current_Evo, current_MN = current_state
    HP_consumption, delta_At, delta_Bl, delta_In = action[0], action[3], action[4], action[5]

    evolved_status = is_evolved(current_state, action)
    
    next_HP = max(current_HP - HP_consumption, 0)
    next_At = min(current_At + delta_At, parameters['M_A_max'])
    next_Bl = min(current_Bl + delta_Bl, parameters['M_B_max'])
    next_In = min(current_In + delta_In, parameters['M_I_max'])
    next_Evo = current_Evo
    next_MN = current_MN

    if evolved_status == 1:
        next_Evo = 1
    elif evolved_status == 2:
        next_Evo = 2
    elif evolved_status == 3:
        next_Evo = 3

    if evolved_status == 1 and evolved_status == 2 and evolved_status == 3:
        if t % 2 != 0:
            next_MN = 1
        else:
            next_MN = 2

    next_success_state = (next_HP, next_At, next_Bl, next_In, next_Evo, next_MN)
    next_false_state = current_state

    return next_success_state, next_false_state


def get_next_reward(current_state, action_index, action, t = parameters["T"]):
    if current_state == (5,7,7,7,0,0) and t == 7:
        tmp = 0

    next_success_reward, next_false_reward = 0, 0
    evolved_status = is_evolved(current_state, action)
    if t % 2 != 0:
        if evolved_status == 1:
            next_success_reward = rewards['RmorningA']
        elif evolved_status == 2:
            next_success_reward = rewards['RmorningB']
        elif evolved_status == 3:
            next_success_reward = rewards['RmorningC']
    else:
        if evolved_status == 1:
            next_success_reward = rewards['RnightA']
        elif evolved_status == 2:
            next_success_reward = rewards['RnightB']
        elif evolved_status == 3:
            next_success_reward = rewards['RnightC']

    if action_index == 12:
        next_success_reward = rewards['Rnothing']

    return next_success_reward, next_false_reward


print(f"{parameters['T']}期目")
# T期目の処理
for state in states[-1]:
    HP = state[0]
    if is_state_null(state):
            continue
    
    for i, action in actions.items():
        HP_consumption, success_rate = action[:2]

        if HP < HP_consumption:continue

        next_success_reward, next_false_reward = get_next_reward(state, i, action)

        new_value = success_rate * next_success_reward + (1 - success_rate) * next_false_reward

        # 期待利得が最大であれば期待利得と最適行動を更新
        if new_value > states[parameters["T"]][state]:
            states[parameters["T"]][state] = new_value
            policies[parameters["T"]][state] = i  # 最適行動を記録

# T-1期目からさかのぼって計算
for t in range(parameters['T'] - 1, 0, -1):
    print(f"{t}期目")
    for state in states[t]:
        if state == (1,4,6,6,0,0) and t == 7:
            tmp = 0
        HP = state[0]
        if is_state_null(state):
            continue

        for i, action in actions.items():
            HP_consumption, success_rate = action[:2]

            if HP < HP_consumption:continue

            next_success_state, next_false_state = get_next_state(state, action, t)
            next_success_reward, next_false_reward = get_next_reward(state, i, action, t)

            new_value = success_rate * (next_success_reward + parameters['Beta'] * states[t + 1][next_success_state]) + (1 - success_rate) * (next_false_reward + parameters['Beta'] * states[t + 1][next_false_state])
            tmp = success_rate * (next_success_reward + parameters['Beta'] * states[t + 1][next_success_state])
            sss = (1 - success_rate) * (next_false_reward + parameters['Beta'] * states[t + 1][next_false_state])

            # 期待利得が最大であれば期待利得と最適行動を更新
            if new_value > states[t][state]:
                states[t][state] = new_value
                policies[t][state] = i  # 最適行動を記録

print(states[1][(parameters['M_HP_max'], 0, 0, 0, 0, 0)])
print(policies[1][(parameters['M_HP_max'], 0, 0, 0, 0, 0)])

print(states[7][(5, 5, 3, 2, 0, 0)])
print(policies[7][(5, 5, 3, 2, 0, 0)])

for i in states[9]:
    if states[9][i] >= 500:
        print(states[9][i])

while True:
    t = input("期を入力：")
    a = input("状態を入力：")
    if a == "end":
        break

    print(states[int(t)][tuple(map(int,a))])
    print(policies[int(t)][tuple(map(int,a))])