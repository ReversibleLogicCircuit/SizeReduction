from utils import *
from nonInter import *
import copy

def gate_to_str(n, gate):
    result = "C{}Not (".format(len(gate[1]))
    
    for con in gate[1]:
        result += "{}".format(n - con[0])
        if con[1] == 0:
            result += "n"
        result += ","
    result = result[:-1] + ")"
    
    result += "({})".format(n - gate[0])
    
    return result

def parityOfSbox(n, sbox):
    wantForm = copy.deepcopy(sbox)
    wantForm.sort()
    tSbox = copy.deepcopy(sbox)
    count = 0
    for i in range(len(tSbox)):
        compareVal = wantForm[i]
        if compareVal != tSbox[i]:
            count += 1
            pos = tSbox.index(compareVal)
            tSbox[pos] = tSbox[i]
            tSbox[i] = compareVal

    if count & 1:
        return True # odd permutation
    else:
        return False

#################################################
def makeBlock(n, now_n, sbox, cons, nList, now_rows):
    result = []

    # blcok 만들기
    gates = makeBlock_subroutine(now_n, sbox[-(1 << now_n):].index(now_rows[0]), sbox[-(1 << now_n):].index(now_rows[1]), cons)
    # gate 변환
    if now_n != n and gates != []:
        for j in range(n - now_n):
            gates[-1][1].append([n - 1 - j,1]) # gate 바꾸기
    result.append(gates)
    costGB = 0
    for j in range(len(gates)):
        sbox = apply_gate(n, sbox, gates[j])
        if len(gates[j][1]) > 1:
            costGB += 2 * len(gates[j][1]) - 3

    # blcok 위치 수정
    gates = makeLeft(now_n, sbox[-(1 << now_n):].index(now_rows[0]), sbox[-(1 << now_n):].index(now_rows[1]), cons)
    result.append(gates)
    costAL = 0
    for j in range(len(gates)):
        sbox = apply_gate(n, sbox, gates[j])
        if len(gates[j][1]) > 1:
            costAL += 2 * len(gates[j][1]) - 3

    # nList updates
    indexRows = nList.index(now_rows[0])
    nList = nList[:indexRows] + nList[indexRows+2:]

    # cons updtaes
    cons = cons_update(now_n, cons + [next_position(now_n, cons)])

    return result, [costGB, costAL], sbox, cons, nList

# 맞춰지는 블록의 개수가 2의 거듭제곱을 넘는 순가
# 실제로 다루어야할 실제 크기가 줄어드는데, 그거에 맞게 사용해서 시간복잡도를 줄이기 위한 용도
def makeBlock_semi(n, now_n, sbox, cons, nList, now_rows):
    # blcok 만들기
    gates = makeBlock_subroutine(now_n, sbox.index(now_rows[0]), sbox.index(now_rows[1]), cons)
    costGB = 0
    if now_n != n and gates != []:
        for j in range(0, len(gates)-1, 1):
            sbox = apply_gate(now_n, sbox, gates[j])
            if len(gates[j][1]) > 1:
                costGB += 2 * len(gates[j][1]) - 3
        # 마지막 게이트는 따로 카운트
        sbox = apply_gate(now_n, sbox, gates[-1])
        costGB += 2 * (len(gates[-1][1]) + n - now_n) - 3 # 게이트비용 조정
    else:
        for j in range(0, len(gates), 1):
            sbox = apply_gate(now_n, sbox, gates[j])
            if len(gates[j][1]) > 1:
                costGB += 2 * len(gates[j][1]) - 3

    # blcok 위치 수정
    gates = makeLeft(now_n, sbox.index(now_rows[0]), sbox.index(now_rows[1]), cons)
    costAL = 0
    for j in range(len(gates)):
        sbox = apply_gate(now_n, sbox, gates[j])
        if len(gates[j][1]) > 1:
            costAL += 2 * len(gates[j][1]) - 3

    # nList updates
    indexRows = nList.index(now_rows[0])
    nList = nList[:indexRows] + nList[indexRows+2:]

    # cons updtaes
    cons = cons_update(now_n, cons + [next_position(now_n, cons)])

    return [costGB, costAL], sbox, cons, nList

