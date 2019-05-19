# GLEE: Geometric Laplacian Eigenmap Embedding

GLEE is a graph embedding technique based on the spectral and geometric
properties of the Laplacian matrix of an undirected graph.


## Installation

Clone this repo to access the GLEE functionality. Requirements are numpy,
scipy and networkX.


## Usage

This library can be used in two different ways. It can be directly imported
for use within your Python application using `import glee`. For an example
of this kind of usage see `GLEE example usage.ipynb`.

It can also be used from the command line by executing `python glee.py
<args>`. Running `python glee.py -h` will show an explanation of the
available arguments.

```
usage: glee.py [-h] --input INPUT --output OUTPUT [--dim DIM]
               [--method METHOD]

optional arguments:
  -h, --help       show this help message and exit
  --input INPUT    edge list file path
  --output OUTPUT  embedding output file path
  --dim DIM        dimension of embedding (default 128)
  --method METHOD  "glee" or "eigen"
```

A usual way to use GLEE in this way is, for example,

```
python glee.py --input karate.txt --output karate.out --dim 8
```

One can also compute the original version of Laplacian Eigenmaps by doing

```
python glee.py --input karate.txt --output karate.out --dim 8 --method eigen
```
