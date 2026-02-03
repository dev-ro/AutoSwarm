# Semantic Switchboard Technical Specification

## 1. Introduction
The **Semantic Switchboard** is the central routing and orchestration component of the `PersonaEngine`. It is responsible for real-time persona selection, hot-swapping profiles based on environmental metrics, and ensuring stateful continuity across transitions.

## 2. Intent Detection Logic
The Intent Detection system analyzes incoming user prompts and task metadata to identify the optimal persona profile.

### 2.1 Keyword & Semantic Analysis
- **Keyword Matching:** Utilizes the `context_aware_triggers.domain_keywords` from the PDS.
- **Semantic Embedding:** Uses a transformer-based model (e.g., `BERT` or `Ada-002`) to compute cosine similarity between the user prompt and persona "Identity Layer" descriptions.
- **Confidence Scoring:** 
  $$Score_{semantic} = \sum (KeywordMatches \times Weight_{keyword}) + Sim(Prompt, Identity)$$

### 2.2 Task Metadata Extraction
The Switchboard extracts metadata from the task request:
- **Domain:** (e.g., Financial, Creative, Technical)
- **Complexity Level:** (Mapping to `lexile_complexity`)
- **Urgency/Risk Level:** (Determining the need for executive personas)

## 3. Metric-Aware Trigger System
This system allows the Switchboard to react to external business or system metrics rather than just user prompts.

### 3.1 Refined Metric Triggers
The Switchboard monitors a real-time `MetricStream`. Triggers defined in the PDS (Section 6) are evaluated:
- **Hard Triggers (Overrides):** Triggers like `burn_rate_variance > 0.05` generate a `HIGH_PRIORITY_INTERRUPT` signal, forcing an immediate swap to the designated persona (e.g., Risk-Averse Analytical).
- **Soft Triggers:** Metrics that increase the weight of a specific persona without forcing an immediate swap.

### 3.2 Metric Evaluation Protocol
```python
def evaluate_metric_triggers(current_metrics, personas):
    for persona in personas:
        for trigger in persona.metric_threshold_triggers:
            if eval_logic(trigger.condition, current_metrics):
                return persona, trigger.priority
    return None, None
### 3.2 Metric Evaluation Protocol (Metric-Threshold Triggers)
The Switchboard parses the `metric_threshold_triggers` block using a specialized DSL (Domain Specific Language) parser to avoid security risks associated with `eval()`.

**Standard Trigger Syntax:**
`if <metric_key> <operator> <value>: <action_id>`

- **Metric Keys:** `burn_rate_variance`, `debt_to_equity_ratio`, `confidence_interval`, `market_volatility`, etc.
- **Operators:** `>`, `<`, `>=`, `<=`, `==`.
- **Action IDs:** `OVERRIDE`, `WARN`, `INJECT_CONSTRAINT`.

**Example Logic Gate:**
```json
{
  "trigger": "burn_rate_variance > 0.05",
  "priority": "CRITICAL",
  "target_persona": "EXEC-RAA-2026",
  "instruction": "Enforce RULE_02 and RAA voice DNA immediately."
}
```
3. **Formula:** 
   $$TotalScore = (w_1 \cdot S_{keyword}) + (w_2 \cdot S_{semantic}) + (w_3 \cdot S_{metric})$$
4. **Threshold:** Persona is only activated if $TotalScore > ActivationThreshold$ (defined in PDS).

### 4.2 Hot-Swapping Mechanism
When a swap occurs mid-session:
1. **Current Persona Suspend:** Save the current state (Internal Monologue, Active Task).
2. **Contextual Handover:** Generate a "Transition Brief" (see Section 5).
3. **New Persona Load:** Load the new PDS profile and inject the brief.

## 5. Stateful Transition Protocols
To prevent "persona amnesia," the Switchboard implements a structured transition.

### 5.1 Context Injection (The "Handover Brief")
When Persona A swaps to Persona B, the Switchboard generates a summary:
- **Reason for Swap:** (e.g., "Burn rate exceeded 5%, switching to Risk-Averse Analytical")
- **Active Goal:** The current objective the user is trying to achieve.
- **Sentiment State:** The emotional state of the conversation.
- **Memory Buffer:** Last 3-5 exchanges summarized.

### 5.2 Transition Logic Flow
1. **Detect Change:** Intent or Metric triggers a swap.
2. **Wait for Logic Gate:** Check if the current sentence is finished (Atomic Transition).
3. **Inject System Prompt:** 
   `[SYSTEM]: ALERT: Swapping to EXEC-RAA-2026. Reason: Financial Metric Threshold Met. Context: User is discussing expansion. Current risk score: 0.82.`
4. **Persona Execution:** New persona acknowledges the context and responds according to its `Voice DNA`.

## 6. Conflict Resolution
If multiple personas meet the activation threshold:
- **Hierarchy of Authority:** Executive personas (RAA, AI-X) override specialized personas (Writer, Coder) in conflict scenarios.
- **Tie-breaker:** The persona with the highest $S_{metric}$ wins.

---
**Document Status:** Technical Specification v1.0
**Project:** PersonaEngine