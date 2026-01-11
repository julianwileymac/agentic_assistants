# Chunk: befe5c6ecdcf_10

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 698-785
- chunk: 11/12

```
      if build_dir is None:
            return

        create_archive = True
        archive_name = "{}-{}.zip".format(self.name, self.metadata["version"])
        archive_path = os.path.join(build_dir, archive_name)

        if os.path.exists(archive_path):
            response = ask_path_exists(
                f"The file {display_path(archive_path)} exists. (i)gnore, (w)ipe, "
                "(b)ackup, (a)bort ",
                ("i", "w", "b", "a"),
            )
            if response == "i":
                create_archive = False
            elif response == "w":
                logger.warning("Deleting %s", display_path(archive_path))
                os.remove(archive_path)
            elif response == "b":
                dest_file = backup_dir(archive_path)
                logger.warning(
                    "Backing up %s to %s",
                    display_path(archive_path),
                    display_path(dest_file),
                )
                shutil.move(archive_path, dest_file)
            elif response == "a":
                sys.exit(-1)

        if not create_archive:
            return

        zip_output = zipfile.ZipFile(
            archive_path,
            "w",
            zipfile.ZIP_DEFLATED,
            allowZip64=True,
        )
        with zip_output:
            dir = os.path.normcase(os.path.abspath(self.unpacked_source_directory))
            for dirpath, dirnames, filenames in os.walk(dir):
                for dirname in dirnames:
                    dir_arcname = self._get_archive_name(
                        dirname,
                        parentdir=dirpath,
                        rootdir=dir,
                    )
                    zipdir = zipfile.ZipInfo(dir_arcname + "/")
                    zipdir.external_attr = 0x1ED << 16  # 0o755
                    zip_output.writestr(zipdir, "")
                for filename in filenames:
                    file_arcname = self._get_archive_name(
                        filename,
                        parentdir=dirpath,
                        rootdir=dir,
                    )
                    filename = os.path.join(dirpath, filename)
                    zip_output.write(filename, file_arcname)

        logger.info("Saved %s", display_path(archive_path))

    def install(
        self,
        root: str | None = None,
        home: str | None = None,
        prefix: str | None = None,
        warn_script_location: bool = True,
        use_user_site: bool = False,
        pycompile: bool = True,
    ) -> None:
        assert self.req is not None
        scheme = get_scheme(
            self.req.name,
            user=use_user_site,
            home=home,
            root=root,
            isolated=self.isolated,
            prefix=prefix,
        )

        assert self.is_wheel
        assert self.local_file_path

        install_wheel(
            self.req.name,
            self.local_file_path,
            scheme=scheme,
```
