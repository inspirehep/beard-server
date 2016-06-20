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

"""Bibliographic Entity Automatic Recognition and Disambiguation."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import cPickle as pickle
import os

from .utils import clustering, learn_model, pair_sampling
from .recid import make_recid_clusters


def predict(records, signatures, clusters=False):
    # Default parameters for clustering signatures.
    blocking_function = 'block_phonetic'
    blocking_threshold = 0
    blocking_phonetic_alg = 'nysiis'
    clustering_threshold = 0.709
    verbose = 0

    # Note that beard-server already receives phonetic blocks in packages.
    n_jobs = 1

    # Paths, where the model is stored.
    distance_model = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'classifiers/linkage.dat'))

    # Create known clusters.
    if clusters:
        known_clusters = make_recid_clusters(signatures, True)
    else:
        known_clusters = None

    return clustering(input_signatures=signatures,
                      input_records=records,
                      input_clusters=known_clusters,
                      distance_model=distance_model,
                      verbose=verbose, n_jobs=n_jobs,
                      clustering_threshold=clustering_threshold,
                      blocking_function=blocking_function,
                      blocking_threshold=blocking_threshold,
                      blocking_phonetic_alg=blocking_phonetic_alg)


def train(clusters, records, signatures):
    # Default parameters for training a model.
    balanced = 1
    sample_size = 500000
    use_blocking = 1
    blocking_function = 'block_phonetic'
    blocking_threshold = 1
    blocking_phonetic_alg = 'nysiis'

    # Sampling step.
    output_pairs = pair_sampling(
        train_filename=signatures,
        clusters_filename=clusters,
        balanced=balanced,
        sample_size=sample_size,
        use_blocking=use_blocking,
        blocking_function=blocking_function,
        blocking_threshold=blocking_threshold,
        blocking_phonetic_alg=blocking_phonetic_alg,
    )

    # Paths, where model will be stored and ethnicity model can be found.
    distance_model = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'classifiers/linkage.dat'))
    ethnicity_estimator = pickle.load(open(os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'classifiers/ethnicity_estimator.pickle')), 'r'))

    # Training with full name, co-authors and affiliation features.
    fast = 2
    verbose = 0

    learn_model(
        distance_pairs=output_pairs,
        input_signatures=signatures,
        input_records=records,
        distance_model=distance_model,
        verbose=verbose,
        ethnicity_estimator=ethnicity_estimator,
        fast=fast)
