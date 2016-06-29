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

"""Celery and Jinja instances configuration."""

# Celery.
BROKER_URL = "amqp://"
CELERY_RESULT_BACKEND = "amqp://"

CELERY_IMPORTS = ("beard_server.tasks",)
CELERY_TASK_SERIALIZER = "msgpack"
CELERY_RESULT_SERIALIZER = "msgpack"

CELERY_ROUTES = {
    "beard_server.tasks.make_clusters": {
        "queue": "beard"
    },
    "beard_server.tasks.solve_conflicts": {
        "queue:": "beard"
    }
}

# Jinja.
BEARD_SERVER_BASE_TEMPLATE = "base.html"
JSON_AS_ASCII = False
