from itertools import permutations
from itertools import combinations
import copy

def sub_PICK(n, sbox, i):
    m = bin(i + (1 << (n-1)))[3:].index("0") + 1
    k = 0
    for j in range(m):
        k += 1 << (n-2-j)
    
    for j in range(k, (1 << n) - 1, 1):
        a = sbox[j]
        b = a ^ 1
        for l in range(j+1, 1 << n, 1):
            c = sbox[l]
            
            if b == c:
                return (a,b)

def sub_N_PICK(n, sbox, i):
    m = bin(i + (1 << (n-1)))[3:].index("0") + 1
    k = 0
    for j in range(m):
        k += 1 << (n-2-j)
    
    for j in range(k, (1 << n) - 1, 1):
        a = sbox[j]            
        b = a ^ 1        
        if a & 1 != j & 1:
            continue
            
        for l in range(j+1, 1 << n, 1):
            c = sbox[l]
            if b & 1 != l & 1:
                continue
            
            if b == c:
                return (a,b)
            
    for j in range(i << 1, (1 << n) - 1, 1):
        a = sbox[j]
        b = a ^ 1
        
        for l in range(j+1, 1 << n, 1):
            c = sbox[l]
            
            if b == c:
                return (a,b)

def sub_PRE_PICK(n, sbox, i):    
    for j in range(i << 1, (1 << n) - 1, 1):
        a = sbox[j]
        if j & 1 != sbox.index(a ^ 1) & 1:
            continue
            
        for l in range(j+1, 1 << n, 1):
            b = sbox[l]
            if l & 1 != sbox.index(b ^ 1) & 1:
                continue
            
            if j & 1 != l & 1:
                return (a,b)

def sub_CONS(n, index1, index2, cons):
    gates = []
    nextPos = next_position(n, cons)
    rightPos = int(nextPos[:-1],2)
    strStartDiff = bin((1<<n) + index1 ^ index2)[3:]
    # guaranting index1 < index2
    if index2 < index1:
        temp = index2
        index2 = index1
        index1 = temp
    
    # already block case
    if strStartDiff[:-1].count('1') == 0:
        return gates
    
    # step 1. correcting a parity
    if strStartDiff[-1] == '0':
        intCon = strStartDiff[:-1].index('1') + 1
        intTar = n
        # making two rows is at normal position(for intterrupgint rows, normal-like position)
        if bin((1<<n) + index2)[3:][-1] == '0':
            gate = [n-intTar, [[n-intCon,int(bin((1<<n) + index2)[3:][intCon-1])]]]
        else:
            gate = [n-intTar, [[n-intCon,int(bin((1<<n) + index1)[3:][intCon-1])]]]
        gates.append(gate)
        
        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)

    # step 2. making different only two bit(including last bit)
    strNowDiff = bin((1<<n) + index1 ^ index2)[3:-1]
    intCon = strNowDiff.index('1') + 1

    # step 2-1. applying X gate depends on i
    if nextPos[intCon - 1] == '1':
        gate = [n-intCon, []]
        gates.append(gate)

        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)

    # step 2-2. applying CX gate whose conrol bit is first different bit
    for i in range(strStartDiff[:-1].count('1') - 1):
        strNowDiff = bin((1<<n) + index1 ^ index2)[3:-1]
        intTar = strNowDiff.index('1',intCon) + 1
        gate = [n-intTar, [[n-intCon, 1]]]
        gates.append(gate)

        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)

    # step 2-3. applying X gate depends on i(repeating)
    if nextPos[intCon - 1] == '1':
        gate = [n-intCon, []]
        gates.append(gate)

        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)
    
    # step 3-1. applying C^{m}X gate (m = 1, ...)
    strNowDiff = bin((1<<n) + index1 ^ index2)[3:-1]
    if len(cons) == 0 and strNowDiff.count('1') == 1:
        intTar = strNowDiff.index('1') + 1
        intCon = n        
        gate = [n-intTar, [[n-intCon, 1]]]        
        gates.append(gate)
    else:
        intTar = strNowDiff.index('1') + 1
        
        strCheckDiff = bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:] + '1' # last '1' is against empty case.
        end = strCheckDiff.index('1') + 1
        
        consList = [i+1 for i in range(0, end, 1) if nextPos[i] == '1']
        
        # generating proper gate
        gate = [n-intTar, []]
        for c in consList:
            gate[1].append([n-c,1])
        if nextPos.count('1') > len(consList):
            gate[1].append([n-end, (index1 >> (n-end)) & 0x01])
        gate[1].append([n-n, index2 & 0x01])
        gates.append(gate)
    
    return gates

