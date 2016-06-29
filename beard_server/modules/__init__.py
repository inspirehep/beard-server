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

"""Collection of all blueprints from available modules."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from .clustering import blueprints as clustering_blueprints
from .predictor import blueprints as predictor_blueprints
from .text import blueprints as text_blueprints

# Register blueprints of modules.
blueprints = []
blueprints.extend(clustering_blueprints)
blueprints.extend(predictor_blueprints)
blueprints.extend(text_blueprints)

__all__ = ['blueprints']
