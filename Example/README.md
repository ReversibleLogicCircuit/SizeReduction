# Example
## Description

- randomPermutationGenerator.py: generate a random substitution function.
- example.function: 6-bit input example
- exampe_out.real: 6-bit output example (.real format)


## Example commands
For an n-bit input, default command is
```
/Example$ python ../source/synthesis.py ./example.function n
/Example$ python ../source/synthesis.py ./example.function 6
```
To specify d_m for depth-d_m exhaustive search,
```
/Example$ python ../source/synthesis.py ./example.function n d_n d_{n-1} d_{n-2} ...
/Example$ python ../source/synthesis.py ./example.function 6 1 1 1 1
```

## Output
Once the program finishes, {example_out.real} will be generated. REAL format is also supported by RCViewer+ (https://ceit.aut.ac.ir/QDA/RCV.htm), which can visualize the circuit.

## Results on screen
User will see something like below on the screen.
Cm means 
```
Target file	: ./example_in.function
# of bits	: 6
Exha. depths	: [0, 0, 0, 0, 0]
Thu Jul  8 19:14:58 2021
	C0N	C1N	C2N	C3N	C4N	C5N	
C6)	0	20	4	1	0	0	
G6)	0	68	17	8	0	2	
P6)	0	1	0	0	0	0	
C5)	0	6	3	0	0	0	
G5)	0	17	9	3	0	0	
P5)	0	1	0	0	0	0	
C4)	0	6	2	0	0	0	
G4)	0	6	5	1	0	0	
P4)	0	1	0	0	0	0	
C3)	0	0	1	0	0	0	
G3)	0	1	2	0	0	0	
P3)	0	1	0	0	0	0	
E2)	[0]
total Tof cost : 96
Thu Jul  8 19:15:03 2021

6-th decomp	[0, 0, 0, 2, 0, 1, 2, 3, 1, 2, 1, 4, 1, 4, 4, 7, 1, 0, 0, 1, 0, 4, 1, 6, 3, 0, 0, 0, 0, 0, 7, 0]
5-th decomp	[0, 0, 1, 2, 1, 0, 2, 4, 1, 0, 0, 4, 3, 0, 0, 0]
4-th decomp	[0, 1, 1, 2, 1, 0, 3, 0]
3-th decomp	[0, 1, 1, 0]
```
