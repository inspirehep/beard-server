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

"""Predictor endpoint."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import cPickle as pickle
import os

from flask import (
    abort,
    Blueprint,
    jsonify,
    request)

from .arxiv import (
    train as learn_model,
    predict as coreness)

blueprint = Blueprint(
    'beard_server_predictor',
    __name__,
    url_prefix='/api/predictor',
)


@blueprint.route('/', methods=['GET'])
def available_methods():
    """List of available methods to call as the part of API."""
    available = {
        "coreness": {
            "path": "/api/predictor/coreness",
            "method": "[POST]",
            "example": {
                "body": {
                    "abstract": "".join([
                        "We report the detection of an ",
                        "infrared selected transient which has lasted at ",
                        "least 5 years, first identified by a large ",
                        "mid-infrared and optical outburst from a faint ",
                        "X-ray source detected with the Chandra X-ray ",
                        "Observatory. In this paper we rule out several ",
                        "scenarios for the cause of this outburst, including ",
                        "a classical nova, a luminous red nova, AGN flaring, ",
                        "a stellar merger, and intermediate luminosity ",
                        "optical transients, and interpret this transient ",
                        "as the result of a Young Stellar Object (YSO) of ",
                        "at least solar mass accreting material from the ",
                        "remains of the dusty envelope from which it ",
                        "formed, in isolation from either a dense complex ",
                        "of cold gas or massive star formation. This ",
                        "object does not fit neatly into other existing ",
                        "categories of large outbursts of YSOs ",
                        "(FU Orionis types) which may be a result of ",
                        "the object's mass, age, and environment. ",
                        "It is also possible that this object is a new ",
                        "type of transient unrelated to YSOs."]),
                    "categories": ["astro-ph"],
                    "title": "".join(["Discovery of a Long-Lived, High",
                                      "Amplitude Dusty Infrared Transient"])
                },
                "header": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "response": {
                    "decision": "Non-CORE",
                    "scores": [
                        -1.2487082195061714,
                        1.375354035683761,
                        -3.064134460779941
                    ]
                }
            }
        },
        "train": {
            "path": "/api/predictor/train",
            "method": "[POST]",
            "example": {
                "body": [{
                    "title": "".join([
                        "Geodesics dynamics in the Linet-Tian spacetime ",
                        "with Lambda&lt;0"]),
                    "collaborations": [],
                    "abstract": "".join([
                        "We investigate the geodesics' kinematics and ",
                        "dynamics in the Linet-Tian metric with Lambda&lt;0 ",
                        "and compare with the results for the Levi-Civita ",
                        "metric, when Lambda=0. This is used to derive new ",
                        "stability results about the geodesics' dynamics in ",
                        "static vacuum cylindrically symmetric spacetimes ",
                        "with respect to the introduction of Lambda&lt;0. In ",
                        "particular, we find that increasing |Lambda| always ",
                        "increases the minimum and maximum radial distances ",
                        "to the axis of any spatially confined planar null ",
                        "geodesic. Furthermore, we show that, in some cases, ",
                        "the inclusion of any Lambda&lt;0 breaks the ",
                        "geodesics' orbit confinement of the Lambda=0 ",
                        "metric, for both planar and non-planar null ",
                        "geodesics, which are therefore unstable. Using ",
                        "the full system of geodesics' equations, we ",
                        "provide numerical examples which illustrate our ",
                        "results."]),
                    "id": "1403.3858",
                    "recid": 1286143,
                    "authors": [
                        "Irene Brito",
                        "M. F. A. da Silva",
                        "Filipe C. Mena",
                        "N. O. Santos"
                    ],
                    "pdf": "http://arxiv.org/pdf/1403.3858v1",
                    "decision": "CORE",
                    "journal": "null",
                    "categories": [
                        "gr-qc"
                    ]
                }],
                "header": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "response": {
                    "success": True
                }
            }
        }
    }

    return jsonify(available)


@blueprint.route('/coreness', methods=['POST'])
def guess_coreness():
    coreness_data = request.get_json(silent=True)

    if not coreness_data:
        # Missing data.
        abort(400)

    try:
        # Paths, where the model is stored.
        distance_model_path = os.path.abspath(os.path.join(os.path.dirname(
            __file__), 'classifiers/linkage.dat'))

        distance_model = pickle.load(open(distance_model_path, 'rb'))
    except IOError:  # pragma: no cover
        # Probably the file does not exist, ie. the model was not trained.
        abort(404)

    decision, scores = coreness(distance_model, coreness_data)

    return jsonify({"decision": decision,
                    "scores": scores.tolist()})


@blueprint.route('/train', methods=['POST'])
def train_model():
    training_data = request.get_json(silent=True)

    if not training_data:
        # Missing data.
        abort(400)

    # Path, where model will be stored.
    distance_model = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'classifiers/linkage.dat'))

    try:
        pipeline = learn_model(training_data)
        pickle.dump(pipeline, open(distance_model, 'w'))

        # Acknowledge successful training.
        return jsonify({"success": True})
    except:
        # Training of a new model has failed.
        abort(500)
