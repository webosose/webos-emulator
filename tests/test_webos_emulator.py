#!/usr/bin/env python

"""
  Copyright (c) 2022 LG Electronics Inc.
  SPDX-License-Identifier: MIT
"""

"""Tests for `webos-emulator` package."""

import pytest


from webos_emulator import webos_emulator


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
