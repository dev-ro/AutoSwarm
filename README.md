# AutoSwarm

AutoSwarm is an autonomous agent system designed to plan and execute complex tasks using a swarm of specialized agents (Executive, Researcher, Coder, Social, Finance). It leverages the Gemini 3 Pro model for high-level reasoning and includes robust safety and reliability features.

## Features

- **Multi-Agent Architecture:** Specialized agents for different domains.
- **Dynamic Replanning:** An "OODA Loop" allowing the Executive Agent to adapt plans based on new information.
- **Robust Coder:** Implementing a "Look, then Leap" protocol and Self-Healing capabilities to fix its own errors.
- **Semantic Handoffs:** Intelligent detection of high-value opportunities using LLM semantic analysis.
- **Docker Sandbox:** Secure execution of shell commands within an isolated Docker container.
- **Smart Browser:** Robust web scraping with context sanitization and smart truncation.
- **Efficiency Gates:** Heuristic filters to minimize expensive LLM calls.

## Setup

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    uv sync
    ```
3.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```
4.  **Install Docker Desktop:** Ensure Docker is running for the sandbox features.
5.  **Environment Variables:**
    Create a `.env` file in the root directory:
    ```
    GOOGLE_API_KEY=your_gemini_api_key
    ```

## Usage

Run the main entry point to start the swarm:

```bash
uv run main.py
```

## Repository Structure

- `src/`: Core application code
  - `agents/`: Specialized agent implementations (Executive, Coder, Tarot, etc.)
  - `core/`: Core orchestrator, state management, and knowledge base
  - `orchestration/`: Multi-agent routing and team management
  - `personality/`: NLU-driven personality routing and `profiles/`
  - `tarot/`: The core tarot reading engine
  - `tools/`: Shared tools (Google Docs, report generators)
- `tests/`: Unit and end-to-end tests
- `scripts/`: Utility scripts for population and debugging
- `workspace/`: Agents' working directory (sandbox output)
- `secrets/`: Local secrets (e.g., service accounts)


## detailed System Upgrades

### 1. Robustness: The "Smart" Coder
The CoderAgent now explores file structures before editing and strictly verifies file existence to prevent blind overwrites.

### 2. Logic: Semantic Handoffs
The Manager Agent uses semantic analysis to detect "high-value opportunities" (e.g., jobs, critical failures) rather than relying on brittle keyword matching.

### 3. Reliability: Self-Healing
If the CoderAgent encounters an error during testing, it enters a self-correction loop to diagnose and fix the issue before reporting back.

### 4. Security: Docker Sandbox
All shell commands executed by the CoderAgent are run inside a `python:3.11-alpine` Docker container (`autoswarm_sandbox`), protecting your host machine.

### 5. Efficiency: Heuristic Gates
The system filters routine outputs using keyword heuristics to avoid unnecessary and expensive semantic analysis calls.

### 6. Strategy: Cost-Benefit Analysis 
The `AnalystAgent` executes objective optimization loops across the repository, assessing decisions strictly on quantifiable cost-benefit metrics while rejecting unneeded complexity.

### 7. Signal Density: Subjective Agents
The `TarotAgent` and related diagnostic logic force maximum signal density. They utilize strict declarative reporting (e.g. four explicit nodes) and absolute clinical honesty with zero forced positivity.
