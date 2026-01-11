# Chunk: 7baed29eb50c_5

- source: `.venv-lab/Lib/site-packages/colorama-0.4.6.dist-info/METADATA`
- lines: 351-427
- chunk: 6/7

```
ta background

All other ANSI sequences of the form ``ESC [ <param> ; <param> ... <command>``
are silently stripped from the output on Windows.

Any other form of ANSI sequence, such as single-character codes or alternative
initial characters, are not recognised or stripped. It would be cool to add
them though. Let me know if it would be useful for you, via the Issues on
GitHub.

Status & Known Problems
-----------------------

I've personally only tested it on Windows XP (CMD, Console2), Ubuntu
(gnome-terminal, xterm), and OS X.

Some valid ANSI sequences aren't recognised.

If you're hacking on the code, see `README-hacking.md`_. ESPECIALLY, see the
explanation there of why we do not want PRs that allow Colorama to generate new
types of ANSI codes.

See outstanding issues and wish-list:
https://github.com/tartley/colorama/issues

If anything doesn't work for you, or doesn't do what you expected or hoped for,
I'd love to hear about it on that issues list, would be delighted by patches,
and would be happy to grant commit access to anyone who submits a working patch
or two.

.. _README-hacking.md: README-hacking.md

License
-------

Copyright Jonathan Hartley & Arnon Yaari, 2013-2020. BSD 3-Clause license; see
LICENSE file.

Professional support
--------------------

.. |tideliftlogo| image:: https://cdn2.hubspot.net/hubfs/4008838/website/logos/logos_for_download/Tidelift_primary-shorthand-logo.png
   :alt: Tidelift
   :target: https://tidelift.com/subscription/pkg/pypi-colorama?utm_source=pypi-colorama&utm_medium=referral&utm_campaign=readme

.. list-table::
   :widths: 10 100

   * - |tideliftlogo|
     - Professional support for colorama is available as part of the
       `Tidelift Subscription`_.
       Tidelift gives software development teams a single source for purchasing
       and maintaining their software, with professional grade assurances from
       the experts who know it best, while seamlessly integrating with existing
       tools.

.. _Tidelift Subscription: https://tidelift.com/subscription/pkg/pypi-colorama?utm_source=pypi-colorama&utm_medium=referral&utm_campaign=readme

Thanks
------

See the CHANGELOG for more thanks!

* Marc Schlaich (schlamar) for a ``setup.py`` fix for Python2.5.
* Marc Abramowitz, reported & fixed a crash on exit with closed ``stdout``,
  providing a solution to issue #7's setuptools/distutils debate,
  and other fixes.
* User 'eryksun', for guidance on correctly instantiating ``ctypes.windll``.
* Matthew McCormick for politely pointing out a longstanding crash on non-Win.
* Ben Hoyt, for a magnificent fix under 64-bit Windows.
* Jesse at Empty Square for submitting a fix for examples in the README.
* User 'jamessp', an observant documentation fix for cursor positioning.
* User 'vaal1239', Dave Mckee & Lackner Kristof for a tiny but much-needed Win7
  fix.
* Julien Stuyck, for wisely suggesting Python3 compatible updates to README.
* Daniel Griffith for multiple fabulous patches.
```
