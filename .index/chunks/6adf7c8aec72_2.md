# Chunk: 6adf7c8aec72_2

- source: `.venv-lab/Lib/site-packages/bs4/diagnose.py`
- lines: 191-269
- chunk: 3/3

```
i in range(length))


def rdoc(num_elements: int = 1000) -> str:
    """Randomly generate an invalid HTML document.

    :meta private:
    """
    tag_names = ["p", "div", "span", "i", "b", "script", "table"]
    elements = []
    for i in range(num_elements):
        choice = random.randint(0, 3)
        if choice == 0:
            # New tag.
            tag_name = random.choice(tag_names)
            elements.append("<%s>" % tag_name)
        elif choice == 1:
            elements.append(rsentence(random.randint(1, 4)))
        elif choice == 2:
            # Close a tag.
            tag_name = random.choice(tag_names)
            elements.append("</%s>" % tag_name)
    return "<html>" + "\n".join(elements) + "</html>"


def benchmark_parsers(num_elements: int = 100000) -> None:
    """Very basic head-to-head performance benchmark."""
    print(("Comparative parser benchmark on Beautiful Soup %s" % __version__))
    data = rdoc(num_elements)
    print(("Generated a large invalid HTML document (%d bytes)." % len(data)))

    for parser_name in ["lxml", ["lxml", "html"], "html5lib", "html.parser"]:
        success = False
        try:
            a = time.time()
            BeautifulSoup(data, parser_name)
            b = time.time()
            success = True
        except Exception:
            print(("%s could not parse the markup." % parser_name))
            traceback.print_exc()
        if success:
            print(("BS4+%s parsed the markup in %.2fs." % (parser_name, b - a)))

    from lxml import etree

    a = time.time()
    etree.HTML(data)
    b = time.time()
    print(("Raw lxml parsed the markup in %.2fs." % (b - a)))

    import html5lib

    parser = html5lib.HTMLParser()
    a = time.time()
    parser.parse(data)
    b = time.time()
    print(("Raw html5lib parsed the markup in %.2fs." % (b - a)))


def profile(num_elements: int = 100000, parser: str = "lxml") -> None:
    """Use Python's profiler on a randomly generated document."""
    filehandle = tempfile.NamedTemporaryFile()
    filename = filehandle.name

    data = rdoc(num_elements)
    vars = dict(bs4=bs4, data=data, parser=parser)
    cProfile.runctx("bs4.BeautifulSoup(data, parser)", vars, vars, filename)

    stats = pstats.Stats(filename)
    # stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats("_html5lib|bs4", 50)


# If this file is run as a script, standard input is diagnosed.
if __name__ == "__main__":
    diagnose(sys.stdin.read())
```
