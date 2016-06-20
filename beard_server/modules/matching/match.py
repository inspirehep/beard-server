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

"""Methods to match existing clusters with Beard's output."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from .simplex import _solve_clusters

from .subproblems import _divide_into_subproblems


def match_clusters(clusters_before, clusters_after):
    """Split the given clusters into subproblems, then match.

    The method matches provided clusters into pairs of clusters,
    clusters that are new and clusters to remove.
    Values of the provided clusters (dictionaries) must be in the
    form of lists.

    :param clusters_before:
        A dictionary containing clustered data from the-state-before.

        Example:
            clusters_before = {"1": ["A", "B"], "2": ["C"], "3": ["D"]}

    :param clusters_after:
        A dictionary containing clustered data from the-state-after.

        Example:
            clusters_after = {"4": ["A", "B"], "5": ["C"], "6": ["E"]}

    :return:
        The method returns three buckets (lists) containing the keys of matched
        clusters (as pairs), clusters to add and clusters to remove.

        Example:
            ([(1, 4), (2, 5)], [6], [3])
    """
    bucket_matched = []
    bucket_new = []
    bucket_removed = []

    # Copy and rename keys of the given dictionaries to avoid a key collision.
    clusters_before_copy = {}
    clusters_after_copy = {}
    key_map = {}

    for key in clusters_before.keys():
        new_key = 'before_%r' % key
        key_map[new_key] = key
        clusters_before_copy[new_key] = clusters_before[key]

    for key in clusters_after.keys():
        new_key = 'after_%r' % key
        key_map[new_key] = key
        clusters_after_copy[new_key] = clusters_after[key]

    for subproblem_before, subproblem_after in _divide_into_subproblems(
            clusters_before_copy, clusters_after_copy):

        matching_result = _solve_clusters(subproblem_before,
                                          subproblem_after)

        if matching_result[0]:
            bucket_matched.extend(matching_result[0])

        if matching_result[1]:
            bucket_new.extend(matching_result[1])

        if matching_result[2]:
            bucket_removed.extend(matching_result[2])

    # Return the original key names.
    for index, pair in enumerate(bucket_matched):
        bucket_matched[index] = (key_map[pair[0]], key_map[pair[1]])

    for index, new in enumerate(bucket_new):
        bucket_new[index] = key_map[new]

    for index, removed in enumerate(bucket_removed):
        bucket_removed[index] = key_map[removed]

    return bucket_matched, bucket_new, bucket_removed