def choose(n, options):
    tempOps = sorted(options, key=lambda fun: fun[2], reverse=True)      # 해당 비용안에서 FB순으로 정렬 (Full로 들어와서 [2] 항목에 FB 개수만 있음)
    for di in range(len(tempOps[0][1]), 0, -1):                          # 앞쪽부터 FB가 있는 것 부터 사용하도록
        tempOps = sorted(tempOps, key=lambda fun: fun[1][di-1])
    tempOps = sorted(tempOps, key=lambda fun: sum(fun[1]))               # 해당 비용으로 정렬 -> 비용순으로 작은비용으로 정렬되며, 그 순서는 FB가 큰 순서임

    return tempOps[0][0]

# 깊이전수조사용 (재귀함수를 이용한, 깊이우선 탐색)
# nowQuality와 BestQuality는 depth만큼 길이가 정의되어 있어야 됨
# ex) d=3, nowQuality = [10, 10, 10], bestQuality = [10, 10, 10]
def depthExhasutive(n, now_n, sbox, cons, nList, nowQuality, bestQuality, now_d, d):
    if now_d == d:
        if sum(nowQuality) == sum(bestQuality) and nowQuality < bestQuality:
            for i in range(d):
                bestQuality[i] = nowQuality[i]
        elif sum(nowQuality) < sum(bestQuality):
            for i in range(d):
                bestQuality[i] = nowQuality[i]
    else:
        for i in range(0, len(nList), 2):
            now_rows = [nList[i], nList[i+1]]
            tNow_n = now_n
            tempCosts, tempSbox, tempCons, tempNList = makeBlock_semi(n, tNow_n, sbox, cons, nList, now_rows)
            nowQuality[now_d] = sum(tempCosts)

            if tempCons[0] == '0' + '-' * (tNow_n - 1) and tNow_n > 2:
                tempCons = []
                tNow_n -= 1
                tempSbox = tempSbox[-(1 << tNow_n):] # now_n 수준으로 줄이기
            
            depthExhasutive(n, tNow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, now_d + 1, d)

# ex) d=3, nowQuality = [[10, 10, 10], [...]], bestQuality = [[10, 10, 10], [...]]
def depthExhasutive2(n, now_n, sbox, cons, nList, nowQuality, bestQuality, bestBackupQuality, now_d, d):
    if now_d == d:
        # depthExhasutive2는 그 사용방법상 여기까지 올 경우 3비트 sbox가 되어 있음
        FB_List = check_block_changed(3, [], nList, sbox)

        if sum(nowQuality[0]) == sum(bestQuality[0]) and nowQuality[0] < bestQuality[0] and FB_List[1] == []:
            for i in range(d):
                bestQuality[0][i] = nowQuality[0][i]
                bestQuality[1][i] = nowQuality[1][i]
        elif sum(nowQuality[0]) < sum(bestQuality[0]) and FB_List[1] == []:
            for i in range(d):
                bestQuality[0][i] = nowQuality[0][i]
                bestQuality[1][i] = nowQuality[1][i]

        if sum(nowQuality[0]) == sum(bestBackupQuality[0]) and nowQuality[0] < bestBackupQuality[0]:
            for i in range(d):
                bestBackupQuality[0][i] = nowQuality[0][i]
                bestBackupQuality[1][i] = nowQuality[1][i]
        elif sum(nowQuality[0]) < sum(bestBackupQuality[0]):
            for i in range(d):
                bestBackupQuality[0][i] = nowQuality[0][i]
                bestBackupQuality[1][i] = nowQuality[1][i]
    else:
        for i in range(0, len(nList), 2):
            now_rows = [nList[i], nList[i+1]]
            tNow_n = now_n
            tempCosts, tempSbox, tempCons, tempNList = makeBlock_semi(n, tNow_n, sbox, cons, nList, now_rows)
            nowQuality[0][now_d] = sum(tempCosts)
            nowQuality[1][now_d] = now_rows

            if tempCons[0] == '0' + '-' * (tNow_n - 1) and tNow_n > 2:
                tempCons = []
                tNow_n -= 1
                tempSbox = tempSbox[-(1 << tNow_n):] # now_n 수준으로 줄이기
            
            depthExhasutive2(n, tNow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, bestBackupQuality, now_d + 1, d)