def sub_ALLOC(n, index1, index2, cons):
    # index2 is not used
    gates = []
    nextPos = next_position(n, cons)
    rightPos = int(nextPos[:-1],2)
    strStartDiff = bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:]
    
    if n == 2 and strStartDiff.count('1') == 1:
        gate = [n-1, []]
        gates.append(gate)
        
        return gates
    
    # step 1. making different only one bit
    for i in range(strStartDiff.count('1') - 1):
        strNowDiff = bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:]
        
        intCon = strNowDiff.index('1') + 1
        intTar = strNowDiff.index('1',intCon) + 1
        
        tempCons = [con for con in cons if con[intCon - 1] != '-' and con[intTar - 1] != '-']
        if tempCons == []:
            val = 1
        else:
            val = int(tempCons[0][intCon - 1]) ^ 1
       
        gate = [n-intTar, [[n-intCon, val]]]
        gates.append(gate)
        index1 = gate_to_index(n, gate, index1)
            
    # step 2. applying proper C^{m}X gate (m = 1, ...)
    strNowDiff = bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:]
    if strNowDiff.count('1') == 1:
        intTar = strNowDiff.index('1') + 1
        
        consList = [intTar + i + 1 for i in range(len(nextPos[intTar:])) if nextPos[intTar:][i] == '1']
        
        gate = [n-intTar, []]
        for con in consList:
            gate[1].append([n-con, 1])
        
        gates.append(gate)
    
    return gates

def alg_mixing(n, sbox):
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
    return alg_mixingMore(n, sbox)

