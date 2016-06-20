# -*- coding: utf-8 -*-
#
# This file is part of Inspire.
# Copyright (C) 2016 CERN.
#
# Inspire is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Inspire is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inspire; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Methods to solve matching problem."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import numpy as np
from scipy.optimize import linprog


def _cost_matrix(clusters_before, clusters_after):
    """Compute costs for the matching solver.

    Receives two partitions representing clusters in the state before
    and after. Each the-state-before cluster is being used to calculate
    the cost function against each of cluster from the the-state-after.
    The cost function is calculating the overlap between members of the
    two given sets.

    :param clusters_before:
        A dictionary of sets representing clusters from the-state-before,
        with enumerated keys.

        Example:
            clusters_before = {1: set(['A', 'B']), 2: set(['C'])}

    :param clusters_after:
        A dictionary of sets representing clusters from the-state-after,
        with enumerated keys.

        Example:
            clusters_after = {1: set(['B']), 2: set(['A', 'C'])}

    :return:
        A matrix of (clusters_before + clusters_after) x (clusters_after)
        size containing all costs values for each pair of clusters.

        Example:
            [[-1.25       -1.16666667]
             [-0.16666667 -1.25      ]
             [-0.25       -0.16666667]
             [-0.25       -0.16666667]]
    """
    cost = np.zeros((len(clusters_before), len(clusters_after)))

    for index_before, cluster_before in clusters_before.items():
        for index_after, cluster_after in clusters_after.items():
            cost[index_before, index_after] = -len(
                set.intersection(
                    set(cluster_before), set(cluster_after))) - 1. / \
                (len(clusters_after) * (1 + len(
                    set.symmetric_difference(set(cluster_before),
                                             set(cluster_after)))))

    return cost


def _solve_clusters(clusters_before, clusters_after, maxiter=5000):
    """Solve the matching problem using simplex method.

    Receives a cost matrix produced by compute_cost_function_matrix.
    Using linprog method from scipy.optimize package, calculates
    the best match for each cluster from the-state-before with a
    cluster from the-state-after.

    :param clusters_before:
        A dictionary of sets representing clusters from the-state-before.

        Example:
            clusters_before = {1: set(['A', 'B']), 2: set(['C'])}

    :param clusters_after:
        A dictionary of sets representing clusters from the-state-after.

        Example:
            clusters_after = {3: set(['B']), 4: set(['A', 'C'])}

    :param maxiter:
        An optional parameter to define the maximum number of
        iterations to perform during linprog execution.

    :return:
        A tuple containing three buckets, representing **keys** of matched
        clusters (as pairs), new ones and removed.

        Example:
            ([(1, 2)], [3], [])
    """
    len_before = len(clusters_before)
    len_after = len(clusters_after)

    # Copies of the given dictionaries, as dictionaries with enumerated keys.
    clusters_before_copy = {}
    cluster_after_copy = {}
    key_map = []

    for index, key in enumerate(clusters_before):
        clusters_before_copy[index] = clusters_before[key]
        key_map.append(key)

    for index, key in enumerate(clusters_after):
        cluster_after_copy[index] = clusters_after[key]
        clusters_before_copy[len_before + index] = set()
        key_map.append(key)

    # Compute the cost matrix.
    cost = _cost_matrix(clusters_before_copy,
                        cluster_after_copy)

    n_cluster_before, n_cluster_after = cost.shape
    n_edges = n_cluster_before * n_cluster_after

    # Each agent may be assigned to at most one task.
    A_ub = np.zeros((n_cluster_before, n_edges))

    for index in range(n_cluster_before):
        A_ub[index, index * n_cluster_after:(
            index + 1) * n_cluster_after] = 1.0

    b_ub = np.ones(n_cluster_before)

    # Each task has to be assignees to exactly one agent.
    A_eq = np.zeros((n_cluster_after, n_edges))

    for index in range(n_cluster_after):
        A_eq[index, index::n_cluster_after] = 1.0

    b_eq = np.ones(n_cluster_after)

    coefficients = cost.ravel()
    solution = linprog(coefficients,
                       A_ub=A_ub,
                       b_ub=b_ub,
                       A_eq=A_eq,
                       b_eq=b_eq,
                       options={'maxiter': maxiter})

    bucket_pairs = []
    bucket_new = []
    bucket_remove = []

    for index_first in range(len_before + len_after):
        for index_second in range(len_after):
            if solution.x[index_first * len_after + index_second] == 1:
                if index_first < len_before:
                    bucket_pairs.append((
                        key_map[index_first],
                        key_map[len_before + index_second]))
                else:
                    bucket_new.append(
                        key_map[len_before + index_second])
                break
        else:
            if index_first < len_before:
                bucket_remove.append(
                    key_map[index_first])

    return bucket_pairs, bucket_new, bucket_remove