# default - Full block
def makeList_Full(n, now_n, sbox, cons, nList, depth):
    options = []
    sbox = sbox[-(1 << now_n):] # now_n 수준으로 줄이기
    for i in range(0, len(nList), 2):
        nownow_n = copy.deepcopy(now_n)

        option = [[nList[i], nList[i + 1]], [], []]

        # 실제 선택된 block을 뭉쳐 시작하기
        #tempGates, tempCosts, tempSbox, tempCons, tempNList = makeBlock(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])
        tempCosts, tempSbox, tempCons, tempNList = makeBlock_semi(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])

        if tempCons[0] == '0' + '-' * (nownow_n - 1) and nownow_n > 2:
            tempCons = []
            nownow_n -= 1
            tempSbox = tempSbox[-(1 << nownow_n):] # now_n 수준으로 줄이기

        # 정보 채우기
        option[1].append(sum(tempCosts))
        FB_list = check_block_changed(nownow_n, tempCons, tempNList, tempSbox)
        option[2] = max([len(FB_list[0]) >> 1,len(FB_list[1]) >> 1])    # Full block 이므로 max로 처리

        # depth가 없을 경우 처리
        if depth == 0:
            options.append(option)
            continue

        # 깊이 전수조사 시작
        tDepth = depth
        if depth > (len(tempNList) >> 1):
            tDepth = len(tempNList) >> 1

        nowQuality = [100 for j in range(tDepth)]
        bestQuality = [100 for j in range(tDepth)]

        depthExhasutive(n, nownow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, 0, tDepth)

        # 깊이-전수조사로 얻은 최고의 결과를 반영해서 option에 입력
        option[1] = option[1] + bestQuality
        options.append(option)

    return options

def makeList2_Full(n, now_n, sbox, cons, nList, oddFlag, depth):
    options = []
    sbox = sbox[-(1 << now_n):] # now_n 수준으로 줄이기
    for i in range(0, len(nList), 2):
        nownow_n = copy.deepcopy(now_n)
        toddFlag = copy.deepcopy(oddFlag)

        option = [[nList[i], nList[i + 1]], [], [], []]

        # 실제 선택된 block을 뭉쳐 시작하기
        #tempGates, tempCosts, tempSbox, tempCons, tempNList = makeBlock(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])
        tempCosts, tempSbox, tempCons, tempNList = makeBlock_semi(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])

        if tempCons[0] == '0' + '-' * (nownow_n - 1) and nownow_n > 2:
            tempCons = []
            nownow_n -= 1
            tempSbox = tempSbox[-(1 << nownow_n):] # now_n 수준으로 줄이기
            if tempCosts[0] == 2 * (n-1) - 3:
                toddFlag = False if toddFlag else True

        # 정보 채우기
        option[1].append(sum(tempCosts))
        FB_list = check_block_changed(nownow_n, tempCons, tempNList, tempSbox)
        option[2] = max([len(FB_list[0]) >> 1,len(FB_list[1]) >> 1]) # Full block이므로 Max로 처리

        # depth가 없을 경우 처리
        if depth == 0:
            options.append(option)
            continue

        # 깊이 전수조사 시작
        tDepth = depth
        if depth > (len(tempNList) >> 1):
            tDepth = len(tempNList) >> 1

        nowQuality = [[10000 for j in range(tDepth)], [0 for j in range(tDepth)]]
        bestQuality = [[10000 for j in range(tDepth)], [0 for j in range(tDepth)]]
        bestBackupQuality = [[10000 for j in range(tDepth)], [0 for j in range(tDepth)]]

        depthExhasutive2(n, nownow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, bestBackupQuality, 0, tDepth)

        # 깊이-전수조사로 얻은 최고의 결과를 반영해서 option에 입력
        if 10000 not in bestQuality[0]:
            option[1] = option[1] + bestQuality[0]
            option[3] = bestQuality[1]
            options.append(option)

            # 마지막 3개 예상
            if toddFlag and option[1][-1] != 2 * (n-1) - 3:
                option[1] += [2 * (n-1) - 5, 0, 2 * (n-1) - 3, 0]
            else:
                option[1] += [2 * (n-1) - 5, 0, 0, 0]
        else:
            option[1] = option[1] + bestBackupQuality[0]
            option[3] = bestBackupQuality[1]
            options.append(option)

    return options