def alg_preprocessing(n, sbox):
    returnGates = []
    tSbox = sbox
    
    # step 1, mixing
    gates = alg_mixing(n, sbox)
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
        gates = sub_ALLOC(n, tSbox.index(CBNumList[i]), tSbox.index(CBNumList[i+1]), cons)

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
   
            gates = sub_CONS(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = sub_ALLOC(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
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
            
            gates = sub_CONS(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = sub_ALLOC(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
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

            gates = sub_CONS(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
            for gate in gates:
                tSbox = apply_gate(n, tSbox, gate)
                returnGates.append(gate)

            gates = sub_ALLOC(n, tSbox.index(targetRow[0]), tSbox.index(targetRow[1]), cons)
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

def alg_reduction_prime(n, sbox, parDepth):
    nList = copy.deepcopy(sbox)
    nList.sort()
    tSbox = sbox
    resultGates = []
    
    now_n = n
    while now_n > 1:
        # setting a conditions
        cons = []
        numMadeBlock = 0    # every block is constructed, numMadeBlock increase by one.

        # When constructing a last 8-th block, 3 depth exhaustive searh is done for finding a feature.
        if now_n == 4:
            oddFlag = parityOfSbox(n, tSbox)
            options = makeList2_Full(n, now_n, tSbox, cons, nList, oddFlag, 3)
            options = sorted(options, key=lambda fun: sum(fun[1]))

            # results from exhaustive search is applied.
            for now_rows in [options[0][0]] + options[0][3]:
                result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, now_rows)
                resultGates += result
                numMadeBlock += 1

            # 4-bit is decomposed.
            now_n -= 1
            continue

        while numMadeBlock < (1 << (now_n - 2)):
            now_parDepth = parDepth[n - now_n]  # setting a depth for now_n

            # MAKELIST()
            options = makeList_Full(n, now_n, tSbox, cons, nList, now_parDepth)

            # CHOOSE()
            now_rows = choose(n, options)

            # constructing and allocating a block
            result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, now_rows)
            resultGates += result

            numMadeBlock += 1

            # break for depth exhaustive searh is done for finding a feature.
            if now_n == 5 and numMadeBlock == 7:
                break

        # When constructing a last 9-th block, 4 depth exhaustive searh is done for finding a feature.
        if now_n == 5 and numMadeBlock == 7:
            oddFlag = parityOfSbox(n, tSbox)
            options = makeList2_Full(n, now_n, tSbox, cons, nList, oddFlag, 4)
            options = sorted(options, key=lambda fun: sum(fun[1]))

            # results from exhaustive search is applied.
            result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, options[0][0])
            resultGates += result

            # after last 9-th block is constructed and allocated, now_n is reduced by one.
            cons = []
            now_n -= 1
            numMadeBlock = 0

            for now_rows in options[0][3]:
                result, costs, tSbox, cons, nList = makeBlock(n, now_n, tSbox, cons, nList, now_rows)
                resultGates += result
                numMadeBlock += 1

            # 4-bit is decomposed.
            now_n -= 1
            continue
        
        # reducing a bit
        now_n -= 1

    return resultGates

# default - alg_reduction_for_Left() + alg_reduction_prime()
def alg_reduction(n, sbox, parDepth):
    resultGates = []

    gates, tSbox = alg_reduction_for_Left(n, sbox, parDepth)
    resultGates += gates

    gates = alg_reduction_prime(n-1, tSbox[1 << (n-1):], parDepth)
    for step in gates:
        for gate in step:
            # adjusting gate
            if 0 in [c[0] for c in gate[1]]:
                gate[1].append([n-1,1])
    resultGates += gates

    return resultGates + [[n-n, [[n-1,1]]]]

# synthesis for 2 bits permutation
def alg_serach(sbox):
    # systhesis for 2-bit permutation
    resultGates = []

    cons = []
    nList = list(range(1 << 2))
    tSbox = sbox

    result, costs, tSbox, cons, nList = makeBlock(2, 2, tSbox, cons, nList, [0,1])
    for r in result:
        for gate in r:
            resultGates.append(gate)

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

    return resultGates

# main function
def alg_synthesis(n, sbox, depths):
    resultGates = []
    tSbox = sbox
    totalCost = 0

    for now_n in range(n, 2, -1):
        # mixing
        now_gates = alg_preprocessing(now_n, tSbox)
        
        # apply
        for now_gate in now_gates:
            tSbox = apply_gate(now_n, tSbox, now_gate)
            # adjusting gate
            n_diff = n - now_n
            now_gate[0] += n_diff
            for cons in now_gate[1]:
                cons[0] += n_diff
        resultGates.append(now_gates)

        # decomposition
        now_gates = alg_reduction(now_n, tSbox, depths[n-now_n:])
        
        # apply
        for step in now_gates[:-1]:
            for now_gate in step:
                tSbox = apply_gate(now_n, tSbox, now_gate)
                # adjusting gate
                n_diff = n - now_n
                now_gate[0] += n_diff
                for cons in now_gate[1]:
                    cons[0] += n_diff
        # adjusting gate for CX1n
        n_diff = n - now_n
        now_gates[-1][0] += n_diff
        for cons in now_gates[-1][1]:
            cons[0] += n_diff
        resultGates.append(now_gates)
        
        # bit size is reduced
        tempSbox = list(range(2**(now_n-1)))
        for i in range(len(tempSbox)):
            tempSbox[i]= int(tSbox[2 * i] / 2)
        tSbox = tempSbox
        #print("P_{} -> P_{} (=".format(now_n, now_n-1), tSbox, ")")

    gates = alg_serach(tSbox)

    # apply
    for gate in gates:
        tSbox = apply_gate(2, tSbox, gate)
        # adjusting gate
        n_diff = n - 2
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
    resultGates.append(gates)

    return resultGates

############################################################################

# gate example
# X1 = [n-1, []]
# C21 = [n-1, [[n-2,1]]], X2 C21 X2 = [n-1, [[n-2,0]]]
def apply_gate(n, sbox, gate):
    result = copy.deepcopy(sbox)
    pos = [[n-gate[0]-1, '-']] # by decreasing one, it matches
    for i in range(len(gate[1])):
        pos.append([n-gate[1][i][0]-1, str(gate[1][i][1])])
    pos = sorted(pos, key=lambda fun: fun[0])
    for i in range(1,len(pos),1):
        pos[i][0] -= i  # adjusting a postion
    num = n - len(pos)
    
    for i in range(1 << num):
        vals = bin((1 << num) + i)[3:]
        tarNum = vals[:pos[0][0]] + pos[0][1]
        for j in range(len(pos) - 1):
            tarNum += vals[pos[j][0]:pos[j+1][0]]+ pos[j+1][1]
        tarNum += vals[pos[-1][0]:]
                
        tarPos = tarNum.index("-")
        num1 = int("0b" + tarNum[:tarPos] + "0" + tarNum[tarPos+1:], 2)
        num2 = int("0b" + tarNum[:tarPos] + "1" + tarNum[tarPos+1:], 2)

        temp = result[num1]
        result[num1] = result[num2]
        result[num2] = temp
    
    return result

def gate_to_index(n, gate, index):
    strIndex = bin((1<<n) + index)[3:]
    flagActive = True
    
    for con in gate[1]:
        if strIndex[n-con[0]-1] != str(con[1]):
            flagActive = False
            break
    
    if flagActive:
        return index ^ (1<<(gate[0]))
    else:
        return index

def conditions_and(n, cons):
    result = ''
    for i in range(n):
        temp = '0'
        flag = True
        for con in cons:
            if con[i] != '0':
                flag = False
                break
        if flag == False:
            result = result + '-'
        else:
            result = result + '0'
    return result

def check_block(n, cons, number_list, sbox):
    result = []
    for i in range(int(len(number_list) / 2)):
        n1 = sbox.index(number_list[2*i + 0])
        n2 = sbox.index(number_list[2*i + 1])
        
        if bin(2**n + n1)[3:-1] == bin(2**n + n2)[3:-1]:
            result.append(sbox[n1])
            result.append(sbox[n2])
    return result

def next_position(n, cons):
    if cons == []:
        return '0'*(n-1) + '-'
    
    target = cons[-1]
    pos = target.index('-')
    
    result = target[:pos - 1] + '1' + ('0' * (n - pos - 1)) + '-'
    
    return result

def cons_update(n, cons):
    result = [c for c in cons]
    
    while len(result) > 1 and result[-1].count('-') == result[-2].count('-'):
        c1 = result.pop()
        c2 = result.pop()
        
        pos = c1.index('-')
        
        result.append(c1[:pos-1] + ('-' * (n-pos+1)))    
    
    return result

def cons_back(n, cons):    
    result = [c for c in cons]
    
    while result[-1].count('-') != 1:
        pos = result[-1].index('-')
        a = result[-1][:pos] + '0' + result[-1][pos+1:]
        b = result[-1][:pos] + '1' + result[-1][pos+1:]
        result = result[:-1] + [a] + [b]
    
    return result[:-1]

def parity_check(n, cons, gate):
    for con in cons:
        flagNowNonActive = True
        
        for eachCons in gate[1]:
            if (con[n-eachCons[0]-1] != '-') and (con[n-eachCons[0]-1] != str(eachCons[1])):
                flagNowNonActive = False
        
        if flagNowNonActive:
            return False
        
    return True

def returnOptions(n, sbox):
    options = []
    
    for i in range(0,1<<n,2):
        option = [[i,i+1]]
        nowParitiness = sbox.index(i) % 2 if sbox.index(i) % 2 != sbox.index(i+1) % 2 else 2
        option.append(nowParitiness)

        options.append(option)
    
    return options

def alg_mixingMore(n, sbox):
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

def FBList(n, cons, number_list, sbox):
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

# with alg_CONS and alg_ALLOC, it make and allocate block with entered rows
def makeBlock(n, now_n, sbox, cons, nList, now_rows):
    result = []

    # constructing a block
    gates = sub_CONS(now_n, sbox[-(1 << now_n):].index(now_rows[0]), sbox[-(1 << now_n):].index(now_rows[1]), cons)
    if now_n != n and gates != []:
        for j in range(n - now_n):
            gates[-1][1].append([n - 1 - j,1]) # adjusting to appropriate gate
    result.append(gates)
    costGB = 0
    for j in range(len(gates)):
        sbox = apply_gate(n, sbox, gates[j])
        if len(gates[j][1]) > 1:
            costGB += 2 * len(gates[j][1]) - 3

    # allocating a block
    gates = sub_ALLOC(now_n, sbox[-(1 << now_n):].index(now_rows[0]), sbox[-(1 << now_n):].index(now_rows[1]), cons)
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

# when the number of allocated blocks are bigger than some square of two, it is possible to reduce the size of bit.
# In that case, below function is used rather than makeBlock().
def makeBlock_semi(n, now_n, sbox, cons, nList, now_rows):
    # constructing a block
    gates = sub_CONS(now_n, sbox.index(now_rows[0]), sbox.index(now_rows[1]), cons)
    costGB = 0
    if now_n != n and gates != []:
        for j in range(0, len(gates)-1, 1):
            sbox = apply_gate(now_n, sbox, gates[j])
            if len(gates[j][1]) > 1:
                costGB += 2 * len(gates[j][1]) - 3
        # the last gate is counted.
        sbox = apply_gate(now_n, sbox, gates[-1])
        costGB += 2 * (len(gates[-1][1]) + n - now_n) - 3 # adjusting quality of last gate
    else:
        for j in range(0, len(gates), 1):
            sbox = apply_gate(now_n, sbox, gates[j])
            if len(gates[j][1]) > 1:
                costGB += 2 * len(gates[j][1]) - 3

    # allocating a block
    gates = sub_ALLOC(now_n, sbox.index(now_rows[0]), sbox.index(now_rows[1]), cons)
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
    # sorting a options and returning a one of the best options
    tempOps = sorted(options, key=lambda fun: fun[2], reverse=True)      # sorting the number of free block
    for di in range(len(tempOps[0][1]), 0, -1):                          # sorting for one with free block used first
        tempOps = sorted(tempOps, key=lambda fun: fun[1][di-1])
    tempOps = sorted(tempOps, key=lambda fun: sum(fun[1]))               # sorting the qualities

    return tempOps[0][0]

##############################
# depth exhaustive search 
##############################
# depth exhaustive search (using recursive function)
# nowQuality and BestQuality must be defiend as length is depth
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
                tempSbox = tempSbox[-(1 << tNow_n):] # reducing permutation to now_n bit
            
            depthExhasutive(n, tNow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, now_d + 1, d)

# ex) d=3, nowQuality = [[10, 10, 10], [...]], bestQuality = [[10, 10, 10], [...]]
def depthExhasutive2(n, now_n, sbox, cons, nList, nowQuality, bestQuality, bestBackupQuality, now_d, d):
    if now_d == d:
        # depthExhasutive2 is only used to arrive here only when sbox is 3-bit
        FB_List = FBList(3, [], nList, sbox)

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
                tempSbox = tempSbox[-(1 << tNow_n):] # reducing permutation to now_n bit
            
            depthExhasutive2(n, tNow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, bestBackupQuality, now_d + 1, d)

# default - Full block
# full means that it only has normalr or inverted postions
def makeList_Full(n, now_n, sbox, cons, nList, depth):
    options = []
    sbox = sbox[-(1 << now_n):] # reducing permutation to now_n bit
    for i in range(0, len(nList), 2):
        nownow_n = copy.deepcopy(now_n)

        option = [[nList[i], nList[i + 1]], [], []]

        # constructing a block with makeBlock_semi() function
        # the process is done after the block is really constructed.
        tempCosts, tempSbox, tempCons, tempNList = makeBlock_semi(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])

        if tempCons[0] == '0' + '-' * (nownow_n - 1) and nownow_n > 2:
            tempCons = []
            nownow_n -= 1
            tempSbox = tempSbox[-(1 << nownow_n):] # reducing permutation to now_n bit
            
        option[1].append(sum(tempCosts))
        FB_list = FBList(nownow_n, tempCons, tempNList, tempSbox)
        option[2] = max([len(FB_list[0]) >> 1,len(FB_list[1]) >> 1])    # In Full case, max is fine.
        
        if depth == 0:
            options.append(option)
            continue

        # Stating depth exhaustive search
        tDepth = depth
        if depth > (len(tempNList) >> 1):
            tDepth = len(tempNList) >> 1

        nowQuality = [100 for j in range(tDepth)]
        bestQuality = [100 for j in range(tDepth)]

        depthExhasutive(n, nownow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, 0, tDepth)

        option[1] = option[1] + bestQuality
        options.append(option)

    return options

def makeList2_Full(n, now_n, sbox, cons, nList, oddFlag, depth):
    options = []
    sbox = sbox[-(1 << now_n):] # reducing permutation to now_n bit
    for i in range(0, len(nList), 2):
        nownow_n = copy.deepcopy(now_n)
        toddFlag = copy.deepcopy(oddFlag)

        option = [[nList[i], nList[i + 1]], [], [], []]

        # constructing a block with makeBlock_semi() function
        # the process is done after the block is really constructed.
        tempCosts, tempSbox, tempCons, tempNList = makeBlock_semi(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])

        if tempCons[0] == '0' + '-' * (nownow_n - 1) and nownow_n > 2:
            tempCons = []
            nownow_n -= 1
            tempSbox = tempSbox[-(1 << nownow_n):] # reducing permutation to now_n bit
            if tempCosts[0] == 2 * (n-1) - 3:
                toddFlag = False if toddFlag else True

        option[1].append(sum(tempCosts))
        FB_list = FBList(nownow_n, tempCons, tempNList, tempSbox)
        option[2] = max([len(FB_list[0]) >> 1,len(FB_list[1]) >> 1]) # In Full case, max is fine.

        if depth == 0:
            options.append(option)
            continue

        # Stating depth exhaustive search
        tDepth = depth
        if depth > (len(tempNList) >> 1):
            tDepth = len(tempNList) >> 1

        nowQuality = [[10000 for j in range(tDepth)], [0 for j in range(tDepth)]]
        bestQuality = [[10000 for j in range(tDepth)], [0 for j in range(tDepth)]]
        bestBackupQuality = [[10000 for j in range(tDepth)], [0 for j in range(tDepth)]]

        depthExhasutive2(n, nownow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, bestBackupQuality, 0, tDepth)

        # updating the result with best one
        if 10000 not in bestQuality[0]:
            option[1] = option[1] + bestQuality[0]
            option[3] = bestQuality[1]
            options.append(option)

            # it can predict last four block's quality, because of the feature.
            if toddFlag and option[1][-1] != 2 * (n-1) - 3:
                option[1] += [2 * (n-1) - 5, 0, 2 * (n-1) - 3, 0]
            else:
                option[1] += [2 * (n-1) - 5, 0, 0, 0]
        else:
            option[1] = option[1] + bestBackupQuality[0]
            option[3] = bestBackupQuality[1]
            options.append(option)

    return options

