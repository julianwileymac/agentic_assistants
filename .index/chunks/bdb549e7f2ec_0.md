# Chunk: bdb549e7f2ec_0

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_core_metadata.py`
- lines: 1-109
- chunk: 1/8

```
from __future__ import annotations

import functools
import importlib
import io
from email import message_from_string
from email.generator import Generator
from email.message import EmailMessage, Message
from email.parser import Parser
from email.policy import EmailPolicy
from inspect import cleandoc
from pathlib import Path
from unittest.mock import Mock

import jaraco.path
import pytest
from packaging.metadata import Metadata
from packaging.requirements import Requirement

from setuptools import _reqs, sic
from setuptools._core_metadata import rfc822_escape, rfc822_unescape
from setuptools.command.egg_info import egg_info, write_requirements
from setuptools.config import expand, setupcfg
from setuptools.dist import Distribution

from .config.downloads import retrieve_file, urls_from_file

EXAMPLE_BASE_INFO = dict(
    name="package",
    version="0.0.1",
    author="Foo Bar",
    author_email="foo@bar.net",
    long_description="Long\ndescription",
    description="Short description",
    keywords=["one", "two"],
)


@pytest.mark.parametrize(
    ("content", "result"),
    (
        pytest.param(
            "Just a single line",
            None,
            id="single_line",
        ),
        pytest.param(
            "Multiline\nText\nwithout\nextra indents\n",
            None,
            id="multiline",
        ),
        pytest.param(
            "Multiline\n    With\n\nadditional\n  indentation",
            None,
            id="multiline_with_indentation",
        ),
        pytest.param(
            "  Leading whitespace",
            "Leading whitespace",
            id="remove_leading_whitespace",
        ),
        pytest.param(
            "  Leading whitespace\nIn\n    Multiline comment",
            "Leading whitespace\nIn\n    Multiline comment",
            id="remove_leading_whitespace_multiline",
        ),
    ),
)
def test_rfc822_unescape(content, result):
    assert (result or content) == rfc822_unescape(rfc822_escape(content))


def __read_test_cases():
    base = EXAMPLE_BASE_INFO

    params = functools.partial(dict, base)

    return [
        ('Metadata version 1.0', params()),
        (
            'Metadata Version 1.0: Short long description',
            params(
                long_description='Short long description',
            ),
        ),
        (
            'Metadata version 1.1: Classifiers',
            params(
                classifiers=[
                    'Programming Language :: Python :: 3',
                    'Programming Language :: Python :: 3.7',
                    'License :: OSI Approved :: MIT License',
                ],
            ),
        ),
        (
            'Metadata version 1.1: Download URL',
            params(
                download_url='https://example.com',
            ),
        ),
        (
            'Metadata Version 1.2: Requires-Python',
            params(
                python_requires='>=3.7',
            ),
        ),
        pytest.param(
```
