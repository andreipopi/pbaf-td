Documentation: https://www.dbai.tuwien.ac.at/research/report/dbai-tr-2016-96.pdf.
Download source code (https://github.com/mabseher/htd?tab=readme-ov-file).

To be able to compile, I had to remove the "googletests", by actually removing all tests.
In the src\htd_main folder of the source ("htd-master") you'll find the main.cpp file, which configures your htd instance.
The one used in this work is included in this folder.

We also include a version that returns a "path tree decomposition", which includes no join nodes. We note that the path tree decomposition returned may have a leaf node somewhere in the path, that is non empty. One approach to deal with it is to just return the result of its child, and continue the computation. Also, we note that in such "path tree decomposition", htd may not return the incident edges of the bag in the first bag containing both ends of an edge, but may wait until upper in the path.

Create a new folder where you want the compilation, then `cd` into it, and run:

`cmake path/to/htdsource`

then run:

`make`

then `cd` in the bin folder. Now you can call the compiled htd like this:

`./htd_main < /Users/andrei/Documents/GitLab/praaf-tree-decomposition/Instances/graph.gr`



Input in graph.gr:

```
c This file describes a path with five vertices and four edges.
p tw 5 4
1 2
2 3
c we are half-way done with the instance definition.
3 4
4 5
```



Output:

```
Human Tree Decomposition
NODE 12: [ ]
  NODE 1: [ 3, 4 ]
    NODE 5: [ 3, 4 ]
      NODE 8: [ 3 ]
        NODE 2: [ 2, 3 ]
          NODE 7: [ 2 ]
            NODE 4: [ 1, 2 ]
              NODE 14: [ 1 ]
                NODE 11: [ ]
    NODE 6: [ 3, 4 ]
      NODE 9: [ 4 ]
        NODE 3: [ 4, 5 ]
          NODE 13: [ 4 ]
            NODE 10: [ ]
Machine Tree Decomposition
s td 14 2 5
b 1 3 4 
b 2 2 3 
b 3 4 5 
b 4 1 2 
b 5 3 4 
b 6 3 4 
b 7 2 
b 8 3 
b 9 4 
b 10 
b 11 
b 12 
b 13 4 
b 14 1 
1 5
1 6
2 7
4 7
5 8
2 8
6 9
3 9
1 12
3 13
10 13
4 14
11 14
Traversal
leaf/root N10:<EMPTY> edges
intro N13:[ 4 ] introduced [ 4 ] edges
intro N3:[ 4, 5 ] introduced [ 5 ] edges [ 4, 5 ] [ 5, 4 ]
rem N9:[ 4 ] removed [ 5 ] edges
intro N6:[ 3, 4 ] introduced [ 3 ] edges [ 3, 4 ]
leaf/root N11:<EMPTY> edges
intro N14:[ 1 ] introduced [ 1 ] edges
intro N4:[ 1, 2 ] introduced [ 2 ] edges [ 1, 2 ]
rem N7:[ 2 ] removed [ 1 ] edges
intro N2:[ 2, 3 ] introduced [ 3 ] edges [ 2, 3 ]
rem N8:[ 3 ] removed [ 2 ] edges
intro N5:[ 3, 4 ] introduced [ 4 ] edges [ 3, 4 ]
join N1:[ 3, 4 ] edges [ 3, 4 ]
rem N12:<EMPTY> removed [ 3, 4 ] edges
```




How to get some order and labels intro/rem/join for python traversal?

We can now get most info, but has to be polished.

leaf/rootNODE10:<EMPTY> edges 
intro NODE3:[ 4, 5 ] edges  [ 4, 5 ] [ 5, 4 ] introvertices [ 4, 5 ]
rem NODE9:[ 4 ] edges  removed [ 5 ]
intro NODE6:[ 3, 4 ] edges  [ 3, 4 ] introvertices [ 3 ]
leaf/rootNODE11:<EMPTY> edges 
intro NODE4:[ 1, 2 ] edges  [ 1, 2 ] introvertices [ 1, 2 ]
rem NODE7:[ 2 ] edges  removed [ 1 ]
intro NODE2:[ 2, 3 ] edges  [ 2, 3 ] introvertices [ 3 ]
rem NODE8:[ 3 ] edges  removed [ 2 ]
intro NODE5:[ 3, 4 ] edges  [ 3, 4 ] introvertices [ 4 ]
join NODE1:[ 3, 4 ] edges  [ 3, 4 ]
rem NODE12:<EMPTY> edges  removed [ 3, 4 ]