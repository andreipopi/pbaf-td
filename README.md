# PBAF-TD

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> [!NOTE]
> This is the maintained GitHub repository for PBAF-TD. The project was originally hosted in the [TU Graz Knowledge Representation and Reasoning (KRR) GitLab repository](https://gitlab.tugraz.at/krr/pbaf-td).

PBAF-TD provides exact dynamic-programming algorithms for computing the probability that a given set of arguments is an extension of a Probabilistic Bipolar Argumentation Framework (PBAF). The algorithms operate on tree decompositions, are designed to exploit low treewidth, and support both abstract and deductive PBAFs.

## Publication

Andrei Popescu and Johannes P. Wallner. **Dynamic Programming Algorithms for Probabilistic Bipolar Argumentation Frameworks.** In *Proceedings of the 40th ACM/SIGAPP Symposium on Applied Computing (SAC 2025)*, pages 1051-1052. ACM, 2025.

- [Published paper](https://doi.org/10.1145/3672608.3707819)

## Supported Variants

Solver entry points are located in [`Pext/verification/`](Pext/verification/):

- `post_order_spbaf_*.py`: abstract PBAFs using supported attacks
- `post_order_dpbaf_*.py`: deductive PBAFs
- `sadm`, `dadm`, and `cadm`: s-, d-, and c-admissible semantics
- `scom`, `dcom`, and `ccom`: s-, d-, and c-complete semantics
- `st`: stable semantics

## Contents

- [`Pext/verification/`](Pext/verification/): dynamic-programming solvers and HTD interface
- [`Pext/verification/preprocessing/`](Pext/verification/preprocessing/): ASP preprocessing for supported and deductive attacks
- [`InstanceGenerator/`](InstanceGenerator/): benchmark instance generator
- [`InstanceGenerator/Instances/`](InstanceGenerator/Instances/): examples and known instances
- [`InstanceGenerator/instance_set/`](InstanceGenerator/instance_set/): instances used in the experimental evaluation
- [`Run/`](Run/): benchmark scripts, raw logs, and result-processing scripts
- [`CompilationHTD/`](CompilationHTD/): the modified HTD entry point and compilation notes

## Requirements

- Python 3
- [pandas](https://pandas.pydata.org/)
- [Clingo](https://potassco.org/clingo/) for preprocessing
- [HTD](https://github.com/mabseher/htd) for computing tree decompositions

## HTD Setup

Compile HTD using the modified [`main.cpp`](CompilationHTD/main.cpp) and the instructions in [`CompilationHTD/compileHTD.md`](CompilationHTD/compileHTD.md). Prebuilt binaries are included under [`Pext/verification/htd-binary/`](Pext/verification/htd-binary/), but they are tied to their original build environments and may need to be rebuilt.

Set the `command` variable in [`Pext/verification/input_output.py`](Pext/verification/input_output.py) to the path of a working HTD binary before running a solver. The file currently contains an absolute path from the original development machine.

## Running a Solver

The current scripts expect to be run from the `Pext` directory, and the instance should be passed with an absolute path. For example, to compute d-admissibility under the deductive interpretation:

```bash
cd Pext
python3 verification/post_order_dpbaf_dadm.py \
  /absolute/path/to/pbaf-td/InstanceGenerator/Instances/running_example.lp d
```

For an abstract PBAF, use a `post_order_spbaf_*.py` entry point and pass `s` as the final argument. For a deductive PBAF, use a `post_order_dpbaf_*.py` entry point and pass `d`.

The scripts in [`Run/`](Run/) reproduce the original experiments but contain absolute paths from the original machines. Update those paths before running the benchmark scripts.

## Instance Format

See [`InstanceGenerator/Instances/running_example.lp`](InstanceGenerator/Instances/running_example.lp) for a complete example. The main predicates are:

- `arg(a).`: argument `a`
- `att(a,b).`: attack from `a` to `b`
- `support(a,b).`: support from `a` to `b`
- `p(a,8).`: probability 0.8 for argument `a`
- `p(i,a,b,7).`: probability 0.7 for attack or support `i` from `a` to `b`
- `in(a).`: argument `a` belongs to the set being verified

Probabilities are represented by integers from `1` to `10`, corresponding to `0.1` through `1.0`.

## Citation

```bibtex
@inproceedings{PopescuWallner2025,
  author    = {Andrei Popescu and Johannes P. Wallner},
  title     = {Dynamic Programming Algorithms for Probabilistic Bipolar Argumentation Frameworks},
  booktitle = {Proceedings of the 40th ACM/SIGAPP Symposium on Applied Computing},
  pages     = {1051--1052},
  publisher = {ACM},
  year      = {2025},
  doi       = {10.1145/3672608.3707819}
}
```

## Authors

- Andrei Popescu
- Johannes P. Wallner

For questions or comments, contact [Andrei Popescu](mailto:andrei.popescu@tugraz.at).

## License

The project code is available under the [MIT License](LICENSE). Included third-party tools retain their own licenses.
