# Example
## Description

- example.function: 6-bit input example
- exampe_out.real: 6-bit output example (.real format)


## Example commands
For given input, default command is
```
/Example$ python ../source/synthesis.py ./example.function
```
To specify d_m for depth-d_m exhaustive search,
```
/Example$ python ../source/synthesis.py ./example.function d_n d_{n-1} d_{n-2} ...
/Example$ python ../source/synthesis.py ./example.function 1
/Example$ python ../source/synthesis.py ./example.function 0 2
/Example$ python ../source/synthesis.py ./example.function 1 2 2 3
```
The second line applies d_m=1 for all steps.
The third line applies d_6=0, d_5=2, d_4=2, d_3=2 in each step.
The fourth line applies d_6=1, d_5=2, d_4=2, d_3=3 in each step.


## Output
Once the program finishes, {example_out.real} will be generated.
RCViewer+ (https://ceit.aut.ac.ir/QDA/RCV.htm) support REAL formats.
The image file {Example_out_circuit.png} is obtained by RCViewer+.

## Results on screen
User will see something like below on the screen.
Detailed cost on Mixing and preprocessing comes first, and then the cost on SizeReduction comes second in each step. 
```
        C0X     C1X     C2X     C3X     C4X     C5X
P6)     0       20      4       1       0       0
R6)     0       68      17      8       0       2
P5)     0       6       3       0       0       0
R5)     0       17      9       3       0       0
P4)     0       6       2       0       0       0
R4)     0       6       5       1       0       0
P3)     0       0       1       0       0       0
R3)     0       1       2       0       0       0
E2)     [0]
total Tof cost : 96
Target file     : ./example.function
# of bits       : 6
Exha. depths    : [0, 0, 0, 0, 0]
Number of Toffoli gate: 96
```
