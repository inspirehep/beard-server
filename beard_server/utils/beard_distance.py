# -*- coding: utf-8 -*-
#
# This file is part of Beard.
# Copyright (C) 2015 CERN.
#
# Beard is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Author disambiguation -- Tools for learning a distance model.

See README.rst for further details.

.. codeauthor:: Gilles Louppe <g.louppe@cern.ch>
.. codeauthor:: Mateusz Susik <mateusz.susik@cern.ch>
.. codeauthor:: Hussein Al-Natsheh <hussein.al.natsheh@cern.ch>

"""

import pickle
import json
import numpy as np
from scipy.special import expit

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline

from .beard_utils import get_author_full_name
from .beard_utils import get_author_other_names
from .beard_utils import get_author_affiliation
from .beard_utils import get_first_given_name
from .beard_utils import get_second_given_name
from .beard_utils import get_second_initial
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

from beard.similarity import AbsoluteDifference
from beard.similarity import CosineSimilarity
from beard.similarity import PairTransformer
from beard.similarity import StringDistance
from beard.similarity import EstimatorTransformer
from beard.similarity import ElementMultiplication
from beard.utils import FuncTransformer
from beard.utils import Shaper


def _build_distance_estimator(X, y, verbose=0, ethnicity_estimator=None,
                              fast=0):
    """Build a vector reprensation of a pair of signatures."""
    if fast == 0:
        transformer = FeatureUnion([
            ("author_full_name_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("full_name", FuncTransformer(func=get_author_full_name)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("author_second_initial_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=FuncTransformer(
                    func=get_second_initial
                ), groupby=group_by_signature)),
                ("combiner", StringDistance(
                    similarity_function="character_equality"))
            ])),
            ("author_first_given_name_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=FuncTransformer(
                    func=get_first_given_name
                ), groupby=group_by_signature)),
                ("combiner", StringDistance())
            ])),
            ("author_second_given_name_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=FuncTransformer(
                    func=get_second_given_name
                ), groupby=group_by_signature)),
                ("combiner", StringDistance())
            ])),
            ("author_other_names_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("other_names", FuncTransformer(
                        func=get_author_other_names)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("affiliation_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("affiliation", FuncTransformer(
                        func=get_author_affiliation)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("coauthors_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("coauthors", FuncTransformer(
                        func=get_coauthors_from_range)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("title_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("title", FuncTransformer(func=get_title)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("journal_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("journal", FuncTransformer(func=get_journal)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("abstract_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("abstract", FuncTransformer(func=get_abstract)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("keywords_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("keywords", FuncTransformer(func=get_keywords)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("collaborations_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("collaborations", FuncTransformer(
                        func=get_collaborations)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("subject_similairty", Pipeline([
               ("pairs", PairTransformer(element_transformer=Pipeline([
                   ("keywords", FuncTransformer(func=get_topics)),
                   ("shaper", Shaper(newshape=(-1))),
                   ("tf-idf", TfidfVectorizer(dtype=np.float32,
                                              decode_error="replace")),
               ]), groupby=group_by_signature)),
               ("combiner", CosineSimilarity())
            ])),
            ("year_diff", Pipeline([
                ("pairs", FuncTransformer(func=get_year, dtype=np.int)),
                ("combiner", AbsoluteDifference())
            ]))
        ])

    elif fast == 1:
        transformer = FeatureUnion([
            ("author_full_name_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("full_name", FuncTransformer(func=get_author_full_name)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("author_other_names_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("other_names", FuncTransformer(
                        func=get_author_other_names)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("affiliation_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("affiliation", FuncTransformer(
                        func=get_author_affiliation)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("coauthors_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("coauthors", FuncTransformer(
                        func=get_coauthors_from_range)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("title_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("title", FuncTransformer(func=get_title)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("year_diff", Pipeline([
                ("pairs", FuncTransformer(func=get_year, dtype=np.int)),
                ("combiner", AbsoluteDifference())
            ]))
        ])

    else:
        transformer = FeatureUnion([
            ("author_full_name_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("full_name", FuncTransformer(func=get_author_full_name)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("affiliation_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("affiliation", FuncTransformer(
                        func=get_author_affiliation)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(analyzer="char_wb",
                                               ngram_range=(2, 4),
                                               dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ])),
            ("coauthors_similarity", Pipeline([
                ("pairs", PairTransformer(element_transformer=Pipeline([
                    ("coauthors", FuncTransformer(
                        func=get_coauthors_from_range)),
                    ("shaper", Shaper(newshape=(-1,))),
                    ("tf-idf", TfidfVectorizer(dtype=np.float32,
                                               decode_error="replace")),
                ]), groupby=group_by_signature)),
                ("combiner", CosineSimilarity())
            ]))
        ])

    if ethnicity_estimator is not None:
        transformer.transformer_list.append(("author_ethnicity", Pipeline([
            ("pairs", PairTransformer(element_transformer=Pipeline([
                ("name", FuncTransformer(func=get_author_full_name)),
                ("shaper", Shaper(newshape=(-1,))),
                ("classifier", EstimatorTransformer(ethnicity_estimator)),
            ]), groupby=group_by_signature)),
            ("sigmoid", FuncTransformer(func=expit)),
            ("combiner", ElementMultiplication())
        ])))

    # Train a classifier on these vectors

    classifier = GradientBoostingClassifier(n_estimators=500,
                                            max_depth=9,
                                            max_features=10,
                                            learning_rate=0.125,
                                            verbose=verbose)

    # classifier = RandomForestClassifier(n_estimators=500,
    #                                     verbose=verbose,
    #                                     n_jobs=8)

    # Return the whole pipeline
    estimator = Pipeline([("transformer", transformer),
                          ("classifier", classifier)]).fit(X, y)

    return estimator


def learn_model(distance_pairs, input_signatures, input_records,
                distance_model, verbose=0, ethnicity_estimator=None,
                fast=False):
    """Learn the distance model for pairs of signatures.

    Parameters
    ----------
    :param distance_pairs: string
        Path to the file with signature pairs. The content should be a JSON
        array of tuples (`signature_id1`, `signature_id2`, `target`),
        where `target = 0` if both signatures belong to the same author,
        and `target = 1` otherwise.

        [(0, 1, 0), (2, 3, 0), (4, 5, 1), ...]

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
        Path to the file with the distance model. The file should be pickled.

    :param fast: boolean
        Whether the distance model should be built on a reduced set of
        features.
    """
    pairs = json.loads(distance_pairs)
    signatures, records = load_signatures(input_signatures, input_records)

    X = np.empty((len(pairs), 2), dtype=np.object)
    y = np.empty(len(pairs), dtype=np.int)

    for k, (i, j, target) in enumerate(pairs):
        X[k, 0] = signatures[i]
        X[k, 1] = signatures[j]
        y[k] = target

    # Learn a distance estimator on paired signatures
    distance_estimator = _build_distance_estimator(
        X, y,
        verbose=verbose, ethnicity_estimator=ethnicity_estimator, fast=fast
    )

    pickle.dump(distance_estimator,
                open(distance_model, "wb"),
                protocol=pickle.HIGHEST_PROTOCOL)
