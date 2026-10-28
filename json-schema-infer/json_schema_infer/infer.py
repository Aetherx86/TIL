import json
from typing import Any, Dict, List, Set, Union


class TypeLattice:
    """
    Implements a bounded semi-lattice for JSON data types:
    Top (any) -> {null, boolean, number -> integer, string, array, object} -> Bottom (never)
    """

    @classmethod
    def unify_types(cls, type_a: str, type_b: str) -> str:
        if type_a == type_b:
            return type_a
        # Integer is a subtype of number
        if {type_a, type_b} == {"integer", "number"}:
            return "number"
        return "anyOf"


def infer_schema(data: Any, track_bounds: bool = True) -> Dict[str, Any]:
    if data is None:
        return {"type": "null"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif isinstance(data, int):
        schema = {"type": "integer"}
        if track_bounds:
            schema["minimum"] = data
            schema["maximum"] = data
        return schema
    elif isinstance(data, float):
        schema = {"type": "number"}
        if track_bounds:
            schema["minimum"] = data
            schema["maximum"] = data
        return schema
    elif isinstance(data, str):
        schema = {"type": "string"}
        if "@" in data and "." in data and " " not in data:
            schema["format"] = "email"
        elif data.startswith("http://") or data.startswith("https://"):
            schema["format"] = "uri"
        elif len(data) == 36 and data.count("-") == 4:
            schema["format"] = "uuid"
        return schema
    elif isinstance(data, list):
        if not data:
            return {"type": "array", "items": {}}
        item_schemas = [infer_schema(x, track_bounds=track_bounds) for x in data]
        
        # Check if all items share the exact same primitive type
        types = [s.get("type") for s in item_schemas]
        if all(t == types[0] and t is not None for t in types):
            merged_items = {"type": types[0]}
            if types[0] in ["integer", "number"] and track_bounds:
                mins = [s["minimum"] for s in item_schemas if "minimum" in s]
                maxs = [s["maximum"] for s in item_schemas if "maximum" in s]
                if mins and maxs:
                    merged_items["minimum"] = min(mins)
                    merged_items["maximum"] = max(maxs)
            elif types[0] == "string":
                formats = {s.get("format") for s in item_schemas if "format" in s}
                if len(formats) == 1:
                    merged_items["format"] = list(formats)[0]
            return {"type": "array", "items": merged_items}

        # Deduplicate anyOf schemas
        unique_schemas = []
        seen = []
        for s in item_schemas:
            rep = json.dumps(s, sort_keys=True)
            if rep not in seen:
                seen.append(rep)
                unique_schemas.append(s)
        return {"type": "array", "items": {"anyOf": unique_schemas}}
    elif isinstance(data, dict):
        properties = {}
        for k, v in data.items():
            properties[k] = infer_schema(v, track_bounds=track_bounds)
        return {
            "type": "object",
            "properties": properties,
            "required": sorted(list(data.keys())),
        }
    return {"type": "any"}
