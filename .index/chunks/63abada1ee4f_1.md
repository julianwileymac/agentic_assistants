# Chunk: 63abada1ee4f_1

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_namespaces.py`
- lines: 85-139
- chunk: 2/2

```
myns.pkgA')
        target = tmpdir / 'packages'
        # use pip to install to the target directory
        install_cmd = [
            sys.executable,
            '-m',
            'pip.__main__',
            'install',
            str(pkg_A),
            '-t',
            str(target),
        ]
        subprocess.check_call(install_cmd)
        namespaces.make_site_dir(target)

        # ensure that package imports and pkg_resources imports
        pkg_resources_imp = [
            sys.executable,
            '-c',
            'import pkg_resources; import myns.pkgA',
        ]
        with paths_on_pythonpath([str(target)]):
            subprocess.check_call(pkg_resources_imp, cwd=str(pkg_A))

    def test_packages_in_the_same_namespace_installed_and_cwd(self, tmpdir):
        """
        Installing one namespace package and also have another in the same
        namespace in the current working directory, both of them must be
        importable.
        """
        pkg_A = namespaces.build_namespace_package(tmpdir, 'myns.pkgA')
        pkg_B = namespaces.build_namespace_package(tmpdir, 'myns.pkgB')
        target = tmpdir / 'packages'
        # use pip to install to the target directory
        install_cmd = [
            sys.executable,
            '-m',
            'pip.__main__',
            'install',
            str(pkg_A),
            '-t',
            str(target),
        ]
        subprocess.check_call(install_cmd)
        namespaces.make_site_dir(target)

        # ensure that all packages import and pkg_resources imports
        pkg_resources_imp = [
            sys.executable,
            '-c',
            'import pkg_resources; import myns.pkgA; import myns.pkgB',
        ]
        with paths_on_pythonpath([str(target)]):
            subprocess.check_call(pkg_resources_imp, cwd=str(pkg_B))
```
