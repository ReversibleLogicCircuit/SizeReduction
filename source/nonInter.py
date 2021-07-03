from itertools import permutations
from itertools import combinations
from utils import *
import copy

def returnOptions(n, sbox):
    options = []
    
    for i in range(0,1<<n,2):
        option = [[i,i+1]]
        nowParitiness = sbox.index(i) % 2 if sbox.index(i) % 2 != sbox.index(i+1) % 2 else 2
        option.append(nowParitiness)

        options.append(option)
    
    return options

# RCB, LCB는 항상 최신화 되어있음
def check_collision_block(n, RCB, LCB, sbox):
    tempRCB = copy.deepcopy(RCB)
    tempLCB = copy.deepcopy(LCB)
    
    freeEvenCB = 0
    freeOddCB = 0
    freeNormalCB = 0
    
    oneMoreFlag = True
    while oneMoreFlag:
        oneMoreFlag = False # 일단 false로 하는데, 뭔가 free CB가 나오면 다시 하도록 하는 것
        breakFlag = False
        for i in range(0, len(tempRCB), 2):
            # break 용
            if breakFlag:
                break
            
            # 두번째 for 문
            for j in range(0, len(tempLCB), 2):
                if sbox.index(tempRCB[i]) >> 1 == sbox.index(tempLCB[j]) >> 1:
                    freeNormalCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i) # pop은 그 index가 나오는거니까 왼쪽처럼 하면 둘다 제거 됨
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break 

                if sbox.index(tempRCB[i+1]) >> 1 == sbox.index(tempLCB[j]) >> 1:
                    freeOddCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i) # pop은 그 index가 나오는거니까 왼쪽처럼 하면 둘다 제거 됨
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break

                if sbox.index(tempRCB[i]) >> 1 == sbox.index(tempLCB[j+1]) >> 1:
                    freeEvenCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i) # pop은 그 index가 나오는거니까 왼쪽처럼 하면 둘다 제거 됨
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break

                if sbox.index(tempRCB[i+1]) >> 1 == sbox.index(tempLCB[j+1]) >> 1:
                    freeNormalCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i) # pop은 그 index가 나오는거니까 왼쪽처럼 하면 둘다 제거 됨
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break
                
    return (freeEvenCB, freeOddCB, freeNormalCB)