def decompse_Full(n, sbox, parDepth):
    nList = copy.deepcopy(sbox)
    nList.sort()
    tSbox = sbox
    resultGates = []
    
    now_n = n
    while now_n > 1:
        # 현재 상태에서 조건 설정
        cons = []
        numMadeBlock = 0    # 매 단계마다 1개의 블록을 만들기 때문에 넘치는 상황을 고려하지 않아도 됨

        # 마지막 오른쪽에서 8번째 블록부터는 depth = 3으로 전수조사
        # 이 if 문은 n=5 인경우에만 동작 (왜냐면 n > 5이면 밑에과정중에서 완료 됨)
        if now_n == 4:
            oddFlag = parityOfSbox(n, tSbox)
            options = makeList2_Full(n, now_n, tSbox, cons, nList, oddFlag, 3)
            options = sorted(options, key=lambda fun: sum(fun[1]))

            # 위의 4개의 블록(현재 + depth 3)에 대해서 뭉침
            for now_rows in [options[0][0]] + options[0][3]:
                result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, now_rows)
                resultGates += result   # 결과물 게이트 반영
                numMadeBlock += 1 # 사실 필요 없음

            # 4비트 끝
            now_n -= 1
            continue

        # now_n에 맞는 블록 만들기 시작
        while numMadeBlock < (1 << (now_n - 2)):
            now_parDepth = parDepth[n - now_n]  # now_n에 따라 다른 depth

            # MAKELIST()
            options = makeList_Full(n, now_n, tSbox, cons, nList, now_parDepth)

            # CHOOSE()
            now_rows = choose(n, options)

            # 실제 뭉치고, 반영
            result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, now_rows)
            resultGates += result   # 결과물 게이트 반영

            # block 개수 하나 만든것을 명시
            numMadeBlock += 1

            # 마지막 오른쪽에서 9번째 블록부터는 depth = 4로 전수조사 하도록 탈출
            if now_n == 5 and numMadeBlock == 7:
                break

        # 마지막 오른쪽에서 9번째 블록부터는 depth = 4로 전수조사
        if now_n == 5 and numMadeBlock == 7:
            oddFlag = parityOfSbox(n, tSbox)
            options = makeList2_Full(n, now_n, tSbox, cons, nList, oddFlag, 4)
            options = sorted(options, key=lambda fun: sum(fun[1]))

            # now_n = 5 수준) 오른쪽에서 9번째 블록 뭉침
            result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, options[0][0])
            resultGates += result   # 결과물 게이트 반영

            # now_n = 5 수준 정리
            cons = []
            now_n -= 1
            numMadeBlock = 0 # 사실 필요 없음

            # now_n == 4 수준에서 뭉침
            for now_rows in options[0][3]:
                result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, now_rows)
                resultGates += result   # 결과물 게이트 반영
                numMadeBlock += 1 # 사실 필요 없음

            # 4비트 끝
            now_n -= 1
            continue
        
        # 비트 하나 줄이기
        now_n -= 1

    return resultGates

