# Sepecific parameters of reulsts

There are 10 functions and its synthesized results.

Among functions, URF5.sbox, nthPrime8, nthPrime10 and nthPrime11 have **aparent structure** that proposed algorithm uses.

Therefore, "systhesis_for_exception.py" is used to synthesize for these functions.

Sepecific command with parameters are as below.


with synthesis.py)

```
- URF1.sbox: "python ./synthesis.py ./URF1.sbox 9 2 2 2 2 4 4 4 4"
- URF2.sbox: "python ./synthesis.py ./URF2.sbox 8 2 4 4 4 4 4 4"
- URF3.sbox: "python ./synthesis.py ./URF3.sbox 10 1 1 1 1 1 1 1 1 1"
- URF4.sbox: "python ./synthesis.py ./URF4.sbox 11 0"
- nthPrime7.sbox: "python ./synthesis.py ./nthPrime7.sbox 7 4 4 4 4 4 4"
```

with synthesis_for_exception.py)

```
- nthPrime8.sbox: "python ./synthesis_for_exception.py ./nthPrime7.sbox 8 2 2 2 4 4 4 4"
- nthPrime9.sbox: "python ./synthesis_for_exception.py ./nthPrime9.sbox 9 1 1 1 1 1 1 1 1"
- nthPrime10.sbox: "python ./synthesis_for_exception.py ./nthPrime10.sbox 10 1 1 1 1 1 1 1 1 1"
- nthPrime11.sbox: "python ./synthesis_for_exception.py ./nthPrime11.sbox 11 0 0 1 1 1 1 1 1 1 1"
```