def makeHalfInterrupting(n, sbox):
    wannaNumCB = 1<<(n-2) if n > 2 else 2 # n-2인 이유는 returnOptions 산정 방식 차이
    
    options = returnOptions(n, sbox)
    paritySet = [op[1] for op in options]
    bestDiff = abs(wannaNumCB - paritySet.count(2))
    bestGates = []
    if paritySet.count(2) == wannaNumCB:
        # 만약 이미 원하는 상황이 되어 있으면 끝내기
        return []

    # restDepth = 0인 case
    for i in range(1,n-1,1):
        for val in [0,1]:
            tSbox = copy.deepcopy(sbox)
            gate = [n-n, [[n-i, val]]]
            tSbox = apply_gate(n, tSbox, gate)
            options = returnOptions(n, tSbox)
            paritySet = [op[1] for op in options]

            if paritySet.count(2) == wannaNumCB:
                return [gate]
            elif bestDiff < abs(wannaNumCB - paritySet.count(2)):
                bestDiff = abs(wannaNumCB - paritySet.count(2))
                bestGates = [gate]

    # restDepth > 0인 case
    for restDepth in range(1,5,1):  # 1 부터 시작
        for i in range(1,n-1,1):
            cBitsList = list(permutations(list(range(1,n+1,1)),2))
            cBitsList = [c for c in cBitsList if c[1] != n]
            cBitsLists = list(permutations(cBitsList,restDepth))

            for gates in cBitsLists:
                for vals in range(1 << restDepth):
                    tSbox = copy.deepcopy(sbox)
                    tempGates = []
                    for j in range(restDepth):
                        gate = [n-gates[j][1], [[n-gates[j][0], (vals >> j) & 1]]]
                        tempGates.append(gate)
                        tSbox = apply_gate(n, tSbox, gate)
                
                    for val in [0,1]:
                        ttSbox = copy.deepcopy(tSbox)
                        gate = [n-n, [[n-i, val]]]
                        ttSbox = apply_gate(n, ttSbox, gate)
                        options = returnOptions(n, ttSbox)
                        paritySet = [op[1] for op in options]

                        if paritySet.count(2) == wannaNumCB:
                            return tempGates + [gate]
                        elif bestDiff < abs(wannaNumCB - paritySet.count(2)):
                            bestDiff = abs(wannaNumCB - paritySet.count(2))
                            bestGates = tempGates + [gate]

    if paritySet.count(2) != wannaNumCB and bestDiff == 2:
        tSbox = copy.deepcopy(sbox)
        for gate in bestGates:
            tSbox = apply_gate(n, tSbox, gate)
        options = returnOptions(n, tSbox)
        paritySet = [op[1] for op in options]
        # targets 설정
        targets = []
        if paritySet.count(2) < wannaNumCB:
            # normal, inverted position로만 되어있는 것을 찾기
            for op in options:
                if op[1] != 2:
                    targets += op[0]
        else:
            # normal, inverted position로만 되어있는 것을 찾기
            for op in options:
                if op[1] == 2:
                    targets += op[0]

        # 그에 맞는 gate 구성
        gate = []
        for i in range(0, 1 << n, 2):
            if sbox[i] in targets and sbox[i+1] in targets:
                gate = [n-n, []]
                for j in range(n-1,0,-1):
                    gate[1].append([j, (i >> j) & 1])
                break

        tSbox = apply_gate(n,tSbox,gate)
        options = returnOptions(n, tSbox)
        paritySet = [op[1] for op in options]
        if paritySet.count(2) == wannaNumCB:
            returnGates = bestGates + [gate]
            return returnGates
    
    # 위 상황으로 안되는 상황이면
    # Tof 하나를 써서 해보는 상황으로 결과 출력
    return makeHalfInterruptingMore(n, sbox)