# default - Half block
def makeList_Half(n, now_n, sbox, cons, nList, depth):
    options = []
    for i in range(0, len(nList), 2):
        # 뭉치려는 block의 even or odd를 보고 다르면 안하기
        if sbox.index(nList[i]) & 1 != 0: # 0으로 고정함
            continue

        nownow_n = copy.deepcopy(now_n)

        option = [[nList[i], nList[i + 1]], [], []]

        # 실제 선택된 block을 뭉쳐 시작하기
        tempGates, tempCosts, tempSbox, tempCons, tempNList = makeBlock(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])

        if tempCons[0] == '0' + '-' * (nownow_n - 1) and nownow_n > 2:
            tempCons = []
            nownow_n -= 1

        # 정보 채우기
        option[1].append(sum(tempCosts))
        FB_list = check_block_changed(nownow_n, tempCons, tempNList, tempSbox)
        option[2] = len(FB_list[0]) >> 1 # even block관련 개수만을 반환

        # depth가 없을 경우 처리
        if depth == 0:
            options.append(option)
            continue

        # 선택목록에서 고려할 경우의 수 선정
        # even, odd 블록의 전수조사를 위해서
        tempEvenList = [tempNList[i] for i in range(len(tempNList)) if tempSbox.index(tempNList[i]) & 1 == ((i & 1) ^ 0)]

        # 깊이 전수조사 시작
        tDepth = depth
        if depth > (len(tempEvenList) >> 1):
            tDepth = len(tempEvenList) >> 1

        nowQuality = [100 for j in range(tDepth)]
        bestQuality = [100 for j in range(tDepth)]

        depthExhasutive(n, nownow_n, tempSbox, tempCons, tempEvenList, nowQuality, bestQuality, 0, tDepth)

        # 깊이-전수조사로 얻은 최고의 결과를 반영해서 option에 입력
        option[1] = option[1] + bestQuality
        options.append(option)

    return options

def decompse_Half(n, sbox, parDepth):
    nList = list(range(1 <<  n))
    tSbox = sbox
    resultGates = []
    cons = []
    
    now_n = n
    while now_n > 1:
        # 현재 상태에서 조건 설정
        numMadeBlock = 0    # 매 단계마다 1개의 블록을 만들기 때문에 넘치는 상황을 고려하지 않아도 됨

        # now_n에 맞는 블록 만들기 시작
        while numMadeBlock < (2 ** (now_n - 3)): # -2에서 -3으로 해서 절반씩하면 다른 상황이 되도록
            now_parDepth = parDepth[n - now_n]  # now_n에 따라 다른 depth

            # MAKELIST()
            options = makeList_Half(n, n, tSbox, cons, nList, now_parDepth)                     # Half는 n비트 게이트를 다루기 때문에 now_n = n으로 입력

            # CHOOSE()
            now_rows = choose(n, options)

            # 실제 뭉치고, 반영
            result, costs, tSbox, cons, nList = makeBlock(n, n, tSbox, cons, nList, now_rows)   # Half는 n비트 게이트를 다루기 때문에 now_n = n으로 입력
            resultGates += result   # 결과물 게이트 반영

            # block 개수 하나 만든것을 명시
            numMadeBlock += 1
        
        # 비트 하나 줄이기
        now_n -= 1

    return resultGates , tSbox

# default - decompse_Half() + decompse_Full()
def decompose(n, sbox, parDepth):
    resultGates = []

    gates, tSbox = decompse_Half(n, sbox, parDepth)
    resultGates += gates

    gates = decompse_Full(n-1, tSbox[1 << (n-1):], parDepth)
    for step in gates:
        for gate in step:
            # gate 조건 추가 (Tof 이상의 게이트는 왼쪽도 조건으로 추가해야 함)
            if 0 in [c[0] for c in gate[1]]:
                gate[1].append([n-1,1])
    resultGates += gates

    return resultGates

