# Sepecific parameters of reulsts

There are 10 functions and its synthesized results.

Among functions, URF5.sbox, nthPrime8, nthPrime10 and nthPrime11 have aprent structure that proposed algorithm uses.

Therefore, "systhesis_for_exception.py" is used to synthesize for thess functions.

Sepecific command with parameters are as below.

'''
with synthesis.py)
'''

- URF1.sbox: "python ./synthesis.py ./URF1.sbox 9 1 ..."
- URF2.sbox: "python ./synthesis.py ./URF2.sbox 8 1 ..."
- URF3.sbox: "python ./synthesis.py ./URF3.sbox 10 1 ..."
- URF4.sbox: "python ./synthesis.py ./URF4.sbox 11 1 ..."
- nthPrime7.sbox: "python ./synthesis.py ./nthPrime7.sbox 7 1 ..."
- nthPrime9.sbox: "python ./synthesis.py ./nthPrime9.sbox 9 1 ..."


'''
with synthesis_for_exception.py)
'''

- nthPrime8.sbox: "python ./synthesis_for_exception.py ./nthPrime7.sbox 8 1 ..."
- nthPrime10.sbox: "python ./synthesis_for_exception.py ./nthPrime10.sbox 10 1 ..."
- nthPrime11.sbox: "python ./synthesis_for_exception.py ./nthPrime11.sbox 9 1 ..."
