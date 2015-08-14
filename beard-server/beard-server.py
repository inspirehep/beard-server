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
import multiprocessing as mp
import os
import requests
import werkzeug

from beard_examples.applications.author_disambiguation import clustering
from beard_examples.applications.author_disambiguation import learn_model
from beard_examples.applications.author_disambiguation import pair_sampling

from flask import Flask
from flask_restful import Api
from flask_restful import reqparse
from flask_restful import Resource

app = Flask(__name__)
api = Api(app)

DATA_PATH = "data/"
MODELS_PATH = "models/"

app.config.from_object(__name__)
app.config.from_envvar('BEARDSERVER_SETTINGS', silent=True)

distance_parser = reqparse.RequestParser()
distance_parser.add_argument('input_signatures', required=True,
                             type=werkzeug.datastructures.FileStorage,
                             location='files')
distance_parser.add_argument('input_records', required=True,
                             type=werkzeug.datastructures.FileStorage,
                             location='files')
distance_parser.add_argument('input_clusters', required=True,
                             type=werkzeug.datastructures.FileStorage,
                             location='files')
distance_parser.add_argument('Callback', required=True, type=str,
                             location='headers')
distance_parser.add_argument('Model_Name', default="model", type=str,
                             location='headers')


def _distance_learning(callback, ethnicity_estimator, model_name):
    pairs = pair_sampling(clusters_filename=app.config["DATA_PATH"] +
                          "/clusters.json", verbose=0,
                          train_filename=app.config["DATA_PATH"] +
                          "/signatures.json")

    json.dump(pairs, open(app.config["DATA_PATH"] + '/pairs.json', "w"))

    learn_model(app.config["DATA_PATH"] + '/pairs.json',
                app.config["DATA_PATH"] + '/signatures.json',
                app.config["DATA_PATH"] + '/records.json',
                app.config["MODELS_PATH"] + model_name,
                ethnicity_estimator=ethnicity_estimator)

    r = requests.post(callback)


class DistanceLearning(Resource):

    """Endpoint for learning the distance model.

    Firstly, it samples the pairs.
    """

    # pass signatures, records and pairs
    def post(self):
        r"""CURL example.

        curl -i -F "input_signatures=@2.json" \
                -F "input_clusters=@4.json" \
                -F "input_records=@3.json" -H "Callback: [sendhere]" \
                -H "Content-Type: multipart/form-data"  \
                -H "Model-Name: [name]" \
                -X POST [server]/distancelearning

        After it creates a model, it will send a notification to the callback.
        """
        args = distance_parser.parse_args()
        # Touch data directory
        if not os.path.exists(app.config['DATA_PATH']):
            os.makedirs(app.config['DATA_PATH'])
        if not os.path.exists(app.config['MODELS_PATH']):
            os.makedirs(app.config['MODELS_PATH'])

        # Touch and erase model
        model_name = args['Model_Name']
        open(app.config["MODELS_PATH"] + model_name, 'w').close()

        signatures = args['input_signatures']
        signatures.save(app.config["DATA_PATH"] + '/signatures.json')
        del signatures

        records = args['input_records']
        records.save(app.config["DATA_PATH"] + '/records.json')
        del records

        clusters = args['input_clusters']
        clusters.save(app.config["DATA_PATH"] + '/clusters.json')
        del clusters

        callback = args['Callback']

        del args

        # Add ethnicity estimator, if present
        ethnicity_estimator_path = app.config["DATA_PATH"] + \
            '/ethnicity_estimator.pickle'
        if os.path.isfile(ethnicity_estimator_path):
            ethnicity_estimator = ethnicity_estimator_path
        else:
            ethnicity_estimator = None

        p = mp.Process(target=_distance_learning, args=(callback,
                                                        ethnicity_estimator,
                                                        model_name))
        p.start()

        return '', 202


clustering_parser = reqparse.RequestParser()
clustering_parser.add_argument('distance_model',
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('input_signatures',
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('train_signatures',
                               type=werkzeug.datastructures.FileStorage,
                               default=None,
                               location='files')
clustering_parser.add_argument('input_records',
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('input_clusters', required=True,
                               type=werkzeug.datastructures.FileStorage,
                               location='files')
clustering_parser.add_argument('Callback', required=True, type=str,
                               location='headers')
clustering_parser.add_argument("Clustering_method",
                               default="average", type=str, location='headers')
clustering_parser.add_argument("Clustering_threshold", default=None,
                               type=float, location='headers')
clustering_parser.add_argument("N_jobs", default=16, type=int,
                               location='headers')
clustering_parser.add_argument('Model_Name', default="model", type=str,
                               location='headers')


def _clustering(n_jobs, method, train_signatures, threshold, model_name):

    clustering(app.config["DATA_PATH"] + '/signatures.json',
               app.config["DATA_PATH"] + '/records.json',
               app.config["MODELS_PATH"] + model_name,
               app.config["DATA_PATH"] + '/clusters.json',
               app.config["DATA_PATH"] + '/output.json',
               0, n_jobs, method, train_signatures, threshold)

    requests.post(callback, files={'disambiguated.json':
                                   open('output.json', 'r')})


class Clustering(Resource):

    """Endpoint for clustering."""

    def post(self):
        r"""CURL example.

        curl -i -F "input_signatures=@2.json" -F "input_records=@3.json" \
                -F "train_signatures=@4.json" -F "input_clusters=@4.json" \
                -H "Callback: aiopiopasdiop" \
                -H "Content-Type: multipart/form-data" \
                -H "Model_Name: [name]" \
                -X POST http://[server]/clustering

        """
        args = clustering_parser.parse_args()
        signatures = args['input_signatures']
        signatures.save(app.config["DATA_PATH"] + '/signatures.json')
        del signatures

        train_signatures = args['train_signatures']
        if train_signatures:
            train_signatures.save(app.config["DATA_PATH"] +
                                  'train_signatures.json')
            train_signatures = app.config["DATA_PATH"] + '/train_signatures'

        records = args['input_records']
        records.save(app.config["DATA_PATH"] + '/records.json')
        del records

        clusters = args['input_clusters']
        clusters.save(app.config["DATA_PATH"] + '/clusters.json')
        del clusters

        callback = args['Callback']
        method = args['Clustering_method']
        threshold = args['Clustering_threshold']
        model_name = args['Model_Name']
        n_jobs = args['N_jobs']

        del args

        p = mp.Process(target=_clustering, args=(n_jobs, method,
                                                 train_signatures,
                                                 threshold,
                                                 model_name))

        p.start()

        return '', 202

api.add_resource(DistanceLearning, '/distancelearning')
api.add_resource(Clustering, '/clustering')


if __name__ == '__main__':
    app.run(debug=True)
