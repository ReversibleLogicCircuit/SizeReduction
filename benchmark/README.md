# Benchmarks

For URF1, URF2, URF3, URF4, and nthPrime7, following d_n options have been applied.

```
/benchmark$ python ../source/synthesis.py ./URF1.function
/benchmark$ python ../source/synthesis.py ./URF2.sbox
/benchmark$ python ../source/synthesis.py ./URF3.sbox 1
/benchmark$ python ../source/synthesis.py ./URF4.sbox
/benchmark$ python ../source/synthesis.py ./nthPrime7.sbox
```

URF5 is somewhat structured; all row numbers are at normal positions. To utilize it, we have used
```
/benchmark$ python ./synthesis_URF5.py ./URF5.sbox
```

Some nthPrimes have small number of interrupting positions. To utilize it, we have used
```
/benchmark$ python ./synthesis_nthPrime.py ./nthPrime8.sbox
/benchmark$ python ./synthesis_nthPrime.py ./nthPrime9.sbox
/benchmark$ python ./synthesis_nthPrime.py ./nthPrime10.sbox
/benchmark$ python ./synthesis_nthPrime.py ./nthPrime11.sbox
```
