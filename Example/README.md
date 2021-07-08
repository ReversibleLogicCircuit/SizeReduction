# Example

In this page, it is explained how to synthesis with proposed algorithm.

A target function is randomly generated with "randomPermutationGenerator.py" and is 6-bit function.

## Description

- randomPermutationGenerator.py: source for making a random function.
- example.function: random 6-bit fucntion
- exampe_out.real: output of synthesis (.real format)

## How to synthesis with example function

**We recommand to type "Python ./syntehsis.py -h" first.**

"python ./syntehsis.py ./example.function 6 0" or "python ./syntehsis.py ./example.function 6 1 1 1 1 1"

## Results

After typing above command, "example_out.real" file is generated in your directory.

Furthermore, you can read the below result too (total number of Toffoli gate is 96).

```
Target file	: ./example_in.function
\# of bits	: 6
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
