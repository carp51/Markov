# このコードは、生物育成ゲームにおける最適な行動を動的計画法を用いて求めるものです。
# T期間をさかのぼりながら期待総利得を最大化します。
# 再帰を使わない方法で期待総利得を求めています。

import itertools


parameters = {
    'T': 10,          # 全体の期間
    'M_HP_max': 5,    # 体力の最大値
    'M_A_max': 10,    # 攻撃力の最大値
    'M_B_max': 10,    # 防御力の最大値
    'M_I_max': 10,    # 賢さの最大値
    'T_A': 5,         # 進化条件：攻撃力の閾値
    'T_B': 5,         # 進化条件：防御力の閾値
    'T_I': 5,         # 進化条件：賢さの閾値
    'E_A': 8,         # 特定進化の閾値（A）
    'E_B': 8,         # 特定進化の閾値（B）
    'E_I': 8,         # 特定進化の閾値（C）
    'Beta': 0.95      # 割引率
}

actions = {
    # 行動の番号: [体力消費量, 成功率, 体力の変化量, 攻撃力の変化量, 防御力の変化量, 賢さの変化量]

    # 特訓
    1: [1, 0.85, 0, 2, 0, 0],   # a1: 攻撃力+2
    2: [1, 0.80, 0, 0, 2, 0],   # a2: 防御力+2
    3: [1, 0.90, 0, 0, 0, 2],   # a3: 賢さ+2
    4: [3, 0.60, 0, 3, 1, 0],   # a4: 攻撃力+3、防御力+1
    5: [3, 0.65, 0, 0, 3, 1],   # a5: 防御力+3、賢さ+1
    6: [3, 0.70, 0, 1, 0, 3],   # a6: 賢さ+3、攻撃力+1
    7: [5, 0.6, 0, 2, 2, 2],   # a7: 攻撃・防御・賢さすべて+2
    8: [5, 0.3, 0, 4, 4, 4],    # a8: 攻撃・防御・賢さすべて+4

    # 休憩
    9: [0, 0.9, 1, 0, 0, 0],  # 簡単な休息、体力を少し回復
    10: [0, 0.7, 3, 0, 0, 0],   # 体力回復メインの休憩、しっかりと休む
    11: [0, 0.5, 5, 0, 0, 0],   # がっつりとした休憩、リスクはあるが体力を大幅回復

    # 何もしない
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

# 生物の状態空間を生成
states = [{ (HP, At, Bl, In, Evo, MN): 0 
            for HP, At, Bl, In, Evo, MN in itertools.product(range(parameters['M_HP_max'] + 1), 
                                                            range(parameters['M_A_max'] + 1), 
                                                            range(parameters['M_B_max'] + 1), 
                                                            range(parameters['M_I_max'] + 1), 
                                                            range(4), 
                                                            range(3))}  
            for _ in range(parameters['T'] + 1)]

# 最適行動を記録するための配列
policies = [{(HP, At, Bl, In, Evo, MN): None 
            for HP, At, Bl, In, Evo, MN in itertools.product(range(parameters['M_HP_max'] + 1), 
                                                              range(parameters['M_A_max'] + 1), 
                                                              range(parameters['M_B_max'] + 1),
                                                              range(parameters['M_I_max'] + 1), 
                                                              range(4), 
                                                              range(3))} 
            for _ in range(parameters['T'] + 1)]


def is_state_null(state):
    """
    引数で受けた状態が無効な状態かどうかを判定する関数。
    もし、無効な状態ならばTrueを返す。
    
    例えば、ステータスがA形態の状態なのにB形態に進化していることになっている場合など(5,8,6,6,2,1)。

    無効な状態の例:
    - 攻撃力、守備力、賢さが進化条件を満たしていないにも関わらず進化済み状態である。
    - 現在の進化形態とステータス値が一致しない。

    戻り値:
    - True: 無効な状態
    - False: 有効な状態
    """
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
    """
    現在の状態で行動が成功した場合にどの進化状態になるかを判定する関数。
    - current_state: 現在の状態(体力, 攻撃力, 防御力, 賢さ, 進化状態, どの時間帯に進化したか)
    - action: 実行する行動
    
    戻り値:
    - 進化状態（0: 未進化, 1: A形態, 2: B形態, 3: C形態）

    アクションが成功する前提での進化判定ですので、注意してください。
    """
    current_HP, current_At, current_Bl, current_In, current_Evo, current_MN = current_state
    delta_At, delta_Bl, delta_In = action[3:]

    if current_Evo != 0:
        return current_Evo
    
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
    """
    現在の状態と行動を基に、行動が成功した場合の状態と失敗した場合の状態を返す関数。
    - current_state: 現在の状態(体力, 攻撃力, 防御力, 賢さ, 進化状態, どの時間帯に進化したか)
    - action: 実行する行動
    - t: 期

    戻り値:
    - next_success_state: 行動が成功した場合の状態
    - next_false_state:   行動が失敗した場合の状態
    """
    current_HP, current_At, current_Bl, current_In, current_Evo, current_MN = current_state
    HP_consumption, delta_HP, delta_At, delta_Bl, delta_In = action[0], action[2], action[3], action[4], action[5]

    evolved_status = is_evolved(current_state, action)
    
    next_HP = max(current_HP - HP_consumption, 0)
    next_HP = min(next_HP + delta_HP, parameters['M_HP_max'])
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

    if (evolved_status == 1 or evolved_status == 2 or evolved_status == 3) and current_MN == 0:
        if t % 2 != 0:
            next_MN = 1
        else:
            next_MN = 2

    next_success_state = (next_HP, next_At, next_Bl, next_In, next_Evo, next_MN)
    next_false_state = current_state

    return next_success_state, next_false_state


def get_next_reward(current_state, action_index, action, t = parameters["T"]):
    """
    現在の状態と行動を基に、行動が成功した場合に得られる利得と失敗した場合に得られる利得を返す関数。
    - current_state: 現在の状態(体力, 攻撃力, 防御力, 賢さ, 進化状態, どの時間帯に進化したか)
    - action: 実行する行動
    - t: 期

    戻り値:
    - next_success_reward: 行動が成功した場合に得られる利得
    - next_false_reward:   行動が失敗した場合に得られる利得
    """
    current_Evo = current_state[4]

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

    if current_Evo != 0:
        next_success_reward = 0

    if action_index == 12:
        next_success_reward = rewards['Rnothing']

    return next_success_reward, next_false_reward


print(f"{parameters['T']}期目")
# T期目の処理
for state in states[parameters["T"]]:
    HP = state[0]
    if is_state_null(state):
            continue
    
    for i, action in actions.items():
        HP_consumption, success_rate = action[:2]

        if HP < HP_consumption:continue

        next_success_reward, next_false_reward = get_next_reward(state, i, action)

        expected_reward = success_rate * next_success_reward + (1 - success_rate) * next_false_reward

        # 期待利得が最大であれば期待利得と最適行動を更新
        if expected_reward > states[parameters["T"]][state]:
            states[parameters["T"]][state] = expected_reward
            policies[parameters["T"]][state] = i  # 最適行動を記録

# T-1期目からさかのぼって計算
for t in range(parameters['T'] - 1, 0, -1):
    print(f"{t}期目")
    for state in states[t]:
        HP = state[0]
        if is_state_null(state):
            continue

        for i, action in actions.items():
            HP_consumption, success_rate = action[:2]

            if HP < HP_consumption:continue

            next_success_state, next_false_state = get_next_state(state, action, t)
            next_success_reward, next_false_reward = get_next_reward(state, i, action, t)

            expected_reward = success_rate * (next_success_reward + parameters['Beta'] * states[t + 1][next_success_state]) + (1 - success_rate) * (next_false_reward + parameters['Beta'] * states[t + 1][next_false_state])

            # 期待総利得が最大であれば期待総利得と最適行動を更新
            if expected_reward > states[t][state]:
                states[t][state] = expected_reward
                policies[t][state] = i  # 最適行動を記録

print(states[7][(5, 6, 6, 6, 0, 0)])
print(policies[7][(5, 6, 6, 6, 0, 0)])

print(states[8][(5, 6, 6, 6, 0, 0)])
print(policies[8][(5, 6, 6, 6, 0, 0)])

while True:
    t = input("期を入力：")
    a = input("状態を入力：")
    if a == "end":
        break

    print(states[int(t)][tuple(map(int,a))])
    print(policies[int(t)][tuple(map(int,a))])