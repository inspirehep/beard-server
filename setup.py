# -*- coding: utf-8 -*-
#
# This file is part of Beard-server.
# Copyright (C) 2015 CERN.
#
# Beard-server is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Setup file for Beard-server."""

from setuptools import setup

setup(
    author="Invenio collaboration",
    author_email="admin@inspirehep.net",
    install_requires=[
        "flask",
        "flask-restful",
        "requests",
        "werkzeug"
    ],
    license="BSD",
    name="beard-server",
    packages=["beard-server"],
    platforms="any",
    version="0.0"
)
