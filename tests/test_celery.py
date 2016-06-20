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

"""Test Celery tasks."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals


def test_make_clusters_new_signatures():
    """Test if signatures will be allocated in bucket for new signatures.

    This test checks if new signatures will be clustered together,
    and then put in the second bucket, which contains new signatures.
    """
    from beard_server.tasks import make_clusters

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
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Wang, Shang-Yung",
            "publication_id": 428605,
            "signature_id": "Wang_428605",
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Lin, Shih-Yuin",
            "publication_id": 428605,
            "signature_id": "Lin_428605",
        }
    ]

    # Bucket with new clusters only.
    result = ({}, {'0': ['Lin_428605'],
                   '1': ['Wang_1395222', 'Wang_428605']})

    assert make_clusters(records, signatures) == result


def test_make_clusters_profile_exists():
    """Test if signatures will be allocated in bucket for matched
    signatures.

    This test checks if signatures, which already have profiles
    will be clustered together, and then put in the first bucket,
    which contains signatures matched by recid and Beard together.
    """

    from beard_server.tasks import make_clusters

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
            "author_recid": "A",
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Wang, Shang-Yung",
            "publication_id": 428605,
            "signature_id": "Wang_428605",
            "author_recid": "A",
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Lin, Shih-Yuin",
            "publication_id": 428605,
            "signature_id": "Lin_428605",
            "author_recid": "B",
        }
    ]

    # Bucket with old clusters only.
    result = ({'A': ['Wang_1395222', 'Wang_428605'], 'B': ['Lin_428605']},
              {})

    assert make_clusters(records, signatures) == result


def test_make_clusters_profile_exists_new_arrives():
    """Test if signatures will be allocated in buckets for matched
    and new signatures.

    This test checks what will happen if a system already has some
    signatures with profiles assigned to them and a new signature
    is arriving. The output should show two signatures clustered together
    in "old" bucket and a new signature in the bucket for new data.
    """
    from beard_server.tasks import make_clusters

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
            "author_recid": "A",
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Wang, Shang-Yung",
            "publication_id": 428605,
            "signature_id": "Wang_428605",
            "author_recid": "A",
        },
        {
            "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
            "author_name": "Lin, Shih-Yuin",
            "publication_id": 428605,
            "signature_id": "Lin_428605",
        }
    ]

    # Bucket with old clusters only.
    result = ({'A': ['Wang_1395222', 'Wang_428605']},
              {'0': ['Lin_428605']})

    assert make_clusters(records, signatures) == result


def test_conflict_resolver():
    """This methods checks conflict resolver."""
    from beard_server.tasks import solve_conflicts

    claimed_signatures = [{
        'author_affiliation': 'Peking U.',
        'publication_id': '13c3cca8-b0bf-42f5-90d4-e3dfcced0511',
        'author_name': 'Wang, Yi-Nan',
        'signature_id': 'd63537a8-1df4-4436-b5ed-224da5b5028c',
        'publication': {
            'collaboration': False,
            'authors': ['Hohm, Olaf', 'Wang, Yi-Nan'],
            'publication_id': '13c3cca8-b0bf-42f5-90d4-e3dfcced0511',
            'year': '2015'
        }}
    ]

    not_claimed_signatures = [{
        'author_affiliation': 'Peking U.',
        'publication_id': '1a16f6ba-7428-479c-8ff6-274d699e3f7b',
        'author_name': 'Wang, Yi-Nan',
        'signature_id': 'fcf53cb9-2d19-433b-b735-f6c1de9a6d57',
        'publication': {
            'collaboration': False,
            'authors': ['Washington Taylor', 'Yi-Nan Wang'],
            'publication_id': '1a16f6ba-7428-479c-8ff6-274d699e3f7b',
            'year': '2015'
        }}
    ]

    result = {
        'd63537a8-1df4-4436-b5ed-224da5b5028c': [
            'fcf53cb9-2d19-433b-b735-f6c1de9a6d57'
        ]
    }

    assert solve_conflicts(
        claimed_signatures, not_claimed_signatures) == result
