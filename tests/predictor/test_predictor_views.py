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

"""Test Jinja views."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json


def test_available_methods(app):
    """Check if the documentation is available."""
    with app.test_client() as client:
        res = client.get("/api/predictor/")
        data = json.loads(res.data)

        assert data['coreness']
        assert data['train']
        assert res.status_code == 200


def test_missing_data(app):
    """Check if the API will return 400."""
    with app.test_client() as client:
        res = client.post(
            "/api/predictor/coreness",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"})

        assert res.status_code == 400


def test_working_predictor(app):
    """Check if the API works."""
    abstract = "".join([
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
        "type of transient unrelated to YSOs."
    ])
    categories = ["astro-ph"]
    title = "".join(["Discovery of a Long-Lived, High",
                     "Amplitude Dusty Infrared Transient"])

    result = {
        'decision': 'Non-CORE',
        'scores': [
            -1.2784773680678039,
            1.360770696211779,
            -3.0140990443900573
        ]
    }

    with app.test_client() as client:
        res = client.post(
            "/api/predictor/coreness",
            data=json.dumps(
                {"abstract": abstract, "categories": categories,
                 "title": title}),
            headers={"Content-Type": "application/json"})
        data = json.loads(res.data)

        assert data == result
        assert res.status_code == 200


def test_working_predictor_top_words(app):
    """Check if the API works including top words."""
    abstract = "".join([
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
        "type of transient unrelated to YSOs."
    ])
    categories = ["astro-ph"]
    title = "".join(["Discovery of a Long-Lived, High",
                     "Amplitude Dusty Infrared Transient"])

    result = {
        'decision': 'Non-CORE',
        'scores': [
            -1.2784773680678039,
            1.360770696211779,
            -3.0140990443900573
        ]
    }

    with app.test_client() as client:
        res = client.post(
            "/api/predictor/coreness",
            data=json.dumps(
                {"abstract": abstract, "categories": categories,
                 "title": title}),
            headers={"Content-Type": "application/json"})
        data = json.loads(res.data)

        assert data == result
        assert res.status_code == 200
