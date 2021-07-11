import argparse
import time
from Qube import *
from utils import *

def writeRealFormat_for_URF5(n, gates, fname):
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

        
        for gate in gates[0]:
            strGates = writeGate(n, gate)
            for gate in strGates:
                fp.write(gate + "\n")

        for i in range(0, len(gates[1]), 2):
            for gate in gates[1][i]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")
            for gate in gates[1][i+1]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

        for gate in gates[2]:
            strGates = writeGate(n, gate)
            for gate in strGates:
                fp.write(gate + "\n")
        
        # 쓰기 시작
        for i in range(0, len(gates[3][:-1]), 3):
            # non- interrupting 
            for gate in gates[3][i]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

            # decompising
            for j in range(0, len(gates[3][i+1]), 2):
                for gate in gates[3][i+1][j]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")
                for gate in gates[3][i+1][j+1]:
                    strGates = writeGate(n, gate)
                    for gate in strGates:
                        fp.write(gate + "\n")

            # parity
            for gate in gates[3][i+2]:
                strGates = writeGate(n, gate)
                for gate in strGates:
                    fp.write(gate + "\n")

        # 2-bits
        for gate in gates[3][-1]:
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
gatesForPre = []
if args.nBit == 8:
    # sepecific gates for converting state to 0.5:0.5:0 of nthPrime8
    gatesForPre.append([n-n, [[n-1,1], [n-2,0], [n-3,1], [n-4,0], [n-5,0]]])                    # C^{5}X
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-4,0], [n-5,1], [n-6,0], [n-7,1]]])  # C^{7}X
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-4,1], [n-5,1], [n-6,1]]])           # C^{6}X
elif args.nBit == 9:
    gatesForPre.append([n-n, [[n-1,0], [n-2,0]]])
    gatesForPre.append([n-n, [[n-1,0], [n-2,0], [n-3,1], [n-4,1]]])
    gatesForPre.append([n-n, [[n-1,0], [n-2,0], [n-3,0]]])
    gatesForPre.append([n-n, [[n-1,0], [n-2,1]]])
    gatesForPre.append([n-n, [[n-1,1], [n-2,0], [n-3,0]]])
    gatesForPre.append([n-n, [[n-1,1], [n-2,0], [n-3,1], [n-4,0], [n-5,0]]])
    gatesForPre.append([n-n, [[n-1,0], [n-2,0], [n-3,1], [n-4,1]]])
    gatesForPre.append([n-n, [[n-1,1], [n-2,0], [n-3,1], [n-4,0], [n-5,1], [n-6,0]]])
    gatesForPre.append([n-n, [[n-1,1], [n-2,0], [n-3,1], [n-4,0], [n-5,1], [n-6,0], [n-7,1], [n-8,1]]])
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-5,0], [n-4,0], [n-6,1], [n-7,1]]])
elif args.nBit == 10:
    # sepecific gates for converting state to 0.5:0.5:0 of nthPrime10
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-4,1], [n-5,0], [n-6,0], [n-7,1]]])          # c^{7}X
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-4,0], [n-5,0], [n-6,1], [n-7,0]]])          # c^{7}X
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,0], [n-4,1], [n-5,1], [n-6,1], [n-7,1]]])          # c^{7}X
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-4,1], [n-5,1], [n-6,1], [n-7,0], [n-8,0]]]) # c^{8}X
elif args.nBit == 11:
    gatesForPre.append([n-n, [[n-1,0], [n-2,0], [n-3,0]]])                                                                  # c^{3}X
    gatesForPre.append([n-n, [[n-1,0], [n-2,0], [n-3,1], [n-4,0], [n-5,0]]])                                                # c^{5}X
    gatesForPre.append([n-n, [[n-1,0], [n-2,0], [n-3,1], [n-4,0], [n-5,0], [n-6,1], [n-7,1], [n-8,1]]])                     # c^{8}X
    gatesForPre.append([n-n, [[n-1,0], [n-2,0], [n-3,1], [n-4,0], [n-5,0], [n-6,1], [n-7,1], [n-8,0], [n-9,1], [n-10,1]]])  # c^{10}X

    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-4,1], [n-5,1], [n-6,1], [n-7,1], [n-8,1]]])                     # c^{8}X
    gatesForPre.append([n-n, [[n-1,1], [n-2,1], [n-3,1], [n-4,1], [n-5,0], [n-6,1], [n-7,1]]])                              # c^{7}X
tSbox = copy.deepcopy(sbox)
for gate in gatesForPre:
    tSbox = apply_gate(n, tSbox, gate)
resultsGates.append(gatesForPre)
# 최상위 비트 normal position만 처리
gates = decompose(n, tSbox, depths)
for step in gates:
    for gate in step:
        tSbox = apply_gate(n, tSbox, gate)
resultsGates.append(gates)

gate = [n-n, [[n-1,1]]]
tSbox = apply_gate(n, tSbox, gate)
resultsGates.append([gate])

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
for gate in resultsGates[0]:
    if len(gate[1]) > 1:
        cost += 2 * len(gate[1]) - 3
    sbox = apply_gate(n, sbox, gate)

for i in range(0, len(resultsGates[1]), 2):
    tempCost = 0
    for gate in resultsGates[1][i]:
        if len(gate[1]) > 1:
            tempCost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)
    for gate in resultsGates[1][i+1]:
        if len(gate[1]) > 1:
            tempCost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)
    nowCostsDecomp.append(tempCost)
    cost += tempCost

for gate in resultsGates[2]:
    if len(gate[1]) > 1:
        cost += 2 * len(gate[1]) - 3
    sbox = apply_gate(n, sbox, gate)

# printing related informations
costsDecomp = [[] for i in range(n-2)]
for i in range(0, len(resultsGates[3][:-1]), 3):
    # non- interrupting 
    for gate in resultsGates[3][i]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)
    
    # decompising
    for j in range(0, len(resultsGates[3][i+1]), 2):
        tempCost = 0
        for gate in resultsGates[3][i+1][j]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            sbox = apply_gate(n, sbox, gate)
        for gate in resultsGates[3][i+1][j+1]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            sbox = apply_gate(n, sbox, gate)
        cost += tempCost
        costsDecomp[int(i/3)].append(tempCost)
    
    # parity
    for gate in resultsGates[3][i+2]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)

print()
# 2-bits
for gate in resultsGates[3][-1]:
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