def makeHalfInterruptingMore(n, sbox):
    wannaNumCB = 1<<(n-2) if n > 2 else 2 # n-2인 이유는 returnOptions 산정 방식 차이
    
    options = returnOptions(n, sbox)
    paritySet = [op[1] for op in options]
    bestDiff = abs(wannaNumCB - paritySet.count(2))
    bestGates = []
    if paritySet.count(2) == wannaNumCB:
        # 만약 이미 원하는 상황이 되어 있으면 끝내기
        return []
    
    # restDepth = 0 으로 CX ijn을 적용
    conCans = list(range(1,n,1))
    cBitsList = list(combinations(conCans,2))
    for cVals in cBitsList:
        for v1, v2 in [(0,0), (0,1), (1,0), (1,1)]:
            tSbox = copy.deepcopy(sbox)
            gate = [n-n, [[n-cVals[0], v1], [n-cVals[1], v2]]]
            tSbox = apply_gate(n, tSbox, gate)
            options = returnOptions(n, tSbox)
            paritySet = [op[1] for op in options]

            if paritySet.count(2) == wannaNumCB:
                return [gate]
            elif bestDiff < abs(wannaNumCB - paritySet.count(2)):
                    bestDiff = abs(wannaNumCB - paritySet.count(2))
                    bestGates = [gate]

    for i in range(1, n-1, 1):
        conCans = list(range(1,i,1)) + list(range(i+1,n+1,1))
        cBitsList = list(combinations(conCans,2))

        for cVals in cBitsList:
            for v1, v2 in [(0,0), (0,1), (1,0), (1,1)]:
                tSbox = copy.deepcopy(sbox)
                gate = [n-i, [[n-cVals[0], v1], [n-cVals[1], v2]]]
                tSbox = apply_gate(n, tSbox, gate)
                options = returnOptions(n, tSbox)
                paritySet = [op[1] for op in options]

                for restDepth in range(1,4,1):
                    for j in range(1,n-1,1):
                        cBitsListMiddle = list(permutations(list(range(1,n+1,1)),2))
                        cBitsListMiddle = [c for c in cBitsListMiddle if c[1] != n]
                        cBitsListsMiddle = list(permutations(cBitsListMiddle,restDepth))

                        for gates in cBitsListsMiddle:
                            for vals in range(1 << restDepth):
                                ttSbox = copy.deepcopy(tSbox)
                                tempGates = []
                                for j in range(restDepth):
                                    gateMiddle = [n-gates[j][1], [[n-gates[j][0], (vals >> j) & 1]]]
                                    tempGates.append(gateMiddle)
                                    tSbox = apply_gate(n, ttSbox, gateMiddle)
                
                                for val in [0,1]:
                                    tttSbox = copy.deepcopy(ttSbox)
                                    gateLast = [n-n, [[n-i, val]]]
                                    tttSbox = apply_gate(n, tttSbox, gateLast)
                                    options = returnOptions(n, tttSbox)
                                    paritySet = [op[1] for op in options]

                                    if paritySet.count(2) == wannaNumCB:
                                        return [gate] + tempGates + [gateLast]
                                    elif bestDiff < abs(wannaNumCB - paritySet.count(2)):
                                        bestDiff = abs(wannaNumCB - paritySet.count(2))
                                        bestGates = [gate] + tempGates + [gateLast]

    if paritySet.count(2) != wannaNumCB and bestDiff == 2:
        tSbox = copy.deepcopy(sbox)
        for gate in bestGates:
            tSbox = apply_gate(n, tSbox, gate)
        options = returnOptions(n, tSbox)
        paritySet = [op[1] for op in options]
        # targets 설정
        targets = []
        if paritySet.count(2) < wannaNumCB:
            # normal, inverted position로만 되어있는 것을 찾기
            for op in options:
                if op[1] != 2:
                    targets += op[0]
        else:
            # normal, inverted position로만 되어있는 것을 찾기
            for op in options:
                if op[1] == 2:
                    targets += op[0]

        # 그에 맞는 gate 구성
        gate = []
        for i in range(0, 1 << n, 2):
            if sbox[i] in targets and sbox[i+1] in targets:
                gate = [n-n, []]
                for j in range(n-1,0,-1):
                    gate[1].append([j, (i >> j) & 1])
                break


        returnGates = bestGates + [gate]
        return returnGates
    
    return []

