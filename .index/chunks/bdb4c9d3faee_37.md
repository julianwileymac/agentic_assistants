# Chunk: bdb4c9d3faee_37

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 2959-3043
- chunk: 38/47

```
other

    # These properties have to be lazy so that we don't have to load any
    # metadata until/unless it's actually needed.  (i.e., some distributions
    # may not know their name or version without loading PKG-INFO)

    @property
    def key(self):
        try:
            return self._key
        except AttributeError:
            self._key = key = self.project_name.lower()
            return key

    @property
    def parsed_version(self):
        if not hasattr(self, "_parsed_version"):
            try:
                self._parsed_version = parse_version(self.version)
            except _packaging_version.InvalidVersion as ex:
                info = f"(package: {self.project_name})"
                if hasattr(ex, "add_note"):
                    ex.add_note(info)  # PEP 678
                    raise
                raise _packaging_version.InvalidVersion(f"{str(ex)} {info}") from None

        return self._parsed_version

    @property
    def _forgiving_parsed_version(self):
        try:
            return self.parsed_version
        except _packaging_version.InvalidVersion as ex:
            self._parsed_version = parse_version(_forgiving_version(self.version))

            notes = "\n".join(getattr(ex, "__notes__", []))  # PEP 678
            msg = f"""!!\n\n
            *************************************************************************
            {str(ex)}\n{notes}

            This is a long overdue deprecation.
            For the time being, `pkg_resources` will use `{self._parsed_version}`
            as a replacement to avoid breaking existing environments,
            but no future compatibility is guaranteed.

            If you maintain package {self.project_name} you should implement
            the relevant changes to adequate the project to PEP 440 immediately.
            *************************************************************************
            \n\n!!
            """
            warnings.warn(msg, DeprecationWarning)

            return self._parsed_version

    @property
    def version(self):
        try:
            return self._version
        except AttributeError as e:
            version = self._get_version()
            if version is None:
                path = self._get_metadata_path_for_display(self.PKG_INFO)
                msg = ("Missing 'Version:' header and/or {} file at path: {}").format(
                    self.PKG_INFO, path
                )
                raise ValueError(msg, self) from e

            return version

    @property
    def _dep_map(self):
        """
        A map of extra to its list of (direct) requirements
        for this distribution, including the null extra.
        """
        try:
            return self.__dep_map
        except AttributeError:
            self.__dep_map = self._filter_extras(self._build_dep_map())
        return self.__dep_map

    @staticmethod
    def _filter_extras(dm: dict[str | None, list[Requirement]]):
        """
```
