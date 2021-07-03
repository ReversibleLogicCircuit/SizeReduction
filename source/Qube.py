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

def makeBlock(n, now_n, sbox, cons, nList, now_rows):
    result = []

    # constructing a block
    gates = makeBlock_subroutine(now_n, sbox[-(1 << now_n):].index(now_rows[0]), sbox[-(1 << now_n):].index(now_rows[1]), cons)
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

# when the number of allocated blocks are bigger than some square of two, it is possible to reduce the size of bit.
# In that case, below function is used rather than makeBlock().
def makeBlock_semi(n, now_n, sbox, cons, nList, now_rows):
    # constructing a block
    gates = makeBlock_subroutine(now_n, sbox.index(now_rows[0]), sbox.index(now_rows[1]), cons)
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
    # sorting a options and returning a one of the best options
    tempOps = sorted(options, key=lambda fun: fun[2], reverse=True)      # sorting the number of free block
    for di in range(len(tempOps[0][1]), 0, -1):                          # sorting for one with free block used first
        tempOps = sorted(tempOps, key=lambda fun: fun[1][di-1])
    tempOps = sorted(tempOps, key=lambda fun: sum(fun[1]))               # sorting the qualities

    return tempOps[0][0]

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
                tempSbox = tempSbox[-(1 << tNow_n):] # reducing permutation to now_n bit
            
            depthExhasutive2(n, tNow_n, tempSbox, tempCons, tempNList, nowQuality, bestQuality, bestBackupQuality, now_d + 1, d)

# default - Full block
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
        FB_list = check_block_changed(nownow_n, tempCons, tempNList, tempSbox)
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
        FB_list = check_block_changed(nownow_n, tempCons, tempNList, tempSbox)
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

def decompse_Full(n, sbox, parDepth):
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

# default - Half block
def makeList_Half(n, now_n, sbox, cons, nList, depth):
    options = []
    for i in range(0, len(nList), 2):
        # For constructing at left side, only constructing with relvant row numbers at normal position.
        if sbox.index(nList[i]) & 1 != 0: # 0으로 고정함
            continue

        nownow_n = copy.deepcopy(now_n)

        option = [[nList[i], nList[i + 1]], [], []]

        tempGates, tempCosts, tempSbox, tempCons, tempNList = makeBlock(n, nownow_n, sbox, cons, nList, [nList[i], nList[i + 1]])

        if tempCons[0] == '0' + '-' * (nownow_n - 1) and nownow_n > 2:
            tempCons = []
            nownow_n -= 1

        option[1].append(sum(tempCosts))
        FB_list = check_block_changed(nownow_n, tempCons, tempNList, tempSbox)
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

def decompse_Half(n, sbox, parDepth):
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

# default - decompse_Half() + decompse_Full()
def decompose(n, sbox, parDepth):
    resultGates = []

    gates, tSbox = decompse_Half(n, sbox, parDepth)
    resultGates += gates

    gates = decompse_Full(n-1, tSbox[1 << (n-1):], parDepth)
    for step in gates:
        for gate in step:
            # adjusting gate
            if 0 in [c[0] for c in gate[1]]:
                gate[1].append([n-1,1])
    resultGates += gates

    return resultGates

def decompse_only2(sbox):
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
        # mixing
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
            # adjusting gate
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

        # decomposition
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
                # adjusting gate
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
        # adjusting gate
        n_diff = n - now_n
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
        resultGates.append([gate])
        
        if showFlag:
            # count and show
            nGates = [0 for i in range(n)]
            nGates[1] = 1 # only one gate is needed for correcting parity (CX gate)
            print("P{})".format(now_n), end="\t")
            for num in nGates:
                print(num, end="\t")
            print()
        
        # bit size is reduced
        tempSbox = list(range(2**(now_n-1)))
        for i in range(len(tempSbox)):
            tempSbox[i]= int(tSbox[2 * i] / 2)
        tSbox = tempSbox

    gates = decompse_only2(tSbox)

    # apply
    cost = 0
    for gate in gates:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        tSbox = apply_gate(2, tSbox, gate)
        # adjusting gate
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

    return resultGates