# default - Half block
# half means that it has normal postion half and the other is inverted postion
def makeList_Half(n, now_n, sbox, cons, nList, depth):
    options = []
    for i in range(0, len(nList), 2):
        # For constructing at left side, only constructing with relvant row numbers at normal position.
        if sbox.index(nList[i]) & 1 != 0: # 0���� ������
            continue

        nownow_n = copy.deepcopy(now_n)

        option = [[nList[i], nList[i + 1]], [], []]

        tempGates, tempCosts, tempSbox, tempCons, tempNList = makeBlock(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])

        if tempCons[0] == '0' + '-' * (nownow_n - 1) and nownow_n > 2:
            tempCons = []
            nownow_n -= 1

        option[1].append(sum(tempCosts))
        FB_list = FBList(nownow_n, tempCons, tempNList, tempSbox)
        option[2] = len(FB_list[0]) >> 1 # the number of free block related with normalr postion

        if depth == 0:
            options.append(option)
            continue

        # only considering candidates at normal positions
        tempEvenList = [tempNList[i] for i in range(len(tempNList)) if tempSbox.index(tempNList[i]) & 1 == ((i & 1) ^ 0)]

        # starting a depth exhaustive search
        tDepth = depth
        if depth > (len(tempEvenList) >> 1):
            tDepth = len(tempEvenList) >> 1

        nowQuality = [100 for j in range(tDepth)]
        bestQuality = [100 for j in range(tDepth)]

        depthExhasutive(n, nownow_n, tempSbox, tempCons, tempEvenList, nowQuality, bestQuality, 0, tDepth)
        
        option[1] = option[1] + bestQuality
        options.append(option)

    return options

