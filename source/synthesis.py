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
gates = alg_synthesis(n, permutation, depths)
print(time.strftime("%c", time.localtime(time.time())))
temp = args.path.split(".")
temp[-2] += "_out"
temp = temp[:-1] + ["real"]
temp = ".".join(temp)
writeRealFormat(n, gates, temp)

# printing related informations
print("Target file\t:", args.path)
print("# of bits\t:", n)
print("Exha. depths\t:", depths[:n-1])

show_Qube_gates(n, gates)

permutation = apply_Qube_gates(n, permutation, gates)
if permutation != list(range(1 << n)):
    print("Not equal!")
    print(permutation)