from itertools import combinations
import copy

# gate example
# X1 = [n-1, []]
# C21 = [n-1, [[n-2,1]]], C2n1 = [n-1, [[n-2,0]]]
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

def makeBlock_subroutine(n, index1, index2, cons):
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

def makeLeft(n, index1, index2, cons):
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

def parity_check(n, cons, gate):
    for con in cons:
        flagNowNonActive = True
        
        for eachCons in gate[1]:
            if (con[n-eachCons[0]-1] != '-') and (con[n-eachCons[0]-1] != str(eachCons[1])):
                flagNowNonActive = False
        
        if flagNowNonActive:
            return False
        
    return True

def writeGate(n, gate):
    strResults = []
    
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
        
        for i in range(0, len(gates[:-1]), 3):
            # non- interrupting 
            for gate in gates[i]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

            # decompising
            for j in range(0, len(gates[i+1]), 2):
                for gate in gates[i+1][j]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")
                for gate in gates[i+1][j+1]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")

            # parity
            for gate in gates[i+2]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

        # 2-bits
        for gate in gates[-1]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")
        
        fp.write(".end")
