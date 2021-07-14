# Example
## Description

- example.function: 6-bit input example (one-line notation)
- example.spec: 6-bit input example (.spec format)
- exampe_out.real: 6-bit output example (.real format)


## Example commands
For given input, default command is
```
/example$ python ../source/synthesis.py ./example.function
```
To specify d_j for depth-d_j exhaustive search,
```
/example$ python ../source/synthesis.py ./example.function d_{n-1} d_{n-2} d_{n-3} ...
/example$ python ../source/synthesis.py ./example.function
/example$ python ../source/synthesis.py ./example.function 1
/example$ python ../source/synthesis.py ./example.function 0 2
/example$ python ../source/synthesis.py ./example.function 1 2 2 3
```
The second line applies d_j=0 for all j (default).  
The third line applies d_j=1 for all j.  
The fourth line applies d_5=0, d_4=2, d_3=2, d_2=2, d_1=2 in each step.  
The fifth line applies d_5=1, d_4=2, d_3=2, d_2=3, d_1=3 in each step.  
Search depth larger than the number of remaining row pairs is ignored for excessive amount.  

## Output
Once the program finishes, {example_out.real} will be generated.
RCViewer+ (https://ceit.aut.ac.ir/QDA/RCV.htm) support REAL formats.
The image file {Example_out_circuit.bmp} is obtained by RCViewer+.
![circuit_for_example](./Example_out_circuit.bmp)

## Results on screen
User will see something like below on the screen.
Detailed costs on Mixing and Preprocessing come first, and then the costs on SizeReduction come second in each step. E2 entry is for exhaustive search of last 2-bit permutation.
```
Tue Jul 13 15:33:57 2021
Tue Jul 13 15:33:58 2021
Target file     : .\example\example.function
# of bits       : 6
Exha. depths    : [0, 0, 0, 0, 0]
        C0X     C1X     C2X     C3X     C4X     C5X
P6)     1       20      4       1       0       0
R6)     18      69      17      8       0       2
P5)     1       6       3       0       0       0
R5)     10      18      9       3       0       0
P4)     1       6       2       0       0       0
R4)     6       7       5       1       0       0
P3)     0       0       1       0       0       0
R3)     1       2       2       0       0       0
E2)     2       1       0       0       0       0
Number of Toffoli gate: 96
```
