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

|  Functions |      d=0      |      d=1      |      d=2      |      d=3      |      d=4      |      d=5      |..., d_i = ,... |
|    ----    |      ----     |     ----      |     ----      |     ----      |     ----      |     ----      |      ----                    |
|    URF1    | 18223, 2805   | 13589, 2066   | 13318, 2029   | 12333, 1869   |       -       |       -       |        -                     |
|    URF2    | 7305, 1085    | 5740, 845     | 5510, 803     | 5105, 738     | 4986, 720     |       -       |        -                     |
|    URF3    | 47161, 6945   | 34845, 5145   | 33541, 4898   |       -       |       -       |       -       |        -                     |
|    URF4    | 108493, 16435 | 81748, 12516  | 77616, 11706  |       -       |       -       |       -       |        -                     |
|    URF5    | 17787, 2555   | 11968, 1527   | 9863, 1366    | 8735, 1309    |       -       |       -       |        -                     |
| nthprime7  | 2461, 382     | 1984, 292     | 1887, 281     | 1772, 258     | 1827, 259     | 1759, 252     |        -                     |
| nthprime8  | 6793, 970     | 5333, 726     | 5165, 691     | 5017, 668     | 4751, 627     |       -       |        -                     |
| nthprime9  | 18043, 2673   | 13203, 1935   | 12189, 1762   | 11512, 1653   |       -       |       -       |        -                     |
| nthprime10 | 40860, 5900   | 30421, 4357   | 28630, 4003   |       -       |       -       |       -       |        -                     |
| nthprime11 | 101840, 15186 | 69702, 10366  | 63314, 9269   |       -       |       -       |       -       |        -                     |
| nthprime12 | 231897, 32369 | 165945, 23992 |       -       |       -       |       -       |       -       |        -                     |
| nthprime13 | 492215, 72941 |       -       |       -       |       -       |       -       |       -       |        -                     |
| nthprime14 |1159561, 162187|       -       |       -       |       -       |       -       |       -       |        -                     |
| nthprime15 |2483879, 355570|       -       |       -       |       -       |       -       |       -       |        -                     |
| nthprime16 |5408140, 770822|       -       |       -       |       -       |       -       |       -       |        -                     |

* Statistically, a large portion of functions benefits from large d_j, but it does not necessarily reduce the cost for a certain function.
