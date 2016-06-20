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

"""Test Beard clustering algorithm."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals


def test_beard_known_clusters():
    """Beard with already known clusters (profiles) supplied."""
    from beard_server.modules.clustering.beard import predict

    records = [
        {
            "title": "Towards graphene-based detectors for" +
                     " dark matter directional detection",
            "year": 2015,
            "publication_id": 1395222,
            "authors": [
                "Wang, Shang-Yung"
            ]
        }, {
            "title": "Induced Einstein-Kalb-Ramond theory and" +
                     " the black hole",
            "year": 1996,
            "publication_id": 428605,
            "authors": [
                "Kao, W.F.",
                "Chyi, Tzuu-Kang",
                "Dai, W.B.",
                "Wang, Shang-Yung",
                "Lin, Shih-Yuun"
            ]
        }
    ]

    signatures = [
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Wang, Shang-Yung",
            "publication_id": 1395222,
            "signature_id": "Wang_1395222",
            "author_recid": 1,
            "author_claimed": True
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Wang, Shang-Yung",
            "publication_id": 428605,
            "signature_id": "Wang_428605",
            "author_recid": 1,
            "author_claimed": True
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Lin, Shih-Yuin",
            "publication_id": 428605,
            "signature_id": "Lin_428605",
        }
    ]

    result = {'0': ['Lin_428605'], '1': ['Wang_1395222', 'Wang_428605']}

    assert predict(records, signatures, clusters=True) == result
