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

# RCB and LCB is always uptated related to sbox
def check_collision_block(n, RCB, LCB, sbox):
    tempRCB = copy.deepcopy(RCB)
    tempLCB = copy.deepcopy(LCB)
    
    freeEvenCB = 0
    freeOddCB = 0
    freeNormalCB = 0
    
    oneMoreFlag = True
    while oneMoreFlag:
        oneMoreFlag = False # when free interruping-block is, for loop does again.
        breakFlag = False
        for i in range(0, len(tempRCB), 2):
            # break 용
            if breakFlag:
                break
            
            for j in range(0, len(tempLCB), 2):
                if sbox.index(tempRCB[i]) >> 1 == sbox.index(tempLCB[j]) >> 1:
                    freeNormalCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i)
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break 

                if sbox.index(tempRCB[i+1]) >> 1 == sbox.index(tempLCB[j]) >> 1:
                    freeOddCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i)
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break

                if sbox.index(tempRCB[i]) >> 1 == sbox.index(tempLCB[j+1]) >> 1:
                    freeEvenCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i)
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break

                if sbox.index(tempRCB[i+1]) >> 1 == sbox.index(tempLCB[j+1]) >> 1:
                    freeNormalCB += 1
                    tempRCB.pop(i)
                    tempRCB.pop(i)
                    tempLCB.pop(j)
                    tempLCB.pop(j)
                    breakFlag = True
                    oneMoreFlag = True
                    break
                
    return (freeEvenCB, freeOddCB, freeNormalCB)

def makeHalfInterrupting(n, sbox):
    wannaNumCB = 1<<(n-2) if n > 2 else 2 # since returnOptions() function return the half number of row, n-2 is right.
    
    options = returnOptions(n, sbox)
    paritySet = [op[1] for op in options]
    bestDiff = abs(wannaNumCB - paritySet.count(2))
    bestGates = []
    if paritySet.count(2) == wannaNumCB:
        return []

    # restDepth = 0 case
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

    # restDepth > 0 case
    for restDepth in range(1,5,1):
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
        # setting a target
        targets = []
        if paritySet.count(2) < wannaNumCB:
            # find proper one
            for op in options:
                if op[1] != 2:
                    targets += op[0]
        else:
            # find proper one
            for op in options:
                if op[1] == 2:
                    targets += op[0]

        # setting a proper gate
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
    
    # If before code not solve the problem, return results with Toffoli gate used.
    return makeHalfInterruptingMore(n, sbox)

def makeHalfInterruptingMore(n, sbox):
    wannaNumCB = 1<<(n-2) if n > 2 else 2
    
    options = returnOptions(n, sbox)
    paritySet = [op[1] for op in options]
    bestDiff = abs(wannaNumCB - paritySet.count(2))
    bestGates = []
    if paritySet.count(2) == wannaNumCB:
        return []
    
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
        targets = []
        if paritySet.count(2) < wannaNumCB:
            for op in options:
                if op[1] != 2:
                    targets += op[0]
        else:
            for op in options:
                if op[1] == 2:
                    targets += op[0]

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

