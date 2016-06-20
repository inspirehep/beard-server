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

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import os
import pickle

import numpy as np


def solve_claims_conflict(claimed_signatures, not_claimed_signatures):
    """Match signatures to the most likely claimed signatures.

    If Beard will cluster at least two different (claimed) signatures
    into one author, then the conflict must be resolved.

    The method creates buckets representing each of the claimed authors
    and then, using _affinity method, calculates the probability of
    each not-claimed signature to belong to one of these buckets.
    The highest probability is selected, thus it is more likely that
    not claimed signature belongs to the selected claimed author.

    :param claimed_signatures:
        A list of claimed signatures in Beard readable format,
        including record data.

        Example:
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

    :param not_claimed_signatures:
        A list of not-claimed signatures to be clustered, ie.
        assigned to one of the claimed ones, including record data.

        Example:
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

    :return:
        A dictionary of manually clustered signatures, where the keys
        represent uuids of claimed signatures and values are the lists
        of not-claimed ones.

        Example:
            {'d63537a8-1df4-4436-b5ed-224da5b5028c':
                ['fcf53cb9-2d19-433b-b735-f6c1de9a6d57']}
    """
    # Prepare results dictionary.
    results = {}

    for claimed_signature in claimed_signatures:
        results[claimed_signature['signature_id']] = []

    claimed_signatures_map = dict(enumerate(results.keys()))

    # Load the linkage model.
    distance_model = os.path.abspath(os.path.join(os.path.dirname(
                                     __file__), 'classifiers/linkage.dat'))
    distance_estimator = pickle.load(open(distance_model, 'rb'))

    try:
        distance_estimator.steps[-1][1].set_params(n_jobs=1)
    except:
        pass

    for not_claimed_signature in not_claimed_signatures:
        X = np.empty((len(claimed_signatures), 2), dtype=np.object)

        for claimed_index, claimed_signature in enumerate(claimed_signatures):
            X[claimed_index] = \
                not_claimed_signature, claimed_signature

        # Position of the claimed signature to represent the same author.
        position = np.argmax(distance_estimator.predict_proba(X)[:, 0])
        results[claimed_signatures_map[position]].append(
            not_claimed_signature['signature_id'])

    return results
