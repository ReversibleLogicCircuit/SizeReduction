import argparse
import time
from Qube import *
from utils import *

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

# synthesis for reversible logic circuit
print(time.strftime("%c", time.localtime(time.time())))
gates = Qube_quick(n, sbox, depths, True)
print(time.strftime("%c", time.localtime(time.time())))
temp = args.path.split(".")
temp = temp[:-1] + ["real"]
temp = ".".join(temp)
writeRealFormat(n, gates, temp)

# printing related informations
costsDecomp = [[] for i in range(n-2)]
cost = 0
for i in range(0, len(gates[:-1]), 3):
    # non- interrupting 
    for gate in gates[i]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)
    
    # decompising
    for j in range(0, len(gates[i+1]), 2):
        tempCost = 0
        for gate in gates[i+1][j]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            sbox = apply_gate(n, sbox, gate)
        for gate in gates[i+1][j+1]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            sbox = apply_gate(n, sbox, gate)
        cost += tempCost
        costsDecomp[int(i/3)].append(tempCost)
    
    # parity
    for gate in gates[i+2]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        sbox = apply_gate(n, sbox, gate)

print()
# 2-bits
for gate in gates[-1]:
    if len(gate[1]) > 1:
        cost += 2 * len(gate[1]) - 3
    sbox = apply_gate(n, sbox, gate)

if sbox != list(range(1 << n)):
    print("result is not equal!!!")
    print(sbox)
print()

for i in range(len(costsDecomp)):
    print("{}-th decomp".format(n-i), end="\t")
    temp = costsDecomp[i] + [0]
    for j in range(0, len(temp), 32):
        if j != 0: print("\t\t", end="")
        print(temp[j:j+32])
