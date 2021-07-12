### Python3 implementation of reversible logic circuit synthesis algorithm given by https://arxiv...
</br>
 
### --- ./source folder ---
1. core.py: all the functions introduced in https://arxiv.org/abs/2107.04298, plus some miscellaneous functions have been implemented.
2. synthesis.py: It takes as input a file {name.function} and outputs a file {name_out.real}.
3. Input formats (either is acceptable): \
	a) SPEC format; truth table (see, http://revlib.org) \
	b) one-line notation (see, https://en.wikipedia.org/wiki/Permutation#One-line_notation)  
4. Output format: REAL format (see, http://revlib.org). This format is also supported by RCViewer+ (https://ceit.aut.ac.ir/QDA/RCV.htm) for circuit visualization.
</br>

### --- ./example folder ---
1. Example command: 
```
/example$ python ../source/synthesis.py ./example.function
```
2. See README.md in the folder for details.
</br>

## --- ./benchmark folder ---
1. To reproduce the benchmark results in https://arxiv.org/abs/2107.04298: run the code with specified options given in README.md in the folder.
</br>

## --- ./sboxes folder ---
1. To reproduce the S-box circuits found by https://arxiv.org/abs/2107.04298: run the code with specified options given in README.md in the folder.
