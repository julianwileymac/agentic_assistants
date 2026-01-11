# Chunk: 01ec2e9b3cac_1

- source: `.venv-lab/Lib/site-packages/json5/tool.py`
- lines: 102-199
- chunk: 2/2

```
[options] [FILE]\n'

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
        help=f'show JSON5 library version ({__version__})',
    )
    parser.add_argument(
        '-c',
        metavar='STR',
        dest='cmd',
        help='inline json5 string to read instead of reading from a file',
    )
    parser.add_argument(
        '--as-json',
        dest='as_json',
        action='store_const',
        const=True,
        default=False,
        help='output as JSON (same as --quote-keys --no-trailing-commas)',
    )
    parser.add_argument(
        '--indent',
        dest='indent',
        default=4,
        help='amount to indent each line (default is 4 spaces)',
    )
    parser.add_argument(
        '--quote-keys',
        action='store_true',
        default=False,
        help='quote all object keys',
    )
    parser.add_argument(
        '--no-quote-keys',
        action='store_false',
        dest='quote_keys',
        help="don't quote object keys that are identifiers"
        ' (this is the default)',
    )
    parser.add_argument(
        '--trailing-commas',
        action='store_true',
        default=True,
        help='add commas after the last item in multi-line '
        'objects and arrays (this is the default)',
    )
    parser.add_argument(
        '--no-trailing-commas',
        dest='trailing_commas',
        action='store_false',
        help='do not add commas after the last item in '
        'multi-line lists and objects',
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        default=True,
        help='Do not allow control characters (\\x00-\\x1f) in strings '
        '(default)',
    )
    parser.add_argument(
        '--no-strict',
        dest='strict',
        action='store_false',
        help='Allow control characters (\\x00-\\x1f) in strings',
    )
    parser.add_argument(
        '--quote-style',
        action='store',
        default='always_double',
        choices=QUOTE_STYLES.keys(),
        help='Controls how strings are encoded. By default they are always '
        'double-quoted ("always_double")',
    )
    parser.add_argument(
        'file',
        metavar='FILE',
        nargs='?',
        default='-',
        help='optional file to read JSON5 document from; if '
        'not specified or "-", will read from stdin '
        'instead',
    )
    return parser.parse_args(argv)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
```
