### Python implementation of reversible logic circuit synthesis algorithm given by https://arxiv...


## --- About {source} folder ---
1. {core.py}: all the functions introduced in https://arxiv..., plus some miscellaneous functions are implemented.
2. {synthesis.py}: It takes as input a file {name.function} and outputs a file {name_out.real}.
3. Input format: two formats are acceptable by {synthesis.py}
  a) SPEC format: truth table (see, http://revlib.org)
  b) one-line notation: (see, https://en.wikipedia.org/wiki/Permutation#One-line_notation). For example, [7,2,0,1,5,3,6,4].
4. Output format: REAL format (see, http://revlib.org). This format is also supported by REViewer+ (https://ceit.aut.ac.ir/QDA/RCV.htm) for visualizing circuits.


## --- About {Example} folder ---
1. {randomPermutationGenerator.py}: generates a permutation.
2. {example.function}: 6-bit input
3. {example_out.real}: 6-bit output
4. Command: SizeReduction-main/Example$ python ../source/synthesis.py ./example.function
5. See README.md in the folder for details.


## --- About {Benchmark} folder ---
1. To reproduce the benchmark results in https://arxiv...: run the code with specified options given in README.md in the folder.


## --- About {S-boxes} folder ---
1. To reproduce the S-box circuits found by https://arxiv...: run the code with specified options given in README.md in the folder.
