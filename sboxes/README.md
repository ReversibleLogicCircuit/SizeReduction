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
|    AES     | 5722, 820     |       -       |       -       |       -       |       -       |            -             |
|  Skipjack  | 5575, 803     |       -       |       -       |       -       |       -       |            -             |
|   KHAZAD   | 5568, 819     |       -       |       -       |       -       |       -       |            -             |
|   DES-1    | 679, 93       |       -       |       -       |       -       |       -       |            -             |
|   DES-2    | 763, 103      |       -       |       -       |       -       |       -       |            -             |
|   DES-3    | 723, 104      |       -       |       -       |       -       |       -       |            -             |
|   DES-4    | 698, 97       |       -       |       -       |       -       |       -       |            -             |
|   DES-5    | 721, 101      |       -       |       -       |       -       |       -       |            -             |
|   DES-6    | 714, 99       |       -       |       -       |       -       |       -       |            -             |
|   DES-7    | 791, 109      |       -       |       -       |       -       |       -       |            -             |
|   DES-8    | 776, 104      |       -       |       -       |       -       |       -       |            -             |

