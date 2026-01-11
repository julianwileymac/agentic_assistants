# Chunk: 01ec2e9b3cac_0

- source: `.venv-lab/Lib/site-packages/json5/tool.py`
- lines: 1-115
- chunk: 1/2

```
# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A tool to parse and pretty-print JSON5.

Usage:

    $ echo '{foo:"bar"}' | python -m json5
    {
        foo: 'bar',
    }
    $ echo '{foo:"bar"}' | python -m json5 --as-json
    {
        "foo": "bar"
    }
"""

import argparse
import sys

import json5
from json5.host import Host
from json5.version import __version__

QUOTE_STYLES = {q.value: q for q in json5.QuoteStyle}


def main(argv=None, host=None):
    host = host or Host()

    args = _parse_args(host, argv)

    if args.version:
        host.print(__version__)
        return 0

    if args.cmd:
        inp = args.cmd
    elif args.file == '-':
        inp = host.stdin.read()
    else:
        inp = host.read_text_file(args.file)

    if args.indent == 'None':
        args.indent = None
    else:
        try:
            args.indent = int(args.indent)
        except ValueError:
            pass

    if args.as_json:
        args.quote_keys = True
        args.trailing_commas = False
        args.quote_style = json5.QuoteStyle.ALWAYS_DOUBLE.value

    obj = json5.loads(inp, strict=args.strict)
    s = json5.dumps(
        obj,
        indent=args.indent,
        quote_keys=args.quote_keys,
        trailing_commas=args.trailing_commas,
        quote_style=QUOTE_STYLES[args.quote_style],
    )
    host.print(s)
    return 0


class _HostedArgumentParser(argparse.ArgumentParser):
    """An argument parser that plays nicely w/ host objects."""

    def __init__(self, host, **kwargs):
        self.host = host
        super().__init__(**kwargs)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, self.host.stderr)
        sys.exit(status)

    def error(self, message):
        self.host.print(f'usage: {self.usage}', end='', file=self.host.stderr)
        self.host.print('    -h/--help for help\n', file=self.host.stderr)
        self.exit(2, f'error: {message}\n')

    def print_help(self, file=None):
        self.host.print(self.format_help(), file=file)


def _parse_args(host, argv):
    usage = 'json5 [options] [FILE]\n'

    parser = _HostedArgumentParser(
        host,
        prog='json5',
        usage=usage,
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-V',
        '--version',
        action='store_true',
```
