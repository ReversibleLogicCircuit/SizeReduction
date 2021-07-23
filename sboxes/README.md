## Reproducing https://arxiv.org/abs/2107.04298

```
/sboxes$ python ../source/synthesis.py ./AES.sbox 3
/sboxes$ python ../source/synthesis.py ./Skipjack.sbox 2
/sboxes$ python ../source/synthesis.py ./KHAZAD.sbox 2
/sboxes$ python ../source/synthesis.py ./DES1.sbox 2
/sboxes$ python ../source/synthesis.py ./DES2.sbox 2
/sboxes$ python ../source/synthesis.py ./DES3.sbox 2
/sboxes$ python ../source/synthesis.py ./DES4.sbox 2
/sboxes$ python ../source/synthesis.py ./DES5.sbox 2
/sboxes$ python ../source/synthesis.py ./DES6.sbox 2
/sboxes$ python ../source/synthesis.py ./DES7.sbox 2
/sboxes$ python ../source/synthesis.py ./DES8.sbox 2
```

</br>

## Results with various d_j
Each entry reads (QC,#TOF)  

|  functions |      d=0      |      d=1      |      d=2      |      d=3      |      d=4      | d_8=3, d_7=4, d_6=5, ... |
|    ----    |      ----     |     ----      |     ----      |     ----      |     ----      |         ----             |
|    AES     | 5722, 820     | 5649, 800     | 5380, 760     |       -       |       -       |            -             |
|  Skipjack  | 5575, 803     | 5562, 791     | 5440, 771     | 5127, 721     |       -       |            -             |
|   KHAZAD   | 5568, 819     | 5411, 794     | 5126, 742     | 4925, 705     |       -       |            -             |
|   DES-1    | 679, 93       | 714, 97       | 721, 95       | 655, 87       | 755, 105      |            -             |
|   DES-2    | 763, 103      | 760, 101      | 672, 92       | 662, 91       | 698, 98       |            -             |
|   DES-3    | 723, 104      | 723, 104      | 731, 104      | 703, 94       | 707, 94       |            -             |
|   DES-4    | 698, 97       | 684, 94       | 684, 94       | 699, 98       | 684, 90       |            -             |
|   DES-5    | 721, 101      | 756, 102      | 739, 101      | 721, 97       | 665, 87       |            -             |
|   DES-6    | 714, 99       | 718, 102      | 794, 112      | 686, 97       | 702, 94       |            -             |
|   DES-7    | 791, 109      | 791, 109      | 718, 101      | 781, 107      | 673, 92       |            -             |
|   DES-8    | 776, 104      | 805, 112      | 744, 100      | 726, 99       | 737, 100      |            -             |

* Statistically, a large portion of functions benefits from large d_j, but it does not necessarily reduce the cost for a certain function.
