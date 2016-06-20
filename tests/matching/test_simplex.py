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

"""Test the simplex algorithm."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals


def test_the_same_clusters():
    """Test if the two exact clusters will be matched."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {1: set(['A', 'B'])}
    partition_after = {2: set(['A', 'B'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([(1, 2)], [], [])


def test_cluster_adding():
    """Test if the new cluster will be distinguished."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {}
    partition_after = {1: set(['A', 'B'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([], [1], [])


def test_cluster_removal():
    """Test if the removed cluster will be distinguished."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {1: set(['A', 'B'])}
    partition_after = {}

    match = _solve_clusters(partition_before,
                            partition_after)

    assert match == ([], [], [1])


def test_complex_matching():
    """Test more complex clustering with no removal or adding."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {1: set(['A', 'B']), 2: set(['C', 'D', 'E'])}
    partition_after = {3: set(['A', 'C', 'E']), 4: set(['B', 'D'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([(1, 4), (2, 3)], [], [])


def test_complex_adding():
    """Test more complex clustering with adding a new cluster."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {1: set(['A', 'B', 'C'])}
    partition_after = {2: set(['A', 'B']), 3: set(['C'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([(1, 2)], [3], [])


def test_complex_removal():
    """Test more complex clustering with removing a cluster."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {1: set(['A', 'B']), 2: set(['C'])}
    partition_after = {3: set(['A', 'B', 'C'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([(1, 3)], [], [2])


def test_strings_as_keys():
    """Test clustering based on strings as keys."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {"1": set(['A', 'B']), "2": set(['C'])}
    partition_after = {"3": set(['A', 'B', 'C'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([('1', '3')], [], ['2'])


def test_different_types_as_keys():
    """Test clustering based on strings as keys."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {1: set(['A', 'B']), "2": set(['C'])}
    partition_after = {"3": set(['A', 'B', 'C']), 4: set(['E', 'F'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([(1, '3')], [4], ['2'])


def test_many_virtual_agents():
    """Test clustering based on strings as keys."""
    from beard_server.modules.matching.simplex import _solve_clusters

    partition_before = {1: set(['A'])}
    partition_after = {1: set(['A', 'B', 'C']), 2: set(['D']),
                       "3": set(['E', 'F'])}

    match = _solve_clusters(partition_before, partition_after)

    assert match == ([(1, 1)], ['3', 2], [])
