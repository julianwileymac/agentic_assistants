# Chunk: afcfc3aea01f_2

- source: `.venv-lab/Lib/site-packages/jsonschema/_keywords.py`
- lines: 174-254
- chunk: 3/6

```
ient) != quotient
        except OverflowError:
            # When `instance` is large and `dB` is less than one,
            # quotient can overflow to infinity; and then casting to int
            # raises an error.
            #
            # In this case we fall back to Fraction logic, which is
            # exact and cannot overflow.  The performance is also
            # acceptable: we try the fast all-float option first, and
            # we know that fraction(dB) can have at most a few hundred
            # digits in each part.  The worst-case slowdown is therefore
            # for already-slow enormous integers or Decimals.
            failed = (Fraction(instance) / Fraction(dB)).denominator != 1
    else:
        failed = instance % dB

    if failed:
        yield ValidationError(f"{instance!r} is not a multiple of {dB}")


def minItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) < mI:
        message = "should be non-empty" if mI == 1 else "is too short"
        yield ValidationError(f"{instance!r} {message}")


def maxItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) > mI:
        message = "is expected to be empty" if mI == 0 else "is too long"
        yield ValidationError(f"{instance!r} {message}")


def uniqueItems(validator, uI, instance, schema):
    if (
        uI
        and validator.is_type(instance, "array")
        and not uniq(instance)
    ):
        yield ValidationError(f"{instance!r} has non-unique elements")


def pattern(validator, patrn, instance, schema):
    if (
        validator.is_type(instance, "string")
        and not re.search(patrn, instance)
    ):
        yield ValidationError(f"{instance!r} does not match {patrn!r}")


def format(validator, format, instance, schema):
    if validator.format_checker is not None:
        try:
            validator.format_checker.check(instance, format)
        except FormatError as error:
            yield ValidationError(error.message, cause=error.cause)


def minLength(validator, mL, instance, schema):
    if validator.is_type(instance, "string") and len(instance) < mL:
        message = "should be non-empty" if mL == 1 else "is too short"
        yield ValidationError(f"{instance!r} {message}")


def maxLength(validator, mL, instance, schema):
    if validator.is_type(instance, "string") and len(instance) > mL:
        message = "is expected to be empty" if mL == 0 else "is too long"
        yield ValidationError(f"{instance!r} {message}")


def dependentRequired(validator, dependentRequired, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for property, dependency in dependentRequired.items():
        if property not in instance:
            continue

        for each in dependency:
            if each not in instance:
                message = f"{each!r} is a dependency of {property!r}"
```
