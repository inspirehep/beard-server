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

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from .celery import app

from .modules.clustering.beard import predict as make_beard_clusters
from .modules.clustering.recid import make_recid_clusters
from .modules.clustering.resolver import solve_claims_conflict
from .modules.matching import match_clusters


@app.task
def make_clusters(records, signatures):
    """Make clusters and match them with the current state of database.

    This method allows for dispatching Celery tasks, that create
    two sets of clusters, one created by the signatures having the same
    recid and the second one using Beard library.

    After creating two types of clusters, the clusters are matched with
    each other, to link an output of Beard with the current state of the
    database. The further logic of resolving conflicts is not the subject
    of this module and is proceed by the client (invenio-beard).
    """

    # Create clusters using Beard.
    beard_clusters = make_beard_clusters(records, signatures)

    # Create clusters by author's recid.
    recid_clusters = make_recid_clusters(signatures)

    # Match Beard clusters with ones created by common recid.
    # Note that the method returns keys of the clusters.
    clusters_matched, clusters_created, _ = match_clusters(
        recid_clusters, beard_clusters)

    # Handle new clusters.
    clusters_with_no_profiles = {}

    if clusters_created:
        # Here each key represents independent integer (meaningless).
        clusters_with_no_profiles = {key: beard_clusters[key] for key in
                                     beard_clusters if key in clusters_created}

    # Handle matched clusters.
    clusters_with_profiles = {}

    if clusters_matched:
        for match in clusters_matched:
            # Here each key represents recid of an existing profile.
            recid_key, beard_key = match
            clusters_with_profiles[recid_key] = beard_clusters[beard_key]

    return (clusters_with_profiles, clusters_with_no_profiles)


@app.task
def solve_conflicts(claimed_signatures, not_claimed_signatures):
    """Solve conflicts by clustering not-claimed signatures with claimed ones.

    If Beard clusters at least two claimed signatures belonging to different
    authors, then all signatures from the same cluster are the subject to
    cluster one-by-one.

    The client (invenio-beard, check the docstrings from the method above)
    triggers this Celery task to assign each not-claimed signatures to one
    claimed signature.
    """
    return solve_claims_conflict(
        claimed_signatures, not_claimed_signatures)
