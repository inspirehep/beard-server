# -*- coding: utf-8 -*-
#
# This file is part of Beard.
# Copyright (C) 2015 CERN.
#
# Beard is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Author disambiguation -- Clustering.

See README.rst for further details.

.. codeauthor:: Gilles Louppe <g.louppe@cern.ch>
.. codeauthor:: Mateusz Susik <mateusz.susik@cern.ch>

"""

import pickle
import json
import numpy as np

from functools import partial

from sklearn.cross_validation import train_test_split

# These imports are used during unpickling.
from .beard_utils import get_author_full_name
from .beard_utils import get_author_full_name
from .beard_utils import get_author_other_names
from .beard_utils import get_author_initials
from .beard_utils import get_surname
from .beard_utils import get_first_initial
from .beard_utils import get_second_initial
from .beard_utils import get_author_affiliation
from .beard_utils import get_title
from .beard_utils import get_journal
from .beard_utils import get_abstract
from .beard_utils import get_coauthors_from_range
from .beard_utils import get_keywords
from .beard_utils import get_collaborations
from .beard_utils import get_references
from .beard_utils import get_topics
from .beard_utils import get_year
from .beard_utils import group_by_signature
from .beard_utils import load_signatures

from beard.clustering import BlockClustering
from beard.clustering import block_last_name_first_initial
from beard.clustering import block_phonetic
from beard.clustering import ScipyHierarchicalClustering
from beard.metrics import b3_f_score
from beard.metrics import b3_precision_recall_fscore
from beard.metrics import paired_precision_recall_fscore


def _affinity(X, step=10000):
    """Custom affinity function, using a pre-learned distance estimator."""
    # Assumes that 'distance_estimator' lives in global, making things fast
    global distance_estimator

    all_i, all_j = np.triu_indices(len(X), k=1)
    n_pairs = len(all_i)
    distances = np.zeros(n_pairs, dtype=np.float64)

    for start in range(0, n_pairs, step):
        end = min(n_pairs, start+step)
        Xt = np.empty((end-start, 2), dtype=np.object)

        for k, (i, j) in enumerate(zip(all_i[start:end],
                                       all_j[start:end])):
            Xt[k, 0], Xt[k, 1] = X[i, 0], X[j, 0]

        Xt = distance_estimator.predict_proba(Xt)[:, 1]
        distances[start:end] = Xt[:]

    return distances


def clustering(input_signatures, input_records, distance_model,
               input_clusters=None, verbose=1, n_jobs=-1,
               clustering_method="average", train_signatures_file=None,
               clustering_threshold=None, results_file=None,
               blocking_function="block_phonetic",
               blocking_threshold=1, blocking_phonetic_alg="nysiis"):
    """Cluster signatures using a pretrained distance model.

    Parameters
    ----------
    :param input_signatures: string
        Path to the file with signatures. The content should be a JSON array
        of dictionaries holding metadata about signatures.

        [{"signature_id": 0,
          "author_name": "Doe, John",
          "publication_id": 10, ...}, { ... }, ...]

    :param input_records: string
        Path to the file with records. The content should be a JSON array of
        dictionaries holding metadata about records

        [{"publication_id": 0,
          "title": "Author disambiguation using Beard", ... }, { ... }, ...]

    :param distance_model: string
        Path to the file with the distance model. The file should be a pickle
        created using the ``distance.py`` script.

    :param input_clusters: string
        Path to the file with knownn clusters. The file should be a dictionary,
        where keys are cluster labels and values are the `signature_id` of the
        signatures grouped in the clusters. Signatures assigned to the cluster
        with label "-1" are not clustered.

        {"0": [0, 1, 3], "1": [2, 5], ...}

    :param verbose: int
        If not zero, function will output scores on stdout.

    :param n_jobs: int
        Parameter passed to joblib. Number of threads to be used.

    :param clustering_method: string
        Parameter passed to ``ScipyHierarchicalClustering``. Used only if
        ``clustering_test_size`` is specified.

    :param train_signatures_file: str
        Path to the file with train set signatures. Format the same as in
        ``input_signatures``.

    :param clustering_threshold: float
        Threshold passed to ``ScipyHierarchicalClustering``.

    :param results_file: str
        Path to the file where the results will be output. It will give
        additional information about pairwise variant of scores.

    :param blocking_function: string
        must be a defined blocking function. Defined functions are:
        - "block_last_name_first_initial"
        - "block_phonetic"

    :param blocking_threshold: int or None
        It determines the maximum allowed size of blocking on the last name
        It can only be:
        -   None; if the blocking function is block_last_name_first_initial
        -   int; if the blocking function is block_phonetic
            please check the documentation of phonetic blocking in
            beard.clustering.blocking_funcs.py

    :param blocking_phonetic_alg: string or None
        If not None, determines which phonetic algorithm is used. Options:
        -  "double_metaphone"
        -  "nysiis" (only for Python 2)
        -  "soundex" (only for Python 2)
    """
    # Assumes that 'distance_estimator' lives in global, making things fast
    global distance_estimator
    distance_estimator = pickle.load(open(distance_model, "rb"))

    try:
        distance_estimator.steps[-1][1].set_params(n_jobs=1)
    except:
        pass

    signatures, records = load_signatures(input_signatures,
                                          input_records)

    indices = {}
    X = np.empty((len(signatures), 1), dtype=np.object)
    for i, signature in enumerate(sorted(signatures.values(),
                                         key=lambda s: s["signature_id"])):
        X[i, 0] = signature
        indices[signature["signature_id"]] = i

    if blocking_function == "block_last_name_first_initial":
        block_function = block_last_name_first_initial
    else:
        block_function = partial(block_phonetic,
                                 threshold=blocking_threshold,
                                 phonetic_algorithm=blocking_phonetic_alg)

    # Semi-supervised block clustering
    if input_clusters:
        y_true = -np.ones(len(X), dtype=np.int)

        for label, signature_ids in input_clusters.items():
            for signature_id in signature_ids:
                y_true[indices[signature_id]] = label

        y = -np.ones(len(X), dtype=np.int)

        if train_signatures_file:
            train_signatures = json.load(open(train_signatures_file, "r"))
            train_ids = [x['signature_id'] for x in train_signatures]
            del train_signatures
            y[train_ids] = y_true[train_ids]
        else:
            y = y_true

    else:
        y = None

    clusterer = BlockClustering(
        blocking=block_function,
        base_estimator=ScipyHierarchicalClustering(
            affinity=_affinity,
            threshold=clustering_threshold,
            method=clustering_method,
            supervised_scoring=b3_f_score),
        verbose=verbose,
        n_jobs=n_jobs).fit(X, y)

    labels = clusterer.labels_

    # Save predicted clusters
    clusters = {}

    for label in np.unique(labels):
        mask = (labels == label)
        clusters[str(label)] = [r[0]["signature_id"] for r in X[mask]]

    return clusters