def alg_reduction_for_Left(n, sbox, parDepth):
    nList = list(range(1 <<  n))
    tSbox = sbox
    resultGates = []
    cons = []
    
    now_n = n
    while now_n > 1:
        numMadeBlock = 0

        # since half of block is already constructed and allocated, consider only lefted block.
        while numMadeBlock < (2 ** (now_n - 3)):
            now_parDepth = parDepth[n - now_n]

            # MAKELIST()
            options = makeList_Half(n, n, tSbox, cons, nList, now_parDepth) # this function treats n-bit permutation, and thus now_n = n

            # CHOOSE()
            now_rows = choose(n, options)

            result, costs, tSbox, cons, nList = makeBlock(n, n, tSbox, cons, nList, now_rows) # this function treats n-bit permutation, and thus now_n = n
            resultGates += result

            numMadeBlock += 1
        
        now_n -= 1

    return resultGates , tSbox

def apply_Qube_gates(n, sbox, gates):
    # (n ~ 3)-bit
    for i in range(0, len(gates[:-1]), 2):
        # non- interrupting 
        for gate in gates[i]:
            sbox = apply_gate(n, sbox, gate)
    
        # decompising
        for j in range(0, len(gates[i+1][:-1]), 2):
            for gate in gates[i+1][j]:
                sbox = apply_gate(n, sbox, gate)
            for gate in gates[i+1][j+1]:
                sbox = apply_gate(n, sbox, gate)
        if gates[i+1][-1] != []:
            sbox = apply_gate(n, sbox, gates[i+1][-1])

    # 2-bits
    for gate in gates[-1]:
        sbox = apply_gate(n, sbox, gate)

    return sbox

