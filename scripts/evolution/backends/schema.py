from __future__ import annotations

from typing import Any


def validate_json(value: Any, schema: dict[str, Any], path: str = "$", errors: list[str] | None = None) -> list[str]:
    errors = errors if errors is not None else []
    expected = schema.get("type")
    type_checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if isinstance(expected, list):
        if not any(candidate in type_checks and type_checks[candidate](value) for candidate in expected):
            errors.append(f"{path}: expected one of {', '.join(map(str, expected))}")
            return errors
    elif expected in type_checks and not type_checks[expected](value):
        errors.append(f"{path}: expected {expected}")
        return errors
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is not in the allowed enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than minLength")
        if len(value) > schema.get("maxLength", float("inf")):
            errors.append(f"{path}: string exceeds maxLength")
    if isinstance(value, (int, float)):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: value exceeds maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has too few items")
        if len(value) > schema.get("maxItems", float("inf")):
            errors.append(f"{path}: array has too many items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_json(item, item_schema, f"{path}[{index}]", errors)
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key {key}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate_json(item, properties[key], f"{path}.{key}", errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected key {key}")
    return errors
