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
    pip install -r requirements.txt
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
python main.py
```

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
