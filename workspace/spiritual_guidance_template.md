# Spiritual Guidance Report: {{ spread_name }}
**Date:** {{ timestamp }}
**Persona:** {{ persona }}
**Reading ID:** {{ reading_id }}

## Elemental Synthesis
- **Strengthening Combinations:** {{ strengthen_count }}
- **Weakening Combinations:** {{ weaken_count }}
- **Neutral Combinations:** {{ neutral_count }}

### Summary
{{ elemental_summary }}

{% if has_cusp_data %}
## Cusp Analysis
{{ cusp_summary }}

{% endif %}
{% for card in cards %}
### {{ card.position }}: {{ card.name }} ({{ card.orientation }})
- **Suit:** {{ card.suit }}
- **Element:** {{ card.element }}
- **Vibe Check:** {{ card.vibe_check.keywords }}
- **Narrative:** {{ card.vibe_check.narrative }}

{% endfor %}

## Integration Advice
{{ integration_advice }}