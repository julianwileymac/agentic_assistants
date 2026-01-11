# Chunk: afcfc3aea01f_3

- source: `.venv-lab/Lib/site-packages/jsonschema/_keywords.py`
- lines: 244-339
- chunk: 4/6

```
_type(instance, "object"):
        return

    for property, dependency in dependentRequired.items():
        if property not in instance:
            continue

        for each in dependency:
            if each not in instance:
                message = f"{each!r} is a dependency of {property!r}"
                yield ValidationError(message)


def dependentSchemas(validator, dependentSchemas, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for property, dependency in dependentSchemas.items():
        if property not in instance:
            continue
        yield from validator.descend(
            instance, dependency, schema_path=property,
        )


def enum(validator, enums, instance, schema):
    if all(not equal(each, instance) for each in enums):
        yield ValidationError(f"{instance!r} is not one of {enums!r}")


def ref(validator, ref, instance, schema):
    yield from validator._validate_reference(ref=ref, instance=instance)


def dynamicRef(validator, dynamicRef, instance, schema):
    yield from validator._validate_reference(ref=dynamicRef, instance=instance)


def type(validator, types, instance, schema):
    types = ensure_list(types)

    if not any(validator.is_type(instance, type) for type in types):
        reprs = ", ".join(repr(type) for type in types)
        yield ValidationError(f"{instance!r} is not of type {reprs}")


def properties(validator, properties, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for property, subschema in properties.items():
        if property in instance:
            yield from validator.descend(
                instance[property],
                subschema,
                path=property,
                schema_path=property,
            )


def required(validator, required, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    for property in required:
        if property not in instance:
            yield ValidationError(f"{property!r} is a required property")


def minProperties(validator, mP, instance, schema):
    if validator.is_type(instance, "object") and len(instance) < mP:
        message = (
            "should be non-empty" if mP == 1
            else "does not have enough properties"
        )
        yield ValidationError(f"{instance!r} {message}")


def maxProperties(validator, mP, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    if validator.is_type(instance, "object") and len(instance) > mP:
        message = (
            "is expected to be empty" if mP == 0
            else "has too many properties"
        )
        yield ValidationError(f"{instance!r} {message}")


def allOf(validator, allOf, instance, schema):
    for index, subschema in enumerate(allOf):
        yield from validator.descend(instance, subschema, schema_path=index)


def anyOf(validator, anyOf, instance, schema):
    all_errors = []
```
