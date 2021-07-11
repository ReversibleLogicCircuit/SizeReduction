# Benchmarks

For URF1, URF2, URF3, URF4, and nthPrime7, following d_n options have been applied.

```
/benchmark$ python ../source/synthesis.py ./URF1.function 2 2 2 2 4 4 4
/benchmark$ python ../source/synthesis.py ./URF2.sbox 2 4 4 4 4 4
/benchmark$ python ../source/synthesis.py ./URF3.sbox 1
/benchmark$ python ../source/synthesis.py ./URF4.sbox 0
/benchmark$ python ../source/synthesis.py ./nthPrime7.sbox 4 4 4 4 4
```

URF5 is somewhat structured; all row numbers are at normal positions. To utilize it, we have used
```
/benchmark$ python ./synthesis_exception.py ./URF5.sbox 2 2 2 2 4 4 4
```

Some nthPrimes have small number of interrupting positions. To utilize it, we have used
```
/benchmark$ python ./synthesis_exception.py ./nthPrime7.sbox 2 2 2 4 4 4
/benchmark$ python ./synthesis_exception.py ./nthPrime9.sbox 1 1 1 1 1 1 1
/benchmark$ python ./synthesis_exception.py ./nthPrime10.sbox 1 1 1 1 1 1 1 1
/benchmark$ python ./synthesis_exception.py ./nthPrime11.sbox 0 0 1 1 1 1 1 1 1
```