def makeHalfInterrupting_before(n, sbox):
    wannaNumCB = 1<<(n-2) if n > 2 else 2 # n-2인 이유는 returnOptions 산정 방식 차이
    
    options = returnOptions(n, sbox)
    paritySet = [op[1] for op in options]
    bestDiff = abs(wannaNumCB - paritySet.count(2))
    bestGates = []
    if paritySet.count(2) == wannaNumCB:
        # 만약 이미 원하는 상황이 되어 있으면 끝내기
        return []

    # restDepth = 0인 case
    for i in range(1,n-1,1):
        for val in [0,1]:
            tSbox = copy.deepcopy(sbox)
            gate = [n-n, [[n-i, val]]]
            tSbox = apply_gate(n, tSbox, gate)
            options = returnOptions(n, tSbox)
            paritySet = [op[1] for op in options]

            if paritySet.count(2) == wannaNumCB:
                return [gate]
            elif bestDiff < abs(wannaNumCB - paritySet.count(2)):
                bestDiff = abs(wannaNumCB - paritySet.count(2))
                bestGates = [gate]

    # restDepth > 0인 case
    for restDepth in range(1,5,1):  # 1 부터 시작
        for i in range(1,n-1,1):
            cBitsList = list(permutations(list(range(1,n+1,1)),2))
            cBitsList = [c for c in cBitsList if c[1] != n]
            cBitsLists = list(permutations(cBitsList,restDepth))

            for gates in cBitsLists:
                for vals in range(1 << restDepth):
                    tSbox = copy.deepcopy(sbox)
                    tempGates = []
                    for j in range(restDepth):
                        gate = [n-gates[j][1], [[n-gates[j][0], (vals >> j) & 1]]]
                        tempGates.append(gate)
                        tSbox = apply_gate(n, tSbox, gate)
                
                    for val in [0,1]:
                        ttSbox = copy.deepcopy(tSbox)
                        gate = [n-n, [[n-i, val]]]
                        ttSbox = apply_gate(n, ttSbox, gate)
                        options = returnOptions(n, ttSbox)
                        paritySet = [op[1] for op in options]

                        if paritySet.count(2) == wannaNumCB:
                            return tempGates + [gate]
                        elif bestDiff < abs(wannaNumCB - paritySet.count(2)):
                            bestDiff = abs(wannaNumCB - paritySet.count(2))
                            bestGates = tempGates + [gate]

    if paritySet.count(2) != wannaNumCB:
        # targets 설정
        targets = []
        if paritySet.count(2) < wannaNumCB:
            # normal, inverted position로만 되어있는 것을 찾기
            for op in options:
                if op[1] != 2:
                    targets += op[0]
        else:
            # normal, inverted position로만 되어있는 것을 찾기
            for op in options:
                if op[1] == 2:
                    targets += op[0]

        # 그에 맞는 gate 구성
        gate = []
        for i in range(0, 1 << n, 2):
            if sbox[i] in targets and sbox[i+1] in targets:
                gate = [n-n, []]
                for j in range(n-1,0,-1):
                    gate[1].append([j, (i >> j) & 1])
                break

        # 적용 및 재귀적 호출
        returnGates = bestGates + [gate]
        return returnGates

