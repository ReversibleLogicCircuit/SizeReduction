import argparse
import time
from Qube import *
from utils import *

def writeRealFormat_for_URF5(n, gates, fname):
    with open(fname, "w") as fp:
        fp.write(".version 2.0\n")
        fp.write(",numvars {}\n".format(n))
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

        for j in range(0, len(gates[0]), 2):
            for gate in gates[0][i]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")
            for gate in gates[0][i+1]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")
        
        # 쓰기 시작
        for i in range(0, len(gates[1][:-1]), 3):
            # non- interrupting 
            for gate in gates[1][i]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

            # decompising
            for j in range(0, len(gates[1][i+1]), 2):
                for gate in gates[1][i+1][j]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")
                for gate in gates[1][i+1][j+1]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")

            # parity
            for gate in gates[1][i+2]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

        # 2-bits
        for gate in gates[1][-1]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")
        # 쓰기 끝
        
        fp.write(".end")

parser = argparse.ArgumentParser(
    prog="Qube",
    description="Reversible Logic Circuit Sysnthesis Algorithm",
    epilog=
        '''
        This message is for epliog.
        ''')

parser.add_argument('path', metavar='File', type=str, help='an target permutation')
parser.add_argument('nBit', metavar='B', type=int, help='the number of bit')
parser.add_argument('depths', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
args = parser.parse_args()

# setting for depths
depths = [0 for i in range(20)]
for i in range(len(args.depths)):
    depths[i] = args.depths[i]

print("Target file\t:", args.path)
print("# of bits\t:", args.nBit)
print("Exha. depths\t:", depths[:args.nBit-1])

# reading a file
with open(args.path, "r") as fp:
    data = fp.readline()
sbox = [int(n) for n in data[1:-1].split(", ")]
n = args.nBit

resultsGates = []
# synthesis for reversible logic circuit
print(time.strftime("%c", time.localtime(time.time())))
# 최상위 비트 normal position만 처리
gates = decompse_Full(n, sbox, depths)
tSbox = copy.deepcopy(sbox)
for step in gates:
    for gate in step:
        tSbox = apply_gate(n, tSbox, gate)
resultsGates.append(gates)

# 1-bit 낮추기
ttSbox = list(range(2**(n-1)))
for i in range(len(ttSbox)):
    ttSbox[i]= int(tSbox[2 * i] / 2)
tSbox = ttSbox

# 한 비트 줄인거 synthesis
gates = Qube_quick(n-1, tSbox, depths[1:], True)

# 게이트 조정
for i in range(0, len(gates[:-1]), 3):
    # non- interrupting 
    for gate in gates[i]:
        n_diff = 1
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
    
    # decompising
    for j in range(0, len(gates[i+1]), 2):
        for gate in gates[i+1][j]:
            n_diff = 1
            gate[0] += n_diff
            for cons in gate[1]:
                cons[0] += n_diff
        for gate in gates[i+1][j+1]:
            n_diff = 1
            gate[0] += n_diff
            for cons in gate[1]:
                cons[0] += n_diff
    
    # parity
    for gate in gates[i+2]:
        n_diff = 1
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff

for gate in gates[-1]:
    n_diff = 1
    gate[0] += n_diff
    for cons in gate[1]:
        cons[0] += n_diff
resultsGates.append(gates)
print(time.strftime("%c", time.localtime(time.time())))
temp = args.path.split(".")
temp = temp[:-1] + ["real"]
temp = ".".join(temp)
writeRealFormat_for_URF5(n, resultsGates, temp)

nowCostsDecomp = []
cost = 0
for i in range(0, len(resultsGates[0]), 2):
    tempCost = 0
    for gate in resultsGates[0][i]:
        if len(gate[1]) > 1:
            tempCost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)
    for gate in resultsGates[0][i+1]:
        if len(gate[1]) > 1:
            tempCost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)
    nowCostsDecomp.append(tempCost)
    cost += tempCost

# printing related informations
costsDecomp = [[] for i in range(n-2)]
for i in range(0, len(resultsGates[1][:-1]), 3):
    # non- interrupting 
    for gate in resultsGates[1][i]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)
    
    # decompising
    for j in range(0, len(resultsGates[1][i+1]), 2):
        tempCost = 0
        for gate in resultsGates[1][i+1][j]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            sbox = apply_gate(n, sbox, gate)
        for gate in resultsGates[1][i+1][j+1]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            sbox = apply_gate(n, sbox, gate)
        cost += tempCost
        costsDecomp[int(i/3)].append(tempCost)
    
    # parity
    for gate in resultsGates[1][i+2]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)

print()
# 2-bits
for gate in resultsGates[1][-1]:
    if len(gate[1]) > 1:
        cost += 2 * len(gate[1]) - 3
    sbox = apply_gate(n, sbox, gate)

print(cost)
if sbox != list(range(1 << n)):
    print("result is not equal!!!")
    print(sbox)
print()

costsDecomp = [nowCostsDecomp] + costsDecomp
for i in range(len(costsDecomp)):
    print("{}-th decomp".format(n-i), end="\t")
    temp = costsDecomp[i] + [0]
    for j in range(0, len(temp), 32):
        if j != 0: print("\t\t", end="")
        print(temp[j:j+32])
