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

## Results with various d_j  
Each entry reads (QC,#TOF)  

|  Functions |      d=0      |      d=1      |      d=2      |      d=3      |      d=4      |      d=5      |..., d_9=2, d_8=3, d_7=4, ... |
|    ----    |      ----     |     ----      |     ----      |     ----      |     ----      |     ----      |      ----                    |
|    URF1    |       -       | 13589, 2066   | 13318, 2029   | 12333, 1869   |       -       |       -       |        -                     |
|    URF2    |       -       | 5740, 845     | 5510, 803     | 5105, 738     | 4986, 720     |       -       |        -                     |
|    URF3    |       -       | 34845, 5145   | 33541, 4898   |       -       |       -       |       -       |        -                     |
|    URF4    |       -       | 81748, 12516  | 77616, 11706  |       -       |       -       |       -       |        -                     |
|    URF5    |       -       | 11968, 1527   | 9863, 1366    | 8735, 1309    |       -       |       -       |        -                     |
| nthprime7  |       -       | 1984, 292     | 1887, 281     | 1772, 258     | 1827, 259     | 1759, 252     |        -                     |
| nthprime8  |       -       | 5333, 726     | 5165, 691     | 5017, 668     | 4751, 627     |       -       |        -                     |
| nthprime9  |       -       | 13203, 1935   | 12189, 1762   | 11512, 1653   |       -       |       -       |        -                     |
| nthprime10 |       -       | 30421, 4357   | 28630, 4003   |       -       |       -       |       -       |        -                     |
| nthprime11 |       -       | 69702, 10366  | 63314, 9269   |       -       |       -       |       -       |        -                     |
| nthprime12 |       -       | 165945, 23992 |       -       |       -       |       -       |       -       |        -                     |

* Statistically, a large portion of functions benefits from large d_j, but it does not necessarily reduce the cost for a certain function.