def zeroCollision_noPrint(n, sbox):
    returnGates = []
    tSbox = sbox
    
    # 1단계, collision number의 수를 절반으로 조정
    gates = makeHalfInterrupting(n, sbox)
    for gate in gates:
        tSbox = apply_gate(n, tSbox, gate)
        returnGates.append(gate)

    options = returnOptions(n, tSbox)
    paritySet = [op[1] for op in options]
    evenCB = (paritySet.count(1) - paritySet.count(0)) >> 1 if paritySet.count(1) > paritySet.count(0) else 0
    oddCB = (paritySet.count(0) - paritySet.count(1)) >> 1 if paritySet.count(0) > paritySet.count(1) else 0    
    normalCB = (1<<(n-2)) - max(paritySet.count(0), paritySet.count(1))
    
    # 2-1단계, collision block 정보 모으기
    RCB = []
    LCB = []
    cons = []
    for op in options:
        if op[1] == 2:
            if tSbox.index(op[0][0]) % 2 == 0:
                LCB.append(op[0][0])
                LCB.append(op[0][1])
            else:
                RCB.append(op[0][0])
                RCB.append(op[0][1])
    
    # free CB 정보 모으기
    # interrupting position에 있는 네 개의 숫자에서 block형태로 되어 있는 것을 확인하고 저장
    CBNumList = []
    madeBlockList = []
    freeNormalCB = 0
    freeEvenCB = 0
    freeOddCB = 0
    for i in range(0,1<<n,2):
        if tSbox[i] in LCB and tSbox[i+1] in RCB and tSbox[i] not in madeBlockList and tSbox[i+1] not in madeBlockList:
            activeFlag = False
            if tSbox[i] & 1 == tSbox[i+1] & 1:
                activeFlag = True
                freeNormalCB += 1
            elif tSbox[i] & 1 == 0:
                activeFlag = True
                freeOddCB += 1
            elif tSbox[i] & 1 == 1:
                activeFlag = True
                freeEvenCB += 1
            
            if activeFlag:
                CBNumList.append(tSbox[i])
                CBNumList.append(tSbox[i+1])
                
                madeBlockList.append(tSbox[i])
                madeBlockList.append(tSbox[i] ^ 1)
                madeBlockList.append(tSbox[i+1])
                madeBlockList.append(tSbox[i+1] ^ 1)
    
    # 조정1 - free CB 최대한 쓸수있도록 필요한 개수 조정
    if freeEvenCB > evenCB or freeOddCB > oddCB or freeNormalCB > normalCB:
        while max(freeEvenCB - evenCB, freeOddCB - oddCB) != 0 and normalCB > freeNormalCB:
            normalCB -= 2
            evenCB += 1
            oddCB += 1
    if normalCB < 0:
        normalCB += 2
        evenCB -= 1
        oddCB -= 1
    
    # 2-2단계, free collision block 정보 모으기
    # 조정된 개수를 가지고 free interrupting block을 선정
    CBNumList = []
    madeBlockList = []
    for i in range(0,1<<n,2):
        if tSbox[i] in LCB and tSbox[i+1] in RCB and tSbox[i] not in madeBlockList and tSbox[i+1] not in madeBlockList:
            activeFlag = False
            if tSbox[i] & 1 == tSbox[i+1] & 1:
                if normalCB > 0:
                    # collision block 중 (짝,짝)이나 (홀,홀)은 normal collision block
                    activeFlag = True
                    normalCB -= 1
            elif tSbox[i] & 1 == 0:
                if oddCB > 0:
                    # collision block 중 (짝,홀)은 odd collision block
                    # 왜 odd냐면 그걸 뒤집어서 odd이 두 개 생김
                    activeFlag = True
                    oddCB -= 1
            elif tSbox[i] & 1 == 1:
                if evenCB > 0:
                    # collision block 중 (홀,짝)은 even collision block
                    # 왜 even이냐면 그걸 뒤집어서 even이 두 개 생김
                    activeFlag = True
                    evenCB -= 1
            
            if activeFlag:
                CBNumList.append(tSbox[i])
                CBNumList.append(tSbox[i+1])
                
                madeBlockList.append(tSbox[i])
                madeBlockList.append(tSbox[i] ^ 1)
                madeBlockList.append(tSbox[i+1])
                madeBlockList.append(tSbox[i+1] ^ 1)

                LCB.remove(tSbox[i])
                LCB.remove(tSbox[i] ^ 1)
                RCB.remove(tSbox[i+1])
                RCB.remove(tSbox[i+1] ^ 1)
    
    # 2-3단계, free collision block을 왼쪽 정렬
    for i in range(0, len(CBNumList), 2):
        gates = makeLeft(n, tSbox.index(CBNumList[i]), tSbox.index(CBNumList[i+1]), cons)

        for gate in gates:
            tSbox = apply_gate(n, tSbox, gate)
            returnGates.append(gate)

        cons = cons_update(n, cons + [next_position(n, cons)])
    
    # 3단계, unfree collision block 뭉치고 왼쪽 정렬
    while RCB != []:
        gates = []
        if normalCB > 0:
            # normal CB용 정보 전수조사
            options = []
            for iL in range(0,len(LCB),2):
                for iR in range(0,len(RCB),2):
                    option = []
                    gates = makeBlock_subroutine(n, tSbox.index(LCB[iL]), tSbox.index(RCB[iR]), cons)
                    nowCost = 0
                    tempSbox = tSbox
                    for gate in gates:
                        if len(gate[1]) > 1:
                            nowCost += 2 * len(gate[1]) - 3
                        tempSbox = apply_gate(n, tempSbox, gate)
                    gates = makeLeft(n, tempSbox.index(LCB[iL]), tempSbox.index(RCB[iR]), cons)
                    for gate in gates:
                        if len(gate[1]) > 1:
                            nowCost += 2 * len(gate[1]) - 3
                        tempSbox = apply_gate(n, tempSbox, gate)
                    option.append((LCB[iL], RCB[iR]))
                    option.append(nowCost)
                    option.append(check_collision_block(n, RCB, LCB, tempSbox))

                    options.append(option)
            
            # 전수조사에서 선택
            options = sorted(options, key=lambda fun: fun[2][2], reverse=True)
            options = sorted(options, key=lambda fun: fun[1])
            targetRow = options[0][0]
            
            # 동작
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            normalCB -= 1
            
            # 최신화
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        elif evenCB > 0:
            # even CB용 정보 전수조사
            options = []
            for iL in range(0,len(LCB),2):
                for iR in range(0,len(RCB),2):
                    option = []
                    gates = makeBlock_subroutine(n, tSbox.index(LCB[iL+1]), tSbox.index(RCB[iR]), cons)
                    nowCost = 0
                    tempSbox = tSbox
                    for gate in gates:
                        if len(gate[1]) > 1:
                            nowCost += 2 * len(gate[1]) - 3
                        tempSbox = apply_gate(n, tempSbox, gate)
                    gates = makeLeft(n, tSbox.index(LCB[iL+1]), tSbox.index(RCB[iR]), cons)
                    for gate in gates:
                        if len(gate[1]) > 1:
                            nowCost += 2 * len(gate[1]) - 3
                        tempSbox = apply_gate(n, tempSbox, gate)
                    option.append((LCB[iL+1], RCB[iR]))
                    option.append(nowCost)
                    option.append(check_collision_block(n, RCB, LCB, tempSbox))

                    options.append(option)
            
            # 전수조사에서 선택
            options = sorted(options, key=lambda fun: fun[2][2], reverse=True)
            options = sorted(options, key=lambda fun: fun[1])
            targetRow = options[0][0]
            
            # 동작
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            evenCB -= 1
            
            # 최신화
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        else:
            # odd CB용 정보 전수조사
            options = []
            for iL in range(0,len(LCB),2):
                for iR in range(0,len(RCB),2):
                    option = []
                    gates = makeBlock_subroutine(n, tSbox.index(LCB[iL]), tSbox.index(RCB[iR+1]), cons)
                    nowCost = 0
                    tempSbox = tSbox
                    for gate in gates:
                        if len(gate[1]) > 1:
                            nowCost += 2 * len(gate[1]) - 3
                        tempSbox = apply_gate(n, tempSbox, gate)
                    gates = makeLeft(n, tSbox.index(LCB[iL]), tSbox.index(RCB[iR+1]), cons)
                    for gate in gates:
                        if len(gate[1]) > 1:
                            nowCost += 2 * len(gate[1]) - 3
                        tempSbox = apply_gate(n, tempSbox, gate)
                    option.append((LCB[iL], RCB[iR+1]))
                    option.append(nowCost)
                    option.append(check_collision_block(n, RCB, LCB, tempSbox))

                    options.append(option)
            
            # 전수조사에서 선택
            options = sorted(options, key=lambda fun: fun[2][2], reverse=True)
            options = sorted(options, key=lambda fun: fun[1])
            targetRow = options[0][0]
            
            # 동작
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            oddCB -= 1
            
            # 최신화
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        
        cons = cons_update(n, cons + [next_position(n, cons)])
          
    # 4단계, collision block 모두 even or odd block으로 만들기
    gate = [n-n, [[n-1,0], [n-2,0]]] if n != 2 else [0, [[1,0]]]
    returnGates.append(gate)
    tSbox = apply_gate(n, tSbox, gate)
    
    return returnGates

