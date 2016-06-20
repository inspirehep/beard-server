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

"""Tool for generating phonetic blocks."""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import numpy as np

from beard.clustering import block_phonetic


def phonetic_blocks(full_names, phonetic_algorithm='nysiis'):
    """Create a dictionary of phonetic blocks for a given list of names."""

    # The method requires a list of dictionaries with full_name as keys.
    full_names_formatted = [
        {"author_name": i} for i in full_names]

    # Create a list of phonetic blocks.
    phonetic_blocks = list(
        block_phonetic(np.array(
            full_names_formatted,
            dtype=np.object).reshape(-1, 1),
            threshold=0,
            phonetic_algorithm=phonetic_algorithm
        )
    )

    return dict(zip(full_names, phonetic_blocks))
