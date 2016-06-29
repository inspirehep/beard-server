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
        res = client.get("/api/text/")
        data = json.loads(res.data)

        assert data['phonetic_blocks']
        assert res.status_code == 200


def test_missing_data(app):
    """Check if the API will return 400."""
    with app.test_client() as client:
        res = client.post(
            "/api/text/phonetic_blocks",
            data=str({}),
            headers={"Content-Type": "application/json"})

        assert res.status_code == 400


def test_working_phonetic_blocks(app):
    """Check if the API works."""
    full_names = ["John Smith", "John Doe", "Władysław II Jagiełło"]

    result = {
        'phonetic_blocks': {
            'John Doe': 'Dj',
            'John Smith': 'SNATHj',
            'Władysław II Jagiełło': 'JAGALw'
        }
    }

    with app.test_client() as client:
        res = client.post(
            "/api/text/phonetic_blocks",
            data=json.dumps({"full_names": full_names}),
            headers={"Content-Type": "application/json"})
        data = json.loads(res.data)

        assert data == result
        assert res.status_code == 200


def test_working_phonetic_blocks_with_error(app):
    """Check if the API works."""
    full_names = ["Władysław II Jagiełło",
                  {"Should not": "be there"}]

    result = {
        'phonetic_blocks': {
            'Władysław II Jagiełło': 'JAGALw'
        }
    }

    with app.test_client() as client:
        res = client.post(
            "/api/text/phonetic_blocks",
            data=json.dumps({"full_names": full_names}),
            headers={"Content-Type": "application/json"})
        data = json.loads(res.data)

        assert data == result
        assert res.status_code == 200
