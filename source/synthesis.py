import argparse
import time
from core import *

parser = argparse.ArgumentParser(
    prog="Qube",
    description="Reversible Logic Circuit Sysnthesis Algorithm")

parser.add_argument('path', metavar='File', type=str, help='an target permutation')
parser.add_argument('depths', metavar='N', type=int, nargs='*', help='an integer for the accumulator')
args = parser.parse_args()

def read_spec_file(path):
    result = []
    
    with open(path, "r") as fp:
        data = fp.readlines()
        
    for d in data:
        if d[0] in [".", "#"]:
            continue
            
        result.append(int(d[:-1], 2))      
        
    return result

# reading a file
FilenameExtension = args.path.split(".")[-1]
if FilenameExtension == "spec":
    permutation = read_spec_file(args.path)
else:
    with open(args.path, "r") as fp:
        data = fp.readline()
    permutation = [int(n) for n in data[1:-2].split(", ")]
n = bin(len(permutation)).count('0') - 1

# setting for depths
depths = [0 for i in range(20)]
for i in range(len(args.depths)):
    depths[i] = args.depths[i]
if len(args.depths) != 0:
    for i in range(len(args.depths), n, 1):
        depths[i] = depths[len(args.depths) - 1]

# synthesis for reversible logic circuit
gates = alg_synthesis(n, permutation, depths, True)

# writing the result to .real file
temp = args.path.split(".")
temp[-2] += "_out"
temp = temp[:-1] + ["real"]
temp = ".".join(temp)
writeRealFormat(n, gates, temp)

#####################################################

# printing related informations
print("Target file\t:", args.path)
print("# of bits\t:", n)
print("Exha. depths\t:", depths[:n-1])

# counting the number of Toffoli gate and adjuting to permutation
cost = 0
for i in range(0, len(gates[:-1]), 3):
    # non- interrupting 
    for gate in gates[i]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        permutation = apply_gate(n, permutation, gate)
    
    # decompising
    for j in range(0, len(gates[i+1]), 2):
        tempCost = 0
        for gate in gates[i+1][j]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            permutation = apply_gate(n, permutation, gate)
        for gate in gates[i+1][j+1]:
            if len(gate[1]) > 1:
                tempCost += 2 * len(gate[1]) - 3
            permutation = apply_gate(n, permutation, gate)
        cost += tempCost
    
    # parity
    for gate in gates[i+2]:
        if len(gate[1]) > 1:
            cost += 2 * len(gate[1]) - 3
        permutation = apply_gate(n, permutation, gate)

# 2-bits
for gate in gates[-1]:
    if len(gate[1]) > 1:
        cost += 2 * len(gate[1]) - 3
    permutation = apply_gate(n, permutation, gate)

# checking resulting permutation is equal to identity
if permutation != list(range(1 << n)):
    print("result is not equal!!!")
    print(permutation)

print("Number of Toffoli gate:", cost)
