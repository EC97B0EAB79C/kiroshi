"""JSON schemas for the settings file and the panel spec file."""

SETTINGS_SCHEMA = {
    "type": "object",
    "required": ["schedule"],
    "properties": {
        "panel_spec": {"type": "string"},
        "epd": {"type": "string"},
        "refresh": {"type": "number", "exclusiveMinimum": 0},
        "schedule": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id"],
                "properties": {
                    "id": {"type": "integer", "minimum": 0},
                    "duration": {"type": "number", "exclusiveMinimum": 0},
                },
            },
        },
        "bedtime": {
            "type": "object",
            "required": ["start", "end", "id"],
            "properties": {
                "start": {"type": "string", "pattern": "^[0-2]?[0-9]:[0-5][0-9]$"},
                "end": {"type": "string", "pattern": "^[0-2]?[0-9]:[0-5][0-9]$"},
                "id": {"type": "integer", "minimum": 0},
            },
        },
    },
}

PANEL_TYPES = ["four", "horizontal", "vertical", "text", "time", "toggl", "picture", "calendar", "github", "picture_time"]

PANELS_SCHEMA = {
    "type": "array",
    "minItems": 1,
    "items": {"$ref": "#/$defs/panel"},
    "$defs": {
        "panel": {
            "type": "object",
            "required": ["type"],
            "properties": {
                "type": {"enum": PANEL_TYPES},
                "settings": {"type": "object"},
                "refresh": {"type": "boolean"},
                "panels": {"type": "array", "items": {"$ref": "#/$defs/panel"}},
            },
        }
    },
}
