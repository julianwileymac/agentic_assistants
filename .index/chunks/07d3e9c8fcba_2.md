# Chunk: 07d3e9c8fcba_2

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/parser.py`
- lines: 158-238
- chunk: 3/4

```
s its defaults by checking the
    configuration files and environmental variables"""

    def __init__(
        self,
        *args: Any,
        name: str,
        isolated: bool = False,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.config = Configuration(isolated)

        assert self.name
        super().__init__(*args, **kwargs)

    def check_default(self, option: optparse.Option, key: str, val: Any) -> Any:
        try:
            return option.check_value(key, val)
        except optparse.OptionValueError as exc:
            print(f"An error occurred during configuration: {exc}")
            sys.exit(3)

    def _get_ordered_configuration_items(
        self,
    ) -> Generator[tuple[str, Any], None, None]:
        # Configuration gives keys in an unordered manner. Order them.
        override_order = ["global", self.name, ":env:"]

        # Pool the options into different groups
        section_items: dict[str, list[tuple[str, Any]]] = {
            name: [] for name in override_order
        }

        for _, value in self.config.items():  # noqa: PERF102
            for section_key, val in value.items():
                # ignore empty values
                if not val:
                    logger.debug(
                        "Ignoring configuration key '%s' as its value is empty.",
                        section_key,
                    )
                    continue

                section, key = section_key.split(".", 1)
                if section in override_order:
                    section_items[section].append((key, val))

        # Yield each group in their override order
        for section in override_order:
            yield from section_items[section]

    def _update_defaults(self, defaults: dict[str, Any]) -> dict[str, Any]:
        """Updates the given defaults with values from the config files and
        the environ. Does a little special handling for certain types of
        options (lists)."""

        # Accumulate complex default state.
        self.values = optparse.Values(self.defaults)
        late_eval = set()
        # Then set the options with those values
        for key, val in self._get_ordered_configuration_items():
            # '--' because configuration supports only long names
            option = self.get_option("--" + key)

            # Ignore options not present in this parser. E.g. non-globals put
            # in [global] by users that want them to apply to all applicable
            # commands.
            if option is None:
                continue

            assert option.dest is not None

            if option.action in ("store_true", "store_false"):
                try:
                    val = strtobool(val)
                except ValueError:
                    self.error(
                        f"{val} is not a valid value for {key} option, "
                        "please specify a boolean value like yes/no, "
```
