## Reproducing https://arxiv.org/abs/2107.04298

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
</br>

## Results with various d_n  
Each entry reads (QC,#TOF)  

|  functions |     d_n=0     |     d_n=1     |     d_n=2     |     d_n=3     |     d_n=4     | ..., d_11=0, d_10=1, d_9=2, d_8=3, d_7=3, d_6=4, ... |
|    ----    |      ----     |     ----      |     ----      |     ----      |     ----      |                       ----                           |
|    URF1    | 13318, 2029   |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
|    URF2    | 5510, 803     |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
|    URF3    |       -       | 33541, 4898   |    not yet    |    not yet    |    not yet    |                     not yet                          |
|    URF4    | 81748, 12516  |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
|    URF5    | 11902, 1527   |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
| nthprime7  | 1984, 292     |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
| nthprime8  | 5333, 726     |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
| nthprime9  | 13918, 2073   |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
| nthprime10 | 30421, 4357   |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
| nthprime11 | 69702, 10366  |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
| nthprime12 |    not yet    |    not yet    |    not yet    |    not yet    |    not yet    |                     not yet                          |
