# Chunk: 9b8ba6f8bd4d_0

- source: `.venv-lab/Lib/site-packages/jupyterlab/tests/mock_packages/test-hyphens-underscore/index.js`
- lines: 1-18
- chunk: 1/1

```
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { ILauncher } from '@jupyterlab/launcher';

const plugin = {
  id: 'test-hyphens-underscore',
  requires: [ILauncher],
  autoStart: true,
  activate: function (application, launcher) {
    // eslint-disable-next-line no-console
    console.log('test-hyphens-underscore extension activated', launcher);
    window.commands = application.commands;
  }
};

export default plugin;
```
