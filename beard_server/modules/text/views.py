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

"""Phonetic blocks endpoint."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from flask import abort, Blueprint, jsonify, request

from .utils import phonetic_blocks

blueprint = Blueprint(
    'beard_server_text',
    __name__,
    url_prefix='/api/text',
)


@blueprint.route('/', methods=['GET'])
def available_methods():
    """List of available methods to call as the part of API."""
    available = {
        "phonetic_blocks": {
            "path": "/api/text/phonetic_blocks",
            "method": "[POST]",
            "example": {
                "body": {
                    "full_names": [
                        "John Smith"
                    ]
                },
                "header": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "response": {
                    "phonetic_blocks": {
                        "John Smith": "SNATHj"
                    }
                }
            }
        }
    }

    return jsonify(available)


@blueprint.route('/phonetic_blocks', methods=['POST'])
def get_phonetic_blocks():
    """Create phonetic block from a given full name using nysiis algorithm."""
    full_names_data = request.get_json(silent=True)

    # Unpack the body of the POST request.
    try:
        full_names = full_names_data['full_names']
    except KeyError:
        # Missing data.
        abort(400)

    try:
        response = phonetic_blocks(full_names)
    except TypeError:
        # Malformed author's name.
        full_names_trimmed = []

        for full_name in full_names:
            try:
                # For the time being of Python 2.
                # Most probably a given name cannot be converted to unicode.
                if not isinstance(full_name, unicode):
                    unicode(full_name, 'utf8')
            except TypeError:
                continue

            # Create a subset of valid full names.
            full_names_trimmed.append(full_name)

        response = phonetic_blocks(full_names_trimmed)

    return jsonify({"phonetic_blocks": response})
