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

from collections import defaultdict


def make_recid_clusters(signatures, claimed_only=False):
    """Group the signatures by author's recid.

    If the author has a profile recid, then all the signatures belonging
    to the same profile will be clustered into a dictionary with a key
    of the recid and signatures (uuids) as a list.

    :param signatures:
        A list of signatures containing uuid and author_recid if possible.

        Example:
            signatures =
                [{'author_affiliation': u'MIT, Cambridge, CTP',
                  'author_name': u'Wang, Yi-Nan',
                  'publication_id': u'13c3cca8-b0bf-42f5-90d4-e3dfcced0511',
                  'signature_id': u'a4156520-560d-4248-a57f-949c361e0dd0',
                  'author_recid': u'10123',
                  'author_claimed: False}]

    :return:
        A dictionary of clustered signatures with a key as recid
        and signatures as a list.

        Example:
            {"10123": ["a4156520-560d-4248-a57f-949c361e0dd0]}
    """
    signatures_by_recid = defaultdict(list)

    for signature in signatures:
        try:
            if claimed_only:
                if signature.get('author_claimed', False) and \
                        signature['signature_id']:
                    signatures_by_recid[signature['author_recid']].append(
                        signature['signature_id'])
            else:
                if signature['signature_id']:
                    signatures_by_recid[signature['author_recid']].append(
                        signature['signature_id'])
        except KeyError:
            # In case of missing 'author_recid'.
            pass

    result = dict(signatures_by_recid)

    # Remove all signatures, with no profile recid,
    # ie. with 'False' key.
    result.pop(False, None)

    return result
