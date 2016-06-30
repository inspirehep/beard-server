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

"""Module tests."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from flask import Flask

from beard_server import beardserver


def test_version():
    """Test version import."""
    from beard_server import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = beardserver(app)
    assert 'beard-server' in app.extensions

    app = Flask('testapp')
    ext = beardserver()
    assert 'beard-server' not in app.extensions
    ext.init_app(app)
    assert 'beard-server' in app.extensions


def test_view(app):
    """Test view."""
    with app.test_client() as client:
        res = client.get("/")
        assert res.status_code == 200


def test_ping(app):
    """Test ping response."""
    with app.test_client() as client:
        res = client.get("/ping")
        assert res.data == "OK"
        assert res.status_code == 200