def nonInterrupting(n, sbox):
    returnGates = []
    tSbox = sbox
    
    # 1단계, collision number의 수를 절반으로 조정
    #region for step 1
    gates = makeHalfInterrupting(n, sbox)
    for gate in gates:
        tSbox = apply_gate(n, tSbox, gate)
        returnGates.append(gate)

    options = returnOptions(n, tSbox)
    paritySet = [op[1] for op in options]
    evenCB = (paritySet.count(1) - paritySet.count(0)) >> 1 if paritySet.count(1) > paritySet.count(0) else 0
    oddCB = (paritySet.count(0) - paritySet.count(1)) >> 1 if paritySet.count(0) > paritySet.count(1) else 0    
    normalCB = (1<<(n-2)) - max(paritySet.count(0), paritySet.count(1))
    #endregion for step 1
    ########################################################
    
    # 2-1단계, collision block 정보 모으기
    #region for step 2-1
    RCB = []
    LCB = []
    cons = []
    for op in options:
        if op[1] == 2:
            if tSbox.index(op[0][0]) % 2 == 0:
                LCB.append(op[0][0])
                LCB.append(op[0][1])
            else:
                RCB.append(op[0][0])
                RCB.append(op[0][1])
    
    # free CB 정보 모으기
    # interrupting position에 있는 네 개의 숫자에서 block형태로 되어 있는 것을 확인하고 저장
    CBNumList = []
    madeBlockList = []
    freeNormalCB = 0
    freeEvenCB = 0
    freeOddCB = 0
    for i in range(0,1<<n,2):
        if tSbox[i] in LCB and tSbox[i+1] in RCB and tSbox[i] not in madeBlockList and tSbox[i+1] not in madeBlockList:
            activeFlag = False
            if tSbox[i] & 1 == tSbox[i+1] & 1:
                activeFlag = True
                freeNormalCB += 1
            elif tSbox[i] & 1 == 0:
                activeFlag = True
                freeOddCB += 1
            elif tSbox[i] & 1 == 1:
                activeFlag = True
                freeEvenCB += 1
            
            if activeFlag:
                CBNumList.append(tSbox[i])
                CBNumList.append(tSbox[i+1])
                
                madeBlockList.append(tSbox[i])
                madeBlockList.append(tSbox[i] ^ 1)
                madeBlockList.append(tSbox[i+1])
                madeBlockList.append(tSbox[i+1] ^ 1)
    
    # 조정1 - free CB 최대한 쓸수있도록 필요한 개수 조정
    if freeEvenCB > evenCB or freeOddCB > oddCB or freeNormalCB > normalCB:
        while max(freeEvenCB - evenCB, freeOddCB - oddCB) != 0 and normalCB > freeNormalCB:
            normalCB -= 2
            evenCB += 1
            oddCB += 1
    if normalCB < 0:
        normalCB += 2
        evenCB -= 1
        oddCB -= 1
    #endregion for step 2-1
    ########################################################
    
    # 2-2단계, free collision block 정보 모으기
    #region for step 2-2
    # 조정된 개수를 가지고 free interrupting block을 선정
    CBNumList = []
    madeBlockList = []
    for i in range(0,1<<n,2):
        if tSbox[i] in LCB and tSbox[i+1] in RCB and tSbox[i] not in madeBlockList and tSbox[i+1] not in madeBlockList:
            activeFlag = False
            if tSbox[i] & 1 == tSbox[i+1] & 1:
                if normalCB > 0:
                    # collision block 중 (짝,짝)이나 (홀,홀)은 normal collision block
                    activeFlag = True
                    normalCB -= 1
            elif tSbox[i] & 1 == 0:
                if oddCB > 0:
                    # collision block 중 (짝,홀)은 odd collision block
                    # 왜 odd냐면 그걸 뒤집어서 odd이 두 개 생김
                    activeFlag = True
                    oddCB -= 1
            elif tSbox[i] & 1 == 1:
                if evenCB > 0:
                    # collision block 중 (홀,짝)은 even collision block
                    # 왜 even이냐면 그걸 뒤집어서 even이 두 개 생김
                    activeFlag = True
                    evenCB -= 1
            
            if activeFlag:
                CBNumList.append(tSbox[i])
                CBNumList.append(tSbox[i+1])
                
                madeBlockList.append(tSbox[i])
                madeBlockList.append(tSbox[i] ^ 1)
                madeBlockList.append(tSbox[i+1])
                madeBlockList.append(tSbox[i+1] ^ 1)

                LCB.remove(tSbox[i])
                LCB.remove(tSbox[i] ^ 1)
                RCB.remove(tSbox[i+1])
                RCB.remove(tSbox[i+1] ^ 1)
    #endregion for step 2-2
    ########################################################
    
    # 2-3단계, free collision block을 왼쪽 정렬
    #region for step 2-3
    for i in range(0, len(CBNumList), 2):
        gates = makeLeft(n, tSbox.index(CBNumList[i]), tSbox.index(CBNumList[i+1]), cons)

        for gate in gates:
            tSbox = apply_gate(n, tSbox, gate)
            returnGates.append(gate)

        cons = cons_update(n, cons + [next_position(n, cons)])
    #endregion for step 2-3
    ########################################################
    
    # 3단계, unfree collision block 뭉치고 왼쪽 정렬
    #region for step 3
    while RCB != []:
        gates = []
        if oddCB > 0:
            #targetRow = [LCB[iL], RCB[iR+1]]
            targetRow = [LCB[0], RCB[1]]

            RightSideLCB = [LCB[i] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i])) >> (n-2) != 0]
            RightSideRCB = [RCB[i+1] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i+1])) >> (n-2) != 0]
            if RightSideLCB != [] and RightSideRCB != []:
                targetRow = [RightSideLCB[0], RightSideRCB[0]]
            
            # 동작
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            oddCB -= 1
            
            # 최신화
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        elif evenCB > 0:
            #targetRow = [LCB[iL+1], RCB[iR]]
            targetRow = [LCB[1], RCB[0]]

            RightSideLCB = [LCB[i+1] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i+1])) >> (n-2) != 0]
            RightSideRCB = [RCB[i] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i])) >> (n-2) != 0]
            if RightSideLCB != [] and RightSideRCB != []:
                targetRow = [RightSideLCB[0], RightSideRCB[0]]
            
            # 동작
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            evenCB -= 1
            
            # 최신화
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        else:
            #targetRow = [LCB[iL], RCB[iR]]
            targetRow = [LCB[0], RCB[0]]

            RightSideLCB0 = [LCB[i] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i])) >> (n-2) != 0]
            RightSideRCB0 = [RCB[i] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i])) >> (n-2) != 0]
            RightSideLCB1 = [LCB[i+1] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i+1])) >> (n-2) != 0]
            RightSideRCB1 = [RCB[i+1] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i+1])) >> (n-2) != 0]
            if RightSideLCB0 != [] and RightSideRCB0 != []:
                targetRow = [RightSideLCB0[0], RightSideRCB0[0]]
            elif RightSideLCB1 != [] and RightSideRCB1 != []:
                targetRow = [RightSideLCB1[0], RightSideRCB1[0]]
            
            # 동작
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            normalCB -= 1
            
            # 최신화
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        
        cons = cons_update(n, cons + [next_position(n, cons)])
    #endregion for step 3
    ########################################################
          
    # 4단계, collision block 모두 even or odd block으로 만들기
    gate = [n-n, [[n-1,0], [n-2,0]]] if n != 2 else [0, [[1,0]]]
    returnGates.append(gate)
    tSbox = apply_gate(n, tSbox, gate)
    
    return returnGates

def check_block_changed(n, cons, number_list, sbox):
    result = [[], []]
    for i in range(int(len(number_list) / 2)):
        n1 = sbox.index(number_list[2*i + 0])
        n2 = sbox.index(number_list[2*i + 1])
        
        if bin((1<<n) + n1)[3:-1] == bin((1<<n) + n2)[3:-1]:
            if n1 % 2 == 0:
                # even block
                result[0].append(sbox[n1])
                result[0].append(sbox[n2])
            else:
                # odd block
                result[1].append(sbox[n1])
                result[1].append(sbox[n2])
    return result
