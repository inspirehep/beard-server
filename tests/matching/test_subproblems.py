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

"""Test the dividing algorithm."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import pytest


def test_splitting():
    """Test if the method splits correctly."""
    from beard_server.modules.matching.subproblems import \
        _divide_into_subproblems

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

    match = _divide_into_subproblems(partition_before, partition_after)
    expected_match = [({1: set(['A', 'B', 'C']), 2: set(['D', 'E']),
                        3: set(['F'])},
                       {6: set(['A', 'B']), 7: set(['C', 'D']),
                        8: set(['E', 'F'])}),
                      ({4: set(['G'])}, {9: set(['G'])}),
                      ({5: set(['H'])}, {}),
                      ({}, {10: set(['I'])})]

    assert match == expected_match


def test_empty_value():
    """Test if the method passes empty values correctly."""
    from beard_server.modules.matching.subproblems import \
        _divide_into_subproblems

    partition_before = {1: ["A", "B", "C"],
                        2: []}

    partition_after = {3: ["A", "B"],
                       4: ["C", "D"]}

    match = _divide_into_subproblems(partition_before, partition_after)
    expected_match = [({1: set(['A', 'B', 'C'])},
                       {3: set(['A', 'B']), 4: set(['C', 'D'])}),
                      ({2: set()}, {})]

    assert match == expected_match


def test_type_error():
    """Test if the method fails on values with no len() attribute."""
    from beard_server.modules.matching.subproblems import \
        _divide_into_subproblems

    partition_before = {1: 42}

    partition_after = {}

    with pytest.raises(TypeError):
        _divide_into_subproblems(partition_before, partition_after)
