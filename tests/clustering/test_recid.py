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

"""Test recid clustering algorithm."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals


def test_claimed_recids():
    """Test if claimed signatures will be clustered together."""
    from beard_server.modules.clustering.recid import make_recid_clusters

    signatures = [{'signature_id': 'ABC', 'author_recid': '1',
                   'author_claimed': True},
                  {'signature_id': 'CDE', 'author_recid': '1',
                   'author_claimed': True},
                  {'signature_id': 'FGH', 'author_recid': '2',
                   'author_claimed': True},
                  {'signature_id': 'XYZ', 'author_recid': '2',
                   'author_claimed': False}]

    output = {'1': ['ABC', 'CDE'], '2': ['FGH']}

    assert make_recid_clusters(signatures, claimed_only=True) == output


def test_claimed_recids_with_missing_data():
    from beard_server.modules.clustering.recid import make_recid_clusters

    signatures = [{'signature_id': 'ABC', 'author_claimed': True},
                  {'author_recid': '1', 'author_claimed': True}]

    output = {}

    assert make_recid_clusters(signatures, claimed_only=True) == output


def test_recids():
    """Test if the two exact clusters will be matched."""
    from beard_server.modules.clustering.recid import make_recid_clusters

    signatures = [{'signature_id': 'ABC', 'author_recid': '1'},
                  {'signature_id': 'CDE', 'author_recid': '1'},
                  {'signature_id': 'XYZ', 'author_recid': '2'}]

    output = {'1': ['ABC', 'CDE'], '2': ['XYZ']}

    assert make_recid_clusters(signatures, claimed_only=False) == output


def test_missing_recids():
    """Test if signatures with no recids will be skipped."""
    from beard_server.modules.clustering.recid import make_recid_clusters

    signatures = [{'signature_id': 'ABC', 'author_recid': '1'},
                  {'signature_id': 'XYZ', 'author_recid': False}]

    output = {'1': ['ABC']}

    assert make_recid_clusters(signatures, claimed_only=False) == output


def test_broken_signatures():
    """Test if signatures with no valid fields will be skipped."""
    from beard_server.modules.clustering.recid import make_recid_clusters

    signatures = [{'uuid': 'ABC', 'recid': '1'},
                  {'signature_id': 'CDE'},
                  {'recid': '2'}]

    output = {}

    assert make_recid_clusters(signatures, claimed_only=False) == output