# preprocess algorithm
def nonInterrupting(n, sbox):
    returnGates = []
    tSbox = sbox
    
    # step 1, mixing
    gates = makeHalfInterrupting(n, sbox)
    for gate in gates:
        tSbox = apply_gate(n, tSbox, gate)
        returnGates.append(gate)

    options = returnOptions(n, tSbox)
    paritySet = [op[1] for op in options]
    evenCB = (paritySet.count(1) - paritySet.count(0)) >> 1 if paritySet.count(1) > paritySet.count(0) else 0
    oddCB = (paritySet.count(0) - paritySet.count(1)) >> 1 if paritySet.count(0) > paritySet.count(1) else 0    
    normalCB = (1<<(n-2)) - max(paritySet.count(0), paritySet.count(1))
    
    # step 2-1, analize about rows at interrupting position.
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
    
    # adjusting for use FREE interrupiting block as possible
    if freeEvenCB > evenCB or freeOddCB > oddCB or freeNormalCB > normalCB:
        while max(freeEvenCB - evenCB, freeOddCB - oddCB) != 0 and normalCB > freeNormalCB:
            normalCB -= 2
            evenCB += 1
            oddCB += 1
    if normalCB < 0:
        normalCB += 2
        evenCB -= 1
        oddCB -= 1
    
    # step 2-2. anaylize abount FREE interrupting block
    CBNumList = []
    madeBlockList = []
    for i in range(0,1<<n,2):
        if tSbox[i] in LCB and tSbox[i+1] in RCB and tSbox[i] not in madeBlockList and tSbox[i+1] not in madeBlockList:
            activeFlag = False
            if tSbox[i] & 1 == tSbox[i+1] & 1:
                if normalCB > 0:
                    # normal collision block
                    activeFlag = True
                    normalCB -= 1
            elif tSbox[i] & 1 == 0:
                if oddCB > 0:
                    # odd collision block (if odd collision block is flipped, then 4 relevant rows numbers at inverted position are generated)
                    activeFlag = True
                    oddCB -= 1
            elif tSbox[i] & 1 == 1:
                if evenCB > 0:
                    # even collision block (if even collision block is flipped, then 4 relevant rows numbers at normal position are generated)
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
    
    # step 2-3. allocating FREE interrupting block
    for i in range(0, len(CBNumList), 2):
        gates = makeLeft(n, tSbox.index(CBNumList[i]), tSbox.index(CBNumList[i+1]), cons)

        for gate in gates:
            tSbox = apply_gate(n, tSbox, gate)
            returnGates.append(gate)

        cons = cons_update(n, cons + [next_position(n, cons)])

    # step 3. constucting interrupting block
    while RCB != []:
        gates = []
        if oddCB > 0:
            #targetRow = [LCB[iL], RCB[iR+1]]
            targetRow = [LCB[0], RCB[1]]

            RightSideLCB = [LCB[i] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i])) >> (n-2) != 0]
            RightSideRCB = [RCB[i+1] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i+1])) >> (n-2) != 0]
            if RightSideLCB != [] and RightSideRCB != []:
                targetRow = [RightSideLCB[0], RightSideRCB[0]]
   
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            oddCB -= 1
            
            # update
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        elif evenCB > 0:
            targetRow = [LCB[1], RCB[0]]

            RightSideLCB = [LCB[i+1] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i+1])) >> (n-2) != 0]
            RightSideRCB = [RCB[i] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i])) >> (n-2) != 0]
            if RightSideLCB != [] and RightSideRCB != []:
                targetRow = [RightSideLCB[0], RightSideRCB[0]]
            
            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            evenCB -= 1
            
            # update
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        else:
            targetRow = [LCB[0], RCB[0]]

            RightSideLCB0 = [LCB[i] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i])) >> (n-2) != 0]
            RightSideRCB0 = [RCB[i] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i])) >> (n-2) != 0]
            RightSideLCB1 = [LCB[i+1] for i in range(0, len(LCB), 2) if (tSbox.index(LCB[i+1])) >> (n-2) != 0]
            RightSideRCB1 = [RCB[i+1] for i in range(0, len(RCB), 2) if (tSbox.index(RCB[i+1])) >> (n-2) != 0]
            if RightSideLCB0 != [] and RightSideRCB0 != []:
                targetRow = [RightSideLCB0[0], RightSideRCB0[0]]
            elif RightSideLCB1 != [] and RightSideRCB1 != []:
                targetRow = [RightSideLCB1[0], RightSideRCB1[0]]

            gates = makeBlock_subroutine(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = makeLeft(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)
            normalCB -= 1
            
            # update
            LCB.remove(targetRow[0])
            LCB.remove(targetRow[0] ^ 1)
            RCB.remove(targetRow[1])
            RCB.remove(targetRow[1] ^ 1)
        
        cons = cons_update(n, cons + [next_position(n, cons)])
          
    # step 4. flipping interrupting blocks by using a one Toffoli gate
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
