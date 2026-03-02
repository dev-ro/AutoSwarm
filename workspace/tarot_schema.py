SCHEMA = {
    "type": "object",
    "properties": {
        "readings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "spread": {"type": "string"},
                    "persona": {"type": "string"},
                    "cards": {
                        "type": "array",
                        "items": {
"name": {"type": "string"},
                                "number": {"type": "integer"},
                                "arcana": {"type": "string", "enum": ["Major", "Minor"]},
                                "suit": {"type": "string"},
                                "orientation": {"type": "string", "enum": ["upright", "reversed"]},
                                "element": {"type": "string"},
                                "astrology": {"type": "string"},
                                "kabbalah": {"type": "string"},
                                "vibe_check": {
                                    "type": "object",
                                    "properties": {
                                        "keywords": {"type": "string"},
                                        "narrative": {"type": "string"},
                                        "traditional": {"type": "string"}
                                    },
                                    "required": ["keywords", "narrative", "traditional"]
                                },
                                "cusp_relevant": {"type": "boolean"}
                            },
                            "required": ["position", "name", "number", "arcana", "suit", "orientation", "element", "astrology", "kabbalah", "vibe_check"]
                                        "narrative": {"type": "string"}
                                    },
                                    "required": ["keywords", "narrative"]
                                },
                                "cusp_relevant": {"type": "boolean"}
                            },
                            "required": ["position", "name", "orientation", "element", "astrology", "kabbalah", "vibe_check"]
                        }
                    },
                    "synthesis": {
                        "type": "object",
                        "properties": {
                            "elemental_dignities": {
                                "type": "object",
                                "properties": {
                                    "strengthen": {"type": "integer"},
                                    "weaken": {"type": "integer"},
                                    "neutral": {"type": "integer"}
                                },
                                "required": ["strengthen", "weaken", "neutral"]
                            },
                            "cusp_analysis": {
                                "type": "object",
                                "properties": {
                                    "target_signs": {"type": "array", "items": {"type": "string"}},
                                    "relevant_cards_count": {"type": "integer"},
                                    "found_signs": {"type": "array", "items": {"type": "string"}},
                                    "summary": {"type": "string"}
                                },
                                "required": ["target_signs", "relevant_cards_count", "found_signs", "summary"]
                            }
                        },
                        "required": ["elemental_dignities"]
                    }
                },
                "required": ["id", "timestamp", "spread", "persona", "cards", "synthesis"]
            }
        }
    },
    "required": ["readings"]
}

def validate_reading_data(data):
    from jsonschema import validate
    validate(instance=data, schema=SCHEMA)
    return True

if __name__ == "__main__":
    import json
    # Simple self-test
    sample_data = {
        "readings": [
            {
                "id": "20231027120000",
                "timestamp": "2023-10-27T12:00:00Z",
                "spread": "celtic_cross",
                "persona": "main_character",
                "cards": [
                    {
                        "position": "Present",
                        "name": "The Moon",
                        "orientation": "upright",
                        "element": "Major",
                        "astrology": "Pisces",
                        "kabbalah": "Qoph (Pisces)",
                        "vibe_check": {
                            "keywords": "Uncanny valley energy...",
                            "narrative": "Uncanny Valley. Things aren't what they seem..."
                        },
                        "cusp_relevant": True
                    }
                ],
                "synthesis": {
                    "elemental_dignities": {
                        "strengthen": 5,
                        "weaken": 2,
                        "neutral": 3
                    },
                    "cusp_analysis": {
                        "target_signs": ["Pisces", "Aries"],
                        "relevant_cards_count": 1,
                        "found_signs": ["Pisces"],
                        "summary": "Focus on Pisces qualities within your cusp placement."
                    }
                }
            }
        ]
    }
    try:
        validate_reading_data(sample_data)
        print("Schema validation successful!")
    except Exception as e:
        print(f"Schema validation failed: {e}")