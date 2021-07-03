#-*- coding:utf-8 -*-
from itertools import combinations
import copy
#################################################################################

# gate example
# X1 = [n-1, []]
# C21 = [n-1, [[n-2,1]]], C2n1 = [n-1, [[n-2,0]]]
def apply_gate(n, sbox, gate):
    result = copy.deepcopy(sbox)
    pos = [[n-gate[0]-1, '-']] # -1을 해서 index에 맞도록
    for i in range(len(gate[1])):
        pos.append([n-gate[1][i][0]-1, str(gate[1][i][1])]) # -1을 해서 index에 맞도록
    pos = sorted(pos, key=lambda fun: fun[0])
    for i in range(1,len(pos),1):
        pos[i][0] -= i  # 위치 조정
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

#################################################################################

def gate_check(n, cons, gate):
    for con in cons:
        # 일단 현재 con과 겹치는게 있을거라고 생각
        flagNowNonActive = True
        
        # 조건을 확인 해보기 (안될경우 바로 False로 break)
        for eachCons in gate[1]:
            if (con[n-eachCons[0]-1] != '-') and (con[n-eachCons[0]-1] != str(eachCons[1])):
                # gate의 조건이 현재 cons의 con과 비교하였을때 non-active인 경우
                # 해당 con은 더 이상 신경 쓰지 않아도 됨
                flagNowNonActive = False
                break
                
        # 조건 만족시 괜찮은 gate인지 확인
        if flagNowNonActive and (0 in [e[0] for e in gate[1]]):
            # gate가 현재 con과 만족하고
            # gate 조건 중 마지막 비트가 있었으면
            # 해당 gate는 적용 하면 안되는 거라고(False) 반환
            return False

        if flagNowNonActive and (con[n-gate[0]-1] != '-'):
            # 해당 게이트로 앞의 조건의 위치는 바뀌지 않았으면 좋겠음
            # 게이트가 앞의 조건의 위치를 바꿀 경우
            # 해당 gate는 적용하면 안되는 거라고(False) 반환
            return False
        
    return True

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
    
# 열 정보 두 개를 입력받아 조건을 확인하며 block으로 만드는 함수
# 입력
# n: bit 수
# index1, index2: balanced를 만들고 싶은 두 숫자
# cons: conditions
# 출력
# gate의 list를 반환
def makeBlock_subroutine(n, index1, index2, cons):
    gates = []
    nextPos = next_position(n, cons)
    rightPos = int(nextPos[:-1],2)
    strStartDiff = bin((1<<n) + index1 ^ index2)[3:]
    # 왼쪽으로 모이게 하기 위해서 index2가 큰 값으로 만듦
    if index2 < index1:
        temp = index2
        index2 = index1
        index1 = temp
    
    # 이미 block인 입력이 들어왔을 경우
    if strStartDiff[:-1].count('1') == 0:
        return gates
    
    # 1단계, parity 조정
    if strStartDiff[-1] == '0':
        intCon = strStartDiff[:-1].index('1') + 1
        intTar = n
        # 아래는 parity를 Even 상태로 항상 만들기 위한 것
        if bin((1<<n) + index2)[3:][-1] == '0':
            gate = [n-intTar, [[n-intCon,int(bin((1<<n) + index2)[3:][intCon-1])]]]
        else:
            gate = [n-intTar, [[n-intCon,int(bin((1<<n) + index1)[3:][intCon-1])]]]
        gates.append(gate)
        
        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)

    # 2단계, 한 비트만 다르게 만들기
    strNowDiff = bin((1<<n) + index1 ^ index2)[3:-1]
    intCon = strNowDiff.index('1') + 1

    # 2-1단계, 첫 위치 값에 따라서 X 게이트 적용
    if nextPos[intCon - 1] == '1':
        gate = [n-intCon, []]
        gates.append(gate)

        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)

    # 2-2단계, 첫 위치를 타겟으로 바꾸기
    for i in range(strStartDiff[:-1].count('1') - 1):
        strNowDiff = bin((1<<n) + index1 ^ index2)[3:-1]
        intTar = strNowDiff.index('1',intCon) + 1
        gate = [n-intTar, [[n-intCon, 1]]]
        gates.append(gate)

        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)

    # 2-3단계, 첫 위치 값에 따라서 X 게이트 적용(다시)
    if nextPos[intCon - 1] == '1':
        gate = [n-intCon, []]
        gates.append(gate)

        index1 = gate_to_index(n, gate, index1)
        index2 = gate_to_index(n, gate, index2)
    
    strNowDiff = bin((1<<n) + index1 ^ index2)[3:-1]
    # 3단계-1, 맨 처음은 CN으로 적용
    if len(cons) == 0 and strNowDiff.count('1') == 1:
        # 맨 처음용 CN으로 해결하기
        intTar = strNowDiff.index('1') + 1
        intCon = n        
        gate = [n-intTar, [[n-intCon, 1]]]        
        gates.append(gate)
    else:
        intTar = strNowDiff.index('1') + 1
        
        # nexPos와 다른 위치 구하기
        strCheckDiff = bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:] + '1' # 마지막1은 1이 없는거에대한 방지용
        end = strCheckDiff.index('1') + 1
        
        # 조건 구하기
        consList = [i+1 for i in range(0, end, 1) if nextPos[i] == '1']
        
        # 게이트 만들기
        gate = [n-intTar, []]
        for c in consList:
            gate[1].append([n-c,1])
        #if end != n and nextPos.count('1') > len(consList):
        if nextPos.count('1') > len(consList):
            # 해당 게이트는 만들어진 조건의 개수가 더 적을 수 있는 경우
            gate[1].append([n-end, (index1 >> (n-end)) & 0x01])
        gate[1].append([n-n, index2 & 0x01])
        gates.append(gate)
    
    return gates

#################################################################################

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

# recursive 하게 사용되기 위해서는
# sbox가 낮은 level로 들어올때 sbox[16:]과 같이 들어와야 할 듯
def take_two_rows(n, cons, number_list, sbox):
    # 기준 생성
    strCondsAnd = conditions_and(n, cons)
    temp = 1
    intMinRow = 0
    for i in range(len(strCondsAnd)-1,-1,-1):
        if strCondsAnd[i] == '-':
            intMinRow += temp
        temp = temp << 1
    
    for i in range(0,len(number_list),2):
        if sbox.index(number_list[i]) > intMinRow and sbox.index(number_list[i+1]) > intMinRow:
            return (number_list[i], number_list[i+1])
    
    print("그런 쌍 없음 Error")
    
#################################################################################

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
        # 현재 cons에 두 개 이상의 조건이 있고, 그 조건의 '-'의 개수가 같은 경우 합칠 수 있음
        c1 = result.pop()
        c2 = result.pop()
        
        pos = c1.index('-')
        
        result.append(c1[:pos-1] + ('-' * (n-pos+1)))    
    
    return result

def cons_back(n, cons):
    # 되돌아가기 기능에 필요한 cons를 되돌리는 함수    
    result = [c for c in cons]
    
    while result[-1].count('-') != 1:
        pos = result[-1].index('-')
        a = result[-1][:pos] + '0' + result[-1][pos+1:]
        b = result[-1][:pos] + '1' + result[-1][pos+1:]
        result = result[:-1] + [a] + [b]
    
    return result[:-1]

#################################################################################
def makeLeft(n, index1, index2, cons):
    # index2는 사실 필요 없음
    gates = []
    nextPos = next_position(n, cons)
    rightPos = int(nextPos[:-1],2)
    strStartDiff = bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:]
    
    # n = 2인 상황에서 바꾸는 것은 X1로 해결
    if n == 2 and strStartDiff.count('1') == 1:
        gate = [n-1, []]
        gates.append(gate)
        
        return gates
    
    # 1단계, strStartDiff.count('1')  == 1로 만들기
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
            
    # 2단계, 마지막 다른 하나를 바꾸기
    strNowDiff = bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:]
    if strNowDiff.count('1') == 1:
        intTar = strNowDiff.index('1') + 1
        
        consList = [intTar + i + 1 for i in range(len(nextPos[intTar:])) if nextPos[intTar:][i] == '1']
        #print(consList)
        
        #print(nextPos, nextPos[intTar:])
        #print(bin((1<<n) + index1)[3:])
        #print(bin((1<<(n-1)) + rightPos ^ int(index1 >> 1))[3:])
        
        gate = [n-intTar, []]
        for con in consList:
            gate[1].append([n-con, 1])
        
        gates.append(gate)
    
    return gates

#################################################################################

def parity_check(n, cons, gate):
    for con in cons:
        # 일단 현재 con과 겹치는게 있을거라고 생각
        flagNowNonActive = True
        
        # 조건을 확인 해보기 (안될경우 바로 False로 break)
        for eachCons in gate[1]:
            if (con[n-eachCons[0]-1] != '-') and (con[n-eachCons[0]-1] != str(eachCons[1])):
                # gate의 조건이 현재 cons의 con과 비교하였을때 non-active인 경우
                # 해당 con은 더 이상 신경 쓰지 않아도 됨
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
        
        # 쓰기 시작
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
        # 쓰기 끝
        
        fp.write(".end")
