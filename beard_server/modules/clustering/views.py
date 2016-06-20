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

"""Clustering endpoint."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from flask import abort, Blueprint, jsonify, request

from .beard import predict as clustering
from .beard import train as learn_model

blueprint = Blueprint(
    'beard_server_clustering',
    __name__,
    url_prefix='/api/clustering',
)


@blueprint.route('/', methods=['GET'])
def available_methods():
    """List of available methods to call as the part of API."""
    available = {
        "clusters": {
            "path": "/api/clustering/clusters",
            "method": "[POST]",
            "example": {
                "body": {
                    "signatures": [{
                        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
                        "author_name": "Wang, Shang-Yung",
                        "publication_id": 1395222,
                        "signature_id": "Wang_1395222"
                    }, {
                        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
                        "author_name": "Wang, Shang-Yung",
                        "publication_id": 428605,
                        "signature_id": "Wang_428605"
                    }, {
                        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
                        "author_name": "Lin, Shih-Yuin",
                        "publication_id": 428605,
                        "signature_id": "Lin_428605"
                    }],
                    "records": [{
                        "title": "".join(["Towards graphene-based detectors",
                                "for dark matter directional detection"]),
                        "year": 2015,
                        "publication_id": 1395222,
                        "authors": ["Wang, Shang-Yung"]
                    }, {
                        "title": "".join(["Induced Einstein-Kalb-Ramond",
                                          "theory and the black hole"]),
                        "year": 1996,
                        "publication_id": 428605,
                        "authors": [
                            "Kao, W.F.",
                            "Chyi, Tzuu-Kang",
                            "Dai, W.B.",
                            "Wang, Shang-Yung",
                            "Lin, Shih-Yuun"
                        ]
                    }]
                },
                "header": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "response": {
                    "0": ["Lin_428605"],
                    "1": ["Wang_1395222", "Wang_428605"]
                }
            }
        },
        "train": {
            "path": "/api/clustering/train",
            "method": "[POST]",
            "example": {
                "body": {
                    "clusters": [{
                        "0": ["Wang_1395222", "Wang_428605"],
                        "1": ["Lin_428605"]
                    }],
                    "signatures": [{
                        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
                        "author_name": "Wang, Shang-Yung",
                        "publication_id": 1395222,
                        "signature_id": "Wang_1395222"
                    }, {
                        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
                        "author_name": "Wang, Shang-Yung",
                        "publication_id": 428605,
                        "signature_id": "Wang_428605"
                    }, {
                        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
                        "author_name": "Lin, Shih-Yuin",
                        "publication_id": 428605,
                        "signature_id": "Lin_428605"
                    }],
                    "records": [{
                        "title": "".join(["Towards graphene-based detectors",
                                "for dark matter directional detection"]),
                        "year": 2015,
                        "publication_id": 1395222,
                        "authors": ["Wang, Shang-Yung"]
                    }, {
                        "title": "".join(["Induced Einstein-Kalb-Ramond",
                                          "theory and the black hole"]),
                        "year": 1996,
                        "publication_id": 428605,
                        "authors": [
                            "Kao, W.F.",
                            "Chyi, Tzuu-Kang",
                            "Dai, W.B.",
                            "Wang, Shang-Yung",
                            "Lin, Shih-Yuun"
                        ]
                    }]
                },
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


@blueprint.route('/clusters', methods=['POST'])
def make_clusters():
    clusters_data = request.get_json(silent=True)

    # Unpack the body of the POST request.
    try:
        records = clusters_data['records']
        signatures = clusters_data['signatures']
    except KeyError:
        # Missing data.
        abort(400)

    try:
        return jsonify(clustering(records, signatures))
    except IOError:  # pragma: no cover
        # Probably the file does not exist, ie. the model was not trained.
        abort(404)


@blueprint.route('/train', methods=['POST'])
def train_model():
    training_data = request.get_json(silent=True)

    # Unpack the body of the POST request.
    try:
        signatures = training_data['signatures']
        records = training_data['records']
        clusters = training_data['clusters']
    except KeyError:
        # Missing data.
        abort(400)

    try:
        learn_model(clusters, records, signatures)

        # Acknowledge successful training.
        return jsonify({"success": True})
    except:
        # Training of a new model has failed.
        abort(500)
