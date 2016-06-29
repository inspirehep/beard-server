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

"""Methods to build a tree of clusters."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from six import iteritems, viewkeys


def _append_children(node, clusters_before, clusters_after, clusters_reversed,
                     solution_before, solution_after):
    """Append children for the given node.

    Receives a key (representing a node) of one of the dictionaries.
    In order to proceed with building a tree, containing the list of
    nodes required to create a subproblem, the method append the children
    (subnodes) of the given parent. If the node is the key of
    clusters_before or clusters_after dictionary, then the cluster of
    signatures is a part of the currently generating subproblem.

    :param node:
        A key of one of the given dictionaries.

        Example (for example clusters_reversed's key):
            node = A

    :param clusters_before:
        A dictionary containing unique keys and signatures clustered into
        lists (representing the same author), as values.

        Example:
            clusters_before = {1: ['A', 'B'], 2: ['C']}

    :param clusters_after:
        A dictionary containing unique keys and signatures clustered into
        lists (representing the same author), as values.

        Example:
            clusters_after = {3: ['A', 'B'], 4: ['C', D']}

    :param clusters_reversed:
        A dictionary containing values from clusters_before and
        clusters_after dictionaries as the keys and the keys of
        these dictionaries as the values. This dictionary points,
        where the given signatures are stored.

        Example:
            clusters_reversed = {'A': [1, 3], 'B': [1, 3],
                                 'C': [2, 4], 'D': [4]}

    :param solution_before:
        A dictionary of sets containing signatures being selected as the
        part of the currently generating subproblem in the-state-before.

        Example:
            solution_before = {1: set(['A, B'])}

    :param solution_after:
        A dictionary of sets containing signatures being selected as the
        part of the currently generating subproblem in the-state-after.

        Example:
            solution_after = {3: set(['A, B'])}

    :return:
        A list of children of the given node.

        Example:
            [1, 3]
    """
    if node in clusters_before.keys():
        solution_before[node] = clusters_before[node]

        return clusters_before[node]

    if node in clusters_after.keys():
        solution_after[node] = clusters_after[node]

        return clusters_after[node]

    if node in clusters_reversed.keys():
        return clusters_reversed[node]


def _convert_clusters_to_sets(subproblems):
    """Convert a cluster of signatures represented by list into a set.

    Simplex algorithm requires clusters of signatures to be in the format
    of sets, however the subproblem methods work within the lists.
    The converter converters each cluster into a set.

    :param subproblems:
        A dictionary of clusters, where values are in the format of lists.

        Example:
            [({1: ['A', 'B']}, {3: ['A', 'B']}),
             ({2: ['C']}, {4: ['C', 'D']})]

    :return:
        A dictionary of clusters, where values are converted into sets.

        Example:
            [({1: set(['A', 'B')]}, {3: set(['A', 'B'])}),
             ({2: set(['C'])}, {4: set(['C', 'D'])})]
    """
    try:
        for subproblem in subproblems:
            for partition in subproblem:
                for (index, cluster) in iteritems(partition):
                    partition[index] = set(cluster)
    except TypeError:
        raise TypeError("Dictionary of subproblems expected.")

    return subproblems


def _check_node(node, clusters_before, clusters_after,
                clusters_reversed, keys_queue, node_checked,
                solution_before, solution_after):
    """For the given node, create a tree.

    Receives a key (representing a node). If the node was
    already checked in the previous execution, then the method
    terminates. If not, the node is marked as being checked
    and removed from the queue. Using recursion, the method is
    checking the node's children.

    :param node:
        A key of one of the given dictionaries.

        Example (clusters_reversed's key):
            node = A

    :param clusters_before:
        A dictionary containing unique keys and signatures clustered into
        lists (representing the same author), as values.

        Example:
            clusters_before = {1: ['A', 'B'], 2: ['C']}

    :param clusters_after:
        A dictionary containing unique keys and signatures clustered into
        lists (representing the same author), as values.

        Example:
            clusters_after = {3: ['A', 'B'], 4: ['C', D']}

    :param clusters_reversed:
        A dictionary containing values from clusters_before and
        clusters_after dictionaries as the keys and the keys of
        these dictionaries as the values. This dictionary points,
        where the given signatures are stored.

        Example:
            clusters_reversed = {'A': [1, 3], 'B': [1, 3],
                                 'C': [2, 4], 'D': [4]}

    :param keys_queue:
        A list of keys (nodes) of clusters_before and clusters_after
        dictionaries, which will be checked during the run of the
        check_node method. If the key was checked during the
        recursion, then it is removed from the queue.

        Example:
            keys_queue = [3, 4, 1, 2]

    :param node_checked:
        A list of nodes that were checked during the one run of the
        check_node method.

        Example:
            node_checked = [3, 'A', 1, 'B']

    :param solution_before:
        A dictionary of sets containing signatures being selected as the
        part of the currently generating subproblem in the-state-before.

        Example:
            solution_before = {1: set(['A, B'])}

    :param solution_after:
        A dictionary of sets containing signatures being selected as the
        part of the currently generating subproblem in the-state-after.

        Example:
            solution_after = {3: set(['A, B'])}

    :return:
        If the given node was checked, terminate the recursion.

    """
    if node in node_checked:
        return

    if node in keys_queue:
        keys_queue.remove(node)

    node_checked.add(node)
    children = _append_children(node, clusters_before, clusters_after,
                                clusters_reversed, solution_before,
                                solution_after)

    try:
        for child in children:
            _check_node(child, clusters_before, clusters_after,
                        clusters_reversed, keys_queue, node_checked,
                        solution_before, solution_after)
    except TypeError:
        pass


def _divide_into_subproblems(clusters_before, clusters_after):
    """Divide the clusters into subproblems.

    Receives two dictionaries representing clustered data in the-state-before
    and in the-state-after. In order not to check every possible case during
    matching the clusters, the method splits clusters into lists, which are not
    dependent to each other and thus can be treated subproblems for the
    matching algorithm.

    :param clusters_before:
        A dictionary containing unique keys and signatures clustered into
        lists (representing the same author), as values.

        Example:
            clusters_before = {1: ['A', 'B'], 2: ['C']}

    :param clusters_after:
        A dictionary containing unique keys and signatures clustered into
        lists (representing the same author), as values.

        Example:
            clusters_after = {3: ['A', 'B'], 4: ['C', 'D']}

    :return:
        A list of tuples containing matched dictionaries, which shares exactly
        the same elements, thus are are not dependent on other clusters.
        In case of removal/appending new cluster, the cluster is matched with
        an empty dictionary (virtual agent).

        Example:
            [({1: {'A', 'B'}}, {3: {'A', 'B'}}),
             ({2: {'C'}}, {4: {'C', 'D'}})]
    """
    subproblems = []

    clusters_reversed = _dictionary_merge(
        _dictionary_reverse(clusters_before),
        _dictionary_reverse(clusters_after))

    keys_queue = list(clusters_before) + list(clusters_after)

    while keys_queue:
        node_checked = set()
        solution_before = {}
        solution_after = {}

        _check_node(keys_queue.pop(0), clusters_before, clusters_after,
                    clusters_reversed, keys_queue, node_checked,
                    solution_before, solution_after)

        subproblems.append((solution_before, solution_after))

    return _convert_clusters_to_sets(subproblems)


def _dictionary_merge(dictionary_left, dictionary_right):
    """Merge two dictionaries preserving values for the same key.

    :param dictionary_left:
        A valid dictionary with keys and values.

        Example:
            dictionary_left = {1: 'A', 2: ['B', 'C'], 3: []}

    :param dictionary_right:
        A valid dictionary with keys and values.

        Example:
            dictionary_right = {1: 'A', 2: 'C', 4: 'E'}

    :return:
        A merged dictionary, which preserves both values in the situation
        of a key conflict.

        Example:
            {1: ['A', 'A'], 2: [['B', 'C'], 'C'], 3: [[]], 4: ['E']}
    """
    merged_dictionary = {}

    for key in (viewkeys(dictionary_left) | viewkeys(dictionary_right)):
        if key in dictionary_left:
            merged_dictionary.setdefault(key, []).append(dictionary_left[key])
        if key in dictionary_right:
            merged_dictionary.setdefault(key, []).append(
                dictionary_right[key])

    return merged_dictionary


def _dictionary_reverse(dictionary_given):
    """Swap keys with values in the given dictionary.

    The given dictionary is reversed from key-value relation to
    value-key relation by creating a new dictionary. Since any
    signature cannot belong to more than one author, the dictionary
    will not have any occurrences of a signature more than once.
    However in case of more than one occurrence the new value will
    override the old value.

    :param dictionary_given:
        A standard dictionary with keys and values with
        len() attribute. In case of TypeError, the value
        will be skipped. The values must be provided in the
        form of lists.

        Example:
            dictionary_given = {1: ['A'], 2: ['B', 'C']}

    :return:
        A dictionary of swapped values with keys.

        Example:
            {'A': 1, 'B': 2, 'C': 2}
    """
    reversed_dictionary = {}

    for (key, value) in iteritems(dictionary_given):
        try:
            length = len(value)

            if length == 0:
                pass
            elif length == 1:
                reversed_dictionary[value[0]] = key
            else:
                for item in value:
                    reversed_dictionary[item] = key
        except TypeError:
            pass

    return reversed_dictionary
