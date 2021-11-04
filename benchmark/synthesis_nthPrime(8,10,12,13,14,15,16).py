import argparse
import time

from core import *

parser = argparse.ArgumentParser(
    prog="Qube",
    description="Reversible Logic Circuit Sysnthesis Algorithm")

parser.add_argument('path', metavar='File', type=str, help='an target permutation')
parser.add_argument('depths', metavar='N', type=int, nargs='*', help='an integer for the accumulator')
args = parser.parse_args()

# reading a file
FilenameExtension = args.path.split(".")[-1]
if FilenameExtension == "spec":
    permutation = read_spec_file(args.path)
else:
    with open(args.path, "r") as fp:
        data = fp.readline()
    data = data[data.index("[")+1:data.index("]")]
    permutation = [int(n) for n in data.split(", ")]
n = bin(len(permutation)).count('0') - 1

# setting for depths
depths = [0 for i in range(20)]
for i in range(len(args.depths)):
    depths[i] = args.depths[i]
if len(args.depths) != 0:
    for i in range(len(args.depths), n, 1):
        depths[i] = depths[len(args.depths) - 1]

# synthesis for reversible logic circuit
print(time.strftime("%c", time.localtime(time.time())))
resultsGates = []

tpermutation = copy.deepcopy(permutation)
gates = alg_reduction_nthPrime(n, tpermutation, depths)
for step in gates[:-1]:
    for gate in step:
        tpermutation = apply_gate(n, tpermutation, gate)
if gates[-1] != []:
    tpermutation = apply_gate(n, tpermutation, gates[-1])
resultsGates += [[]]
resultsGates += [gates]

# 1-bit 낮추기
ttpermutation = list(range(2**(n-1)))
for i in range(len(ttpermutation)):
    ttpermutation[i]= int(tpermutation[2 * i] / 2)
tpermutation = ttpermutation

# 한 비트 줄인거 synthesis
gates = alg_synthesis(n-1, tpermutation, depths[1:])

# adjusting gates
for i in range(0, len(gates[:-1]), 2):
    # mixing
    for gate in gates[i]:
        n_diff = 1
        gate[0] += n_diff
        for cons in gate[1]:
            cons[0] += n_diff
    
    # decompising
    for j in range(0, len(gates[i+1][:-1]), 2):
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
    # adjusting gate for CX1n
    n_diff = 1
    gates[i+1][-1][0] += n_diff
    for cons in gates[i+1][-1][1]:
        cons[0] += n_diff
# adusting gate for result of 2-bit reudction
for gate in gates[-1]:
    n_diff = 1
    gate[0] += n_diff
    for cons in gate[1]:
        cons[0] += n_diff

resultsGates += gates
print(time.strftime("%c", time.localtime(time.time())))
temp = args.path.split(".")
temp[-2] += "_out"
temp = temp[:-1] + ["real"]
temp = ".".join(temp)
writeRealFormat(n, resultsGates, temp)

# printing related informations
print("Target file\t:", args.path)
print("# of bits\t:", n)
print("Exha. depths\t:", depths[:n])

show_Qube_gates(n, resultsGates)

permutation = apply_Qube_gates(n, permutation, resultsGates)
if permutation != list(range(1 << n)):
    print("Not equal!")
    print(permutation)