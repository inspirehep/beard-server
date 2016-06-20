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

"""Beard as RESTful API and Celery service."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from beard_server import config

from .modules import blueprints
from .views import blueprint


class beardserver(object):
    """beard-server extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        # Register views.py blueprint.
        app.register_blueprint(blueprint)

        # Register blueprints from available modules.
        for module in blueprints:
            app.register_blueprint(module)

        app.extensions['beard-server'] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.from_object(config)
