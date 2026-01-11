# Chunk: 8bbe9fa7b94d_1

- source: `.venv-lab/Lib/site-packages/decorator-5.2.1.dist-info/METADATA`
- lines: 84-125
- chunk: 2/2

```
can get a PDF version by simply using the print
functionality of your browser.

Here is the documentation for previous versions of the module:

https://github.com/micheles/decorator/blob/4.3.2/docs/tests.documentation.rst
https://github.com/micheles/decorator/blob/4.2.1/docs/tests.documentation.rst
https://github.com/micheles/decorator/blob/4.1.2/docs/tests.documentation.rst
https://github.com/micheles/decorator/blob/4.0.0/documentation.rst
https://github.com/micheles/decorator/blob/3.4.2/documentation.rst

For the impatient
-----------------

Here is an example of how to define a family of decorators tracing slow
operations:

.. code-block:: python

   from decorator import decorator

   @decorator
   def warn_slow(func, timelimit=60, *args, **kw):
       t0 = time.time()
       result = func(*args, **kw)
       dt = time.time() - t0
       if dt > timelimit:
           logging.warning('%s took %d seconds', func.__name__, dt)
       else:
           logging.info('%s took %d seconds', func.__name__, dt)
       return result

   @warn_slow  # warn if it takes more than 1 minute
   def preprocess_input_files(inputdir, tempdir):
       ...

   @warn_slow(timelimit=600)  # warn if it takes more than 10 minutes
   def run_calculation(tempdir, outdir):
       ...

Enjoy!
```