def decompse_only2(sbox):
    # 해당 함수는 2-bit 순열의 항등행렬을 만들기 위한 용
    resultGates = []

    cons = []
    nList = list(range(1 << 2))
    tSbox = sbox

    # 실제 뭉치기
    #region for actual making
    # 실제 뭉치고, 반영 (첫번째 블록)
    result, costs, tSbox, cons, nList = makeBlock(2, 2, tSbox, cons, nList, [0,1])
    for r in result:    # 결과물 게이트 반영
        for gate in r:
            resultGates.append(gate)
    #endregion for actual making
    ###############################################################

    # parity 맞추기
    #region for parity
    options = returnOptions(2, tSbox)
    paritySet = [op[1] for op in options]

    if paritySet.count(1) == 1:
        if tSbox[0] == 0:
            gate = [2-2, [[2-1,1]]]
            tSbox = apply_gate(2, tSbox, gate)
            resultGates.append(gate)
        else:
            gate = [2-2, [[2-1,0]]]
            tSbox = apply_gate(2, tSbox, gate)
            resultGates.append(gate)
    elif paritySet.count(1) == 2:
        gate = [2-2, []]
        tSbox = apply_gate(2, tSbox, gate)
        resultGates.append(gate)
    #endregion for parity
    ###############################################################

    return resultGates

#################################################
def Qube(n, sbox, depths, showFlag):
    resultGates = []
    tSbox = sbox
    totalCost = 0

    if showFlag:
        print("\t", end="")
        for i in range(n):
            print("C{}N".format(i), end="\t")
        print()

    for now_n in range(n, 2, -1):

        # zero collision
        now_gates = zeroCollision_noPrint(now_n, tSbox)
        
        # apply
        nGates = [0 for i in range(n)]
        for now_gate in now_gates:
            tSbox = apply_gate(now_n, tSbox, now_gate)
            nCons = len(now_gate[1])
            if nCons > 1:
                nGates[nCons] += 1
                totalCost += 2 * nCons - 3
            elif nCons == 1:
                nGates[nCons] += 1
            # gate 조정
            n_diff = n - now_n
            now_gate[0] += n_diff
            for cons in now_gate[1]:
                cons[0] += n_diff
        resultGates.append(now_gates)
        
        if showFlag:
            # count and show
            print("C{})".format(now_n), end="\t")
            for num in nGates:
                print(num, end="\t")
            print()

        # block grouping
        now_gates = decompose(now_n, tSbox, depths[n-now_n:])
        
        # apply
        nGates = [0 for i in range(n)]
        for step in now_gates:
            for now_gate in step:
                tSbox = apply_gate(now_n, tSbox, now_gate)
                nCons = len(now_gate[1])
                if nCons > 1:
                    nGates[nCons] += 1
                    totalCost += 2 * nCons - 3
                elif nCons == 1:
                    nGates[nCons] += 1
                # gate 조정
                n_diff = n - now_n
                now_gate[0] += n_diff
                for cons in now_gate[1]:
                    cons[0] += n_diff
        resultGates.append(now_gates)
        
        if showFlag:
            # count and show
            print("G{})".format(now_n), end="\t")
            for num in nGates:
                print(num, end="\t")
            print()
        
        # correcting parities
        gate = [now_n-now_n, [[now_n-1,1]]]
        tSbox = apply_gate(now_n, tSbox, gate)
        # gate 조정
        n_diff = n - now_n
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
        resultGates.append([gate])
        
        if showFlag:
            # count and show
            nGates = [0 for i in range(n)]
            nGates[1] = 1 # partiy에는 하나면 됨 (CN gate)
            print("P{})".format(now_n), end="\t")
            for num in nGates:
                print(num, end="\t")
            print()
        
        # 1-bit 낮추기
        tempSbox = list(range(2**(now_n-1)))
        for i in range(len(tempSbox)):
            tempSbox[i]= int(tSbox[2 * i] / 2)
        tSbox = tempSbox

    # 2-bit에서 identity 만들기
    #region for 2-bit
    gates = decompse_only2(tSbox)

    # 2-bit 결과 apply
    cost = 0
    for gate in gates:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        tSbox = apply_gate(2, tSbox, gate)
        # gate 조정
        n_diff = n - 2
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
    totalCost += cost
    resultGates.append(gates)

    if showFlag:
        # count and show
        print("E2)", end="\t")
        print("[{}]".format(cost))
        print("total Tof cost :", totalCost)
    #endregion for 2-bit
    ##################################################################

    return resultGates

