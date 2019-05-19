"""
glee.py
-------

Geometric Laplacian Eigenmap Embedding.

"""

import argparse
import numpy as np
from scipy import sparse
import networkx as nx


def laplacian_degrees(graph):
    """Return the Laplacian matrix and the diagonal degree matrix."""
    adj = nx.to_scipy_sparse_matrix(graph, format='csr')
    degs = sparse.diags(adj.sum(axis=1).flatten(), [0], adj.shape, format='csr')
    return degs - adj, degs


def eigenmaps(graph, dim, method='glee', return_vals=False):
    """Return the Eigenmap embedding of the graph.

    Params
    ------

    graph (nx.Graph): the graph to embed.

    method (str): 'glee' for GLEE (default), or 'eigen' for original
    Laplacian Eigenmaps.

    dim (int): number of embedding dimensions.

    return_vals (bool): whether to return the eigenvalues. Default False.

    """
    if dim > graph.order() - 1 or dim < 2:
        raise ValueError('dim must be grater than 0 and less than graph.order()')

    lapl, degs = laplacian_degrees(graph)
    shape = (graph.order(), graph.order())
    invdegs = sparse.diags(1 / degs.diagonal(), 0, shape, format='csr')

    eig_fun = {
        'glee': {
            True: np.linalg.eigh,
            False: lambda m: sparse.linalg.eigsh(
                m, k=dim, which='LM', return_eigenvectors=True)},
        'eigen': {
            True: np.linalg.eig,
            # In the following we need to compute dim+1 eigenvectors so
            # that after deleting the zero eigenvalue we get exactly dim.
            False: lambda m: sparse.linalg.eigs(
                m, k=dim+1, which='SM', return_eigenvectors=True)}
    }
    matrix_fun = {
        'glee': {True: lambda: lapl.A, False: lambda: lapl},
        'eigen': {True: lambda: invdegs.A.dot(lapl.A),
                  False: lambda: invdegs.dot(lapl)}
    }
    post_process = {
        'glee': lambda vals, vecs: \
        (vals, vecs.dot(np.diag(np.sqrt(vals)))),
        'eigen': lambda vals, vecs: \
        (vals[1:], vecs[:, 1:].dot(
            np.diag([1/np.sqrt(v.dot(degs.A).dot(v))
                     for v in vecs[:, 1:].T])))
    }

    is_full = dim is None or dim > graph.order() - 3
    eig = eig_fun[method][is_full]
    matrix = matrix_fun[method][is_full]()
    vals, vecs = eig(matrix)
    # All eigenvalues are guaranteed to be non-negative, but sometimes the
    # zero eigenvalues can come very close to zero but negative, so we take
    # the absolute value as we need to take sqrt.
    vals, vecs = np.abs(vals.real), vecs.real
    vals, vecs = post_process[method](vals, vecs)

    indices = np.argsort(vals)
    indices = indices[::-1] if method == 'glee' else indices
    vals = vals[indices][:dim]
    vecs = (vecs.T[indices].T)[:, :dim]
    return (vecs, vals) if return_vals else vecs


def main(infile, outfile, dim, method):
    """Load an edge list and compute its GLEE to disk."""
    graph = nx.read_edgelist(infile)
    emb = eigenmaps(graph, method, dim)
    np.save(outfile, emb)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,
                        help='edge list file path')
    parser.add_argument('--output', type=str, required=True,
                        help='embedding output file path')
    parser.add_argument('--dim', default=128, type=int,
                        help='dimension of embedding (default 128)')
    parser.add_argument('--method', default='glee', type=str,
                        help='"glee" or "eigen"')
    args = parser.parse_args()
    main(args.input, args.output, args.dim, args.method)