##############################
# saving gates to .real
##############################
def writeGate(n, gate):
    strResults = []

    if gate == []:
        return []
    
    if len(gate[1]) == 0:
        strResults.append("t1 x{}".format(n - gate[0]))
    else:
        strGate = "t{} ".format(len(gate[1]) + 1)    
        for c in gate[1]:
            strGate += "x{} ".format(n - c[0])
        strGate += "x{}".format(n - gate[0])

        for c in gate[1]:
            if c[1] == 0:
                strResults.append("t1 x{}".format(n - c[0]))

        strResults = strResults + [strGate] + strResults
    
    return strResults

def writeRealFormat(n, gates, fname):
    with open(fname, "w") as fp:
        fp.write(".version 2.0\n")
        fp.write(".numvars {}\n".format(n))
        temp = ".variables "
        for i in range(n):
            temp += "x{} ".format(i+1)
        fp.write(temp[:-1] + "\n")
        temp = ".inputs "
        for i in range(n):
            temp += "i{} ".format(i+1)
        fp.write(temp[:-1] + "\n")
        temp = ".outputs "
        for i in range(n):
            temp += "o{} ".format(i+1)
        fp.write(temp[:-1] + "\n")
        fp.write(".constants " + "-" * n + "\n")
        fp.write(".garbage " + "-" * n + "\n")
        fp.write(".begin\n")
        
        for i in range(0, len(gates[:-1]), 2):
            # non- interrupting 
            for gate in gates[i]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

            # decompising
            for j in range(0, len(gates[i+1][:-1]), 2):
                for gate in gates[i+1][j]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")
                for gate in gates[i+1][j+1]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")
            strGates = writeGate(n, gates[i+1][-1])
            for gate in strGates:
                fp.write(gate + "\n")

        # 2-bits
        for gate in gates[-1]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")
        
        fp.write(".end")