def Qube_quick(n, sbox, depths, showFlag):
    resultGates = []
    tSbox = sbox
    totalCost = 0

    if showFlag:
        print("\t", end="")
        for i in range(n):
            print("C{}N".format(i), end="\t")
        print()

    for now_n in range(n, 2, -1):
        # zero collision
        now_gates = nonInterrupting(now_n, tSbox)
        
        # apply
        nGates = [0 for i in range(n)]
        for now_gate in now_gates:
            tSbox = apply_gate(now_n, tSbox, now_gate)
            nCons = len(now_gate[1])
            if nCons > 1:
                nGates[nCons] += 1
                totalCost += 2 * nCons - 3
            elif nCons == 1:
                nGates[nCons] += 1
            # gate 조정
            n_diff = n - now_n
            now_gate[0] += n_diff
            for cons in now_gate[1]:
                cons[0] += n_diff
        resultGates.append(now_gates)
        
        if showFlag:
            # count and show
            print("C{})".format(now_n), end="\t")
            for num in nGates:
                print(num, end="\t")
            print()

        # block grouping
        now_gates = decompose(now_n, tSbox, depths[n-now_n:])
        
        # apply
        nGates = [0 for i in range(n)]
        for step in now_gates:
            for now_gate in step:
                tSbox = apply_gate(now_n, tSbox, now_gate)
                nCons = len(now_gate[1])
                if nCons > 1:
                    nGates[nCons] += 1
                    totalCost += 2 * nCons - 3
                elif nCons == 1:
                    nGates[nCons] += 1
                # gate 조정
                n_diff = n - now_n
                now_gate[0] += n_diff
                for cons in now_gate[1]:
                    cons[0] += n_diff
        resultGates.append(now_gates)
        
        if showFlag:
            # count and show
            print("G{})".format(now_n), end="\t")
            for num in nGates:
                print(num, end="\t")
            print()
        
        # correcting parities
        gate = [now_n-now_n, [[now_n-1,1]]]
        tSbox = apply_gate(now_n, tSbox, gate)
        # gate 조정
        n_diff = n - now_n
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
        resultGates.append([gate])
        
        if showFlag:
            # count and show
            nGates = [0 for i in range(n)]
            nGates[1] = 1 # partiy에는 하나면 됨 (CN gate)
            print("P{})".format(now_n), end="\t")
            for num in nGates:
                print(num, end="\t")
            print()
        
        # 1-bit 낮추기
        tempSbox = list(range(2**(now_n-1)))
        for i in range(len(tempSbox)):
            tempSbox[i]= int(tSbox[2 * i] / 2)
        tSbox = tempSbox

    # 2-bit에서 identity 만들기
    #region for 2-bit
    gates = decompse_only2(tSbox)

    # 2-bit 결과 apply
    cost = 0
    for gate in gates:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        tSbox = apply_gate(2, tSbox, gate)
        # gate 조정
        n_diff = n - 2
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
    totalCost += cost
    resultGates.append(gates)

    if showFlag:
        # count and show
        print("E2)", end="\t")
        print("[{}]".format(cost))
        print("total Tof cost :", totalCost)
    #endregion for 2-bit
    ##################################################################

    return resultGates
