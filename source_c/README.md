# C Implementation

The reversible logic circuit synthesis algorithm originally implemented in Python (`core.py` and `synthesis.py`) has been ported to C.

In addition, the construction of the candidate list used for depth-limited exhaustive search has been parallelized using OpenMP, thereby improving the overall execution speed.

## Usage

Compile the source files using the following command:

```bash
gcc -fopenmp -O3 -std=c11 -o qube unit_opers.c leaf_utils.c block_ops.c exhaustive.c mixing.c reduction.c synthesis.c qube_main.c
```

Then, run the executable with an input file as follows:

```bash
OMP_NUM_THREADS=8 ./qube ../SizeReduction-main/example/example.function
```

Here, `OMP_NUM_THREADS` specifies the number of OpenMP threads to be used during execution.

## Example Commands

For a given input file, the default command is:

```bash
OMP_NUM_THREADS=8 ./qube ../SizeReduction-main/example/example.function
```

To specify the search depth `d_j` for the depth-`d_j` exhaustive search at each reduction step, additional arguments may be provided:

```bash
OMP_NUM_THREADS=8 ./qube ../SizeReduction-main/example/example.function d_{n-1} d_{n-2} d_{n-3} ...
OMP_NUM_THREADS=8 ./qube ../SizeReduction-main/example/example.function
OMP_NUM_THREADS=8 ./qube ../SizeReduction-main/example/example.function 1
OMP_NUM_THREADS=8 ./qube ../SizeReduction-main/example/example.function 0 2
OMP_NUM_THREADS=8 ./qube ../SizeReduction-main/example/example.function 1 2 2 3
```

The second command uses the default setting, namely `d_j = 0` for all `j`.

The third command sets `d_j = 1` for all `j`.

The fourth command sets `d_5 = 0` and `d_4 = d_3 = d_2 = d_1 = 2` at the corresponding reduction steps.

The fifth command sets `d_5 = 1`, `d_4 = 2`, `d_3 = 2`, `d_2 = 3`, and `d_1 = 3` at the corresponding reduction steps.

If the specified search depth exceeds the number of remaining row pairs, the excessive search depth is ignored to avoid unnecessary computation.

## Output

After the program terminates, an output file named `example_out.real` is generated.

## Screen Output

During execution, the program displays information similar to the following:
```text
Target file     : ../SizeReduction-main/example/example.function
# of bits       : 6
# of gates      : 264
# of Toffoli    : 123
output          : ../SizeReduction-main/example/example_out.real
verified        : identity OK
```