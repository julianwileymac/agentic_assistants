# Chunk: dad5aec113d6_5

- source: `.venv-lab/Lib/site-packages/jsonschema/_legacy_keywords.py`
- lines: 404-450
- chunk: 6/6

```
validator.evolve(schema=schema["if"]).is_valid(instance):
            evaluated_keys += find_evaluated_property_keys_by_schema(
                validator, instance, schema["if"],
            )
            if "then" in schema:
                evaluated_keys += find_evaluated_property_keys_by_schema(
                    validator, instance, schema["then"],
                )
        elif "else" in schema:
            evaluated_keys += find_evaluated_property_keys_by_schema(
                validator, instance, schema["else"],
            )

    return evaluated_keys


def unevaluatedProperties_draft2019(validator, uP, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    evaluated_keys = find_evaluated_property_keys_by_schema(
        validator, instance, schema,
    )
    unevaluated_keys = []
    for property in instance:
        if property not in evaluated_keys:
            for _ in validator.descend(
                instance[property],
                uP,
                path=property,
                schema_path=property,
            ):
                # FIXME: Include context for each unevaluated property
                #        indicating why it's invalid under the subschema.
                unevaluated_keys.append(property)  # noqa: PERF401

    if unevaluated_keys:
        if uP is False:
            error = "Unevaluated properties are not allowed (%s %s unexpected)"
            extras = sorted(unevaluated_keys, key=str)
            yield ValidationError(error % _utils.extras_msg(extras))
        else:
            error = (
                "Unevaluated properties are not valid under "
                "the given schema (%s %s unevaluated and invalid)"
            )
            yield ValidationError(error % _utils.extras_msg(unevaluated_keys))
```
