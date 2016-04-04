# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from __future__ import absolute_import

import os
import pickle

from .celery import app
from .utils import clustering
from .utils import learn_model
from .utils import pair_sampling


@app.task
def make_clusters(signatures, records):
    # Default values.
    blocking_function = "block_phonetic"
    blocking_threshold = 0
    blocking_phonetic_alg = "nysiis"
    clustering_threshold = 0.709
    verbose = 0
    n_jobs = 16

    try:
        # Distance model as a path to the file.
        distance_model = os.path.abspath(os.path.join(os.path.dirname(
                         __file__), 'data/linkage.dat'))

        return clustering(input_signatures=signatures,
                          input_records=records, distance_model=distance_model,
                          verbose=verbose, n_jobs=n_jobs,
                          clustering_threshold=clustering_threshold,
                          blocking_function=blocking_function,
                          blocking_threshold=blocking_threshold,
                          blocking_phonetic_alg=blocking_phonetic_alg)
    except IOError:
        """Probably the file does not exist, ie. the model was not trained."""
        return "ERR: linkage.dat file not found. Train the model."


@app.task
def train_model(signatures, records, clusters):
    """Train the model, which later will be for clustering."""

    # The first step is to create a set of labeled pairs.
    balanced = 1
    sample_size = 500000
    use_blocking = 1
    blocking_function = 'block_phonetic'
    blocking_threshold = 1
    blocking_phonetic_alg = 'nysiis'

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

    # The second step is about creating linkage.dat file (model).
    distance_model = os.path.abspath(os.path.join(os.path.dirname(
                     __file__), 'data/linkage.dat'))
    ethnicity_estimator = pickle.load(open(os.path.abspath(os.path.join(
                          os.path.dirname(__file__),
                          'data/ethnicity_estimator.pickle')), 'r'))
    # Fast: 0 - all features, 1: fast features,
    #       2: co-authors, affiliation, full name.
    fast = 2
    verbose = 0

    try:
        learn_model(
            distance_pairs=output_pairs,
            input_signatures=signatures,
            input_records=records,
            distance_model=distance_model,
            verbose=verbose,
            ethnicity_estimator=ethnicity_estimator,
            fast=fast)
    except:
        return "ERR: linkage.dat couldn't be created."
