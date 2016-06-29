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

"""Test the matching algorithm."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json
import os
import pkg_resources


def test_the_same_clusters():
    """Test if the two exact clusters will be matched."""
    from beard_server.modules.matching import match_clusters

    signatures_before = {1: ['A', 'B']}
    signatures_after = {2: ['A', 'B']}

    match = match_clusters(signatures_before, signatures_after)

    assert match == ([(1, 2)], [], [])


def test_cluster_adding():
    """Test if the new cluster will be distinguished."""
    from beard_server.modules.matching import match_clusters

    partition_before = {}
    partition_after = {1: ['A', 'B']}

    match = match_clusters(partition_before, partition_after)

    assert match == ([], [1], [])


def test_cluster_removal():
    """Test if the removed cluster will be distinguished."""
    from beard_server.modules.matching import match_clusters

    partition_before = {1: ['A', 'B']}
    partition_after = {}

    match = match_clusters(partition_before, partition_after)

    assert match == ([], [], [1])


def test_complex_matching():
    """Test more complex clustering with no removal or adding."""
    from beard_server.modules.matching import match_clusters

    partition_before = {1: ['A', 'B'], 2: ['C', 'D', 'E']}
    partition_after = {3: ['A', 'C', 'E'], 4: ['B', 'D']}

    match = match_clusters(partition_before, partition_after)

    assert match == ([(1, 4), (2, 3)], [], [])


def test_complex_adding():
    """Test more complex clustering with adding a new cluster."""
    from beard_server.modules.matching import match_clusters

    partition_before = {1: ['A', 'B', 'C']}
    partition_after = {2: ['A', 'B'], 3: ['C']}

    match = match_clusters(partition_before, partition_after)

    assert match == ([(1, 2)], [3], [])


def test_complex_removal():
    """Test more complex clustering with removing a cluster."""
    from beard_server.modules.matching import match_clusters

    partition_before = {1: ['A', 'B'], 2: ['C']}
    partition_after = {3: ['A', 'B', 'C']}

    match = match_clusters(partition_before, partition_after)

    assert match == ([(1, 3)], [], [2])


def test_complex_subproblems():
    """Test the case, where there are at least two subproblems."""
    from beard_server.modules.matching import match_clusters

    partition_before = {1: ["A", "B", "C"],
                        2: ["D", "E"],
                        3: ["F"],
                        4: ["G"],
                        5: ["H"]}

    partition_after = {6: ["A", "B"],
                       7: ["C", "D"],
                       8: ["E", "F"],
                       9: ["G"],
                       10: ["I"]}

    match = match_clusters(partition_before, partition_after)

    assert match == ([(4, 9), (1, 6), (2, 7), (3, 8)], [10], [5])


def test_wang_signtures():
    """Test the real output of Beard."""
    from beard_server.modules.matching import match_clusters

    with open(pkg_resources.resource_filename(
        __name__, os.path.join('data', 'wang_clusters_1.json')),
            'r') as file_before:

        signatures_before = json.load(file_before)

    match = match_clusters(signatures_before, signatures_before)

    assert match == ([(u'158992', u'158992'), (u'623639', u'623639'),
                      (u'623638', u'623638')], [], [])


def test_wang_signtures_mixed_up():
    """Test the real output of Beard."""
    from beard_server.modules.matching import match_clusters

    with open(pkg_resources.resource_filename(
        __name__, os.path.join('data', 'wang_clusters_1.json')),
            'r') as file_before:

        signatures_before = json.load(file_before)

    with open(pkg_resources.resource_filename(
        __name__, os.path.join('data', 'wang_clusters_2.json')),
            'r') as file_after:

        signatures_after = json.load(file_after)

    match = match_clusters(signatures_before, signatures_after)

    assert match == ([(u'158992', u'158992'), (u'623639', u'623639')],
                     [u'623638_to_add'], [u'623638'])


def test_almost_the_same_keys():
    """Test the case where the keys are the same after casting."""
    from beard_server.modules.matching import match_clusters

    partition_before = {1: ["A", "B", "C"],
                        "1": ["D", "E"]}

    partition_after = {1: ["A", "B", "C"],
                       "1": ["D", "E"]}

    match = match_clusters(partition_before, partition_after)

    assert match == ([('1', '1'), (1, 1)], [], [])