def show_Qube_gates(n, gates):
    numTof = 0
    numTofDecomp = [[] for i in range(n-2)]

    print("\t", end="")
    for i in range(n):
        print("C{}X".format(i), end="\t")
    print()

    for i in range(0, len(gates[:-1]), 2):
        # preprocessing
        nGates = [0 for i in range(n)]
        for gate in gates[i]:
            nCons = len(gate[1])
            if nCons > 1:
                numTof += 2 * nCons - 3
            nGates[nCons] += 1
        
        # preprocessing results print
        print("P{})".format(n - int(i/2)), end="\t")
        for num in nGates:
            print(num, end="\t")
        print()
    
        # decompising
        nGates = [0 for i in range(n)]
        for j in range(0, len(gates[i+1][:-1]), 2):
            tempNum = 0
            for gate in gates[i+1][j]:
                nCons = len(gate[1])
                if nCons > 1:
                    tempNum += 2 * nCons - 3
                nGates[nCons] += 1
            for gate in gates[i+1][j+1]:
                nCons = len(gate[1])
                if nCons > 1:
                    tempNum += 2 * nCons - 3
                nGates[nCons] += 1
            numTof += tempNum
            numTofDecomp[int(i/2)].append(tempNum)
        nGates[1] += 1

        print("R{})".format(n - int(i/2)), end="\t")
        for num in nGates:
            print(num, end="\t")
        print()

    # 2-bits
    nGates = [0 for i in range(n)]
    for gate in gates[-1]:
        nCons = len(gate[1])
        if nCons > 1:
            numTof += 2 * nCons - 3
        nGates[nCons] += 1

    print("E2)", end="\t")
    for num in nGates:
        print(num, end="\t")
    print()

    print("Number of Toffoli gate:", numTof)
    #print()

    #for i in range(len(numTofDecomp)):
    #    print("{}-th decomp".format(n-i), end="\t")
    #    temp = numTofDecomp[i] + [0]
    #    for j in range(0, len(temp), 32):
    #        if j != 0: print("\t\t", end="")
    #        print(temp[j:j+32])