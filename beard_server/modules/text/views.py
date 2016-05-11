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

from __future__ import (
    absolute_import,
    division,
    print_function)

from flask import (
    abort,
    Blueprint,
    jsonify,
    request)

import numpy as np

from beard.clustering import block_phonetic


blueprint = Blueprint(
    'beard_server_text',
    __name__,
    url_prefix='/api/text',
)


@blueprint.route('/', methods=['GET'])
def available_methods():
    """List of available methods to call as the part of API."""
    available = {
        "clusters": {
            "path": "/api/text/phonetic_block",
            "method": "[GET]",
            "example": {
                "request": "/api/text/phonetic_block?full_name=John%20Smith",
                "response": "SNATHj"
            }
        }
    }

    return jsonify(available)


@blueprint.route('/phonetic_block', methods=['GET'])
def get_phonetic_block():
    """Create phonetic block from a given full name using nysiis algorithm."""
    try:
        name = {'author_name': request.values.get('full_name', 0, type=str)}

        signature_block = block_phonetic(
            np.array([name], dtype=np.object).reshape(-1, 1),
            threshold=0,
            phonetic_algorithm='nysiis'
        )
    except IndexError:
        # Most likely a malformed author name.
        abort(420)
    except TypeError:
        # Missing full_name argument.
        abort(400)

    return jsonify(signature_block[0])
