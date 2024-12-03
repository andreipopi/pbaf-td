## pbaf-td

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Link to paper]()

# Citation


## Problem

PBAF-TD computes the probability of a set of arguments being an extension under some semantics in an abstract(a) or deductive (d) Probabilistic Bipolar Argumentation Framework (PBAF).


## Usage

To run the system for some semantics, you need:

- compiled htd library (see CompilationHTD)
- post_order_sem.py
- sem.py 
- input_output.py (uses htd)
- instance.lp

1) Compile htd for your system.
2) Set the correct path to htd in input_output.py.
3) Call the system: python post_order_sem.py instance.lp

## Example Call

For a d-PBAF for the d-admissible semantics you would issue the following call:

python post_order_dpbaf_dadm.py instance.lp


## Contents

- systems set up for the the semantics described in the paper.
- instances used for the evaluation in the paper ("instance_set"), and other "known" instances.
- instance generator.
- preprocessing encodings.
- htd binaries used on our machines (might not work on yours).
- raw results, automated results processing scripts, etc...
- shell scripts to automatically run all systems for evaluation.

## HTD Compilation

See dedicated folder.

## Instance Format

[RunningExample]
    
    arg(a). arg(b). arg(c). arg(d). arg(e).

    p(a,8). p(b,10). p(c,9). p(d,10). p(e,10).
    
    att(a,d). att(b,a). att(b,c). att(d,c). att(c,d). att(d,e). att(e,d).

    support(d,a). support(a,b). support(c,b).

    p(1,a,d,10). p(9,a,b,7). p(2,e,d,10). p(4,b,c,10). p(5,b,a,10). p(6,d,c,10). p(8,d,a,10). p(3,d,e,5). p(7,c,d,10). p(10,c,b,10).

    in(e).

## Authors

Andrei Popescu (TU Graz) and Johannes Wallner (TU Graz). For questions or comments contact andrei.popescu@ist.tugraz.at.

## License

This software is released under the MIT License and copyrighted by the authors.