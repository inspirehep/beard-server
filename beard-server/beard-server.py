# -*- coding: utf-8 -*-
#
# This file is part of Beard-server.
# Copyright (C) 2015 CERN.
#
# Beard-server is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Implementation of beard-server."""

import json
import os
import requests
import werkzeug

from beard_examples.applications.author_disambiguation import clustering
from beard_examples.applications.author_disambiguation import learn_model

from flask import Flask
from flask_restful import Api
from flask_restful import reqparse
from flask_restful import Resource

app = Flask(__name__)
api = Api(app)


distance_parser = reqparse.RequestParser()
distance_parser.add_argument('distance_pairs', required=True,
                             type=werkzeug.datastructures.FileStorage,
                             location='files')
distance_parser.add_argument('input_signatures', required=True,
                             type=werkzeug.datastructures.FileStorage,
                             location='files')
distance_parser.add_argument('input_records', required=True,
                             type=werkzeug.datastructures.FileStorage,
                             location='files')
distance_parser.add_argument('Callback', required=True, type=str,
                             location='headers')


class DistanceLearning(Resource):

    """Endpoint for learning the distance model."""

    # pass signatures, records and pairs
    def post(self):
        r"""CURL example.

        curl -i -F "distance_pairs=@1.json" -F "input_signatures=@2.json" \
                -F "input_records=@3.json" -H "Callback: aiopiopasdiop" \
                -H "Content-Type: multipart/form-data" \
                -X POST http://[server]/distancelearning

        After it creates a model, it will send it to the callback.

        Pass "null" as callback if you don't want to have the model returned.
        """
        args = distance_parser.parse_args()
        # Touch data directory
        if not os.path.exists('data'):
            os.makedirs('data')
        # Touch and erase model
        open('data/model.dat', 'w').close()

        # Save files
        pairs = args['distance_pairs']
        pairs.save('data/pairs.json')
        signatures = args['input_signatures']
        signatures.save('data/signatures.json')
        records = args['input_records']
        records.save('data/records.json')
        callback = args['Callback']

        del pairs
        del signatures
        del records
        del args
        learn_model('data/pairs.json', 'data/signatures.json',
                    'data/records.json', 'data/model.dat', verbose=3)

        if callback != "null":
            r = requests.post(callback, files={'model.dat':
                                               open('mode.dat', 'rb')})


clustering_parser = reqparse.RequestParser()
clustering_parser.add_argument('distance_model',
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('input_signatures',
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('input_records',
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('input_clusters',
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('Callback', required=True, type=str,
                               location='headers')
clustering_parser.add_argument("Clustering_method",
                               default="average", type=str, location='headers')
clustering_parser.add_argument("Clustering_threshold", default=None,
                               type=float, location='headers')
clustering_parser.add_argument("Clustering_test_size", default=None,
                               type=float, location='headers')
clustering_parser.add_argument("Clustering_random_state", default=42, type=int,
                               location="headers")
clustering_parser.add_argument("N_jobs", default=16, type=int,
                               location='headers')


class Clustering(Resource):

    """Endpoint for clustering."""

    def post(self):
        r"""CURL example.

        curl -i -F "input_signatures=@2.json" -F "input_records=@3.json" \
                -H "Callback: aiopiopasdiop" \
                -H "Clustering_random_state: 234" \
                -H "Content-Type: multipart/form-data" \
                -X POST http://[server]/clustering

        """
        args = clustering_parser.parse_args()
        print args
        if args['input_signatures']:
            signatures = args['input_signatures']
            signatures.save('data/signatures.json')
            del signatures
        if args['distance_model']:
            model = args['distance_model']
            model.save('data/model.dat')
            del model
        if args['input_records']:
            records = args['input_records']
            records.save('data/records.json')
            del records
        callback = args['Callback']
        method = args['Clustering_method']
        threshold = args['Clustering_threshold']
        test_size = args['Clustering_test_size']
        random_state = args['Clustering_random_state']
        n_jobs = args['N_jobs']

        del args

        clustering('data/signatures.json', 'data/records.json',
                   'data/model.dat', 'data/clusters.json', 'data/output.json',
                   3, n_jobs, method, random_state, test_size, threshold)

        r = requests.post(callback, files={'disambiguated.json':
                                           open('output.json', 'r')})


api.add_resource(DistanceLearning, '/distancelearning')
api.add_resource(Clustering, '/clustering')


if __name__ == '__main__':
    app.run(debug=True)
