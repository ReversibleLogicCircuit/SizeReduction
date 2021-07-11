# Benchmarks

For URF1, URF2, URF3, URF4, and nthPrime7, following d_n options have been applied.
```
/Benchmark$ python ../source/synthesis.py ./URF1.function 9 2 2 2 2 4 4 4 4
/Benchmark$ python ../source/synthesis.py ./URF2.sbox 8 2 4 4 4 4 4 4
/Benchmark$ python ../source/synthesis.py ./URF3.sbox 10 1 1 1 1 1 1 1 1 1
/Benchmark$ python ../source/synthesis.py ./URF4.sbox 11 0
/Benchmark$ python ../source/synthesis.py ./nthPrime7.sbox 7 4 4 4 4 4 4
```

URF5 is somewhat structured; all row numbers are at normal positions. To utilize it, we have used
```
/Benchmark$ python
```

Some nthPrimes have small number of interrupting positions. To utilize it, we have used
```
/Benchmark$ python ./synthesis_for_exception.py ./nthPrime7.sbox 8 2 2 2 4 4 4 4"
/Benchmark$ python ./synthesis_for_exception.py ./nthPrime9.sbox 9 1 1 1 1 1 1 1 1"
/Benchmark$ python ./synthesis_for_exception.py ./nthPrime10.sbox 10 1 1 1 1 1 1 1 1 1"
/Benchmark$ python ./synthesis_for_exception.py ./nthPrime11.sbox 11 0 0 1 1 1 1 1 1 1 1"
```
