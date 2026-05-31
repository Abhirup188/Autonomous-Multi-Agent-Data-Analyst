Autonomous Multi-Agent Data Analyst

An autonomous, self-healing AI swarm built with LangGraph, OpenAI, and Streamlit. 

This pipeline acts as a tireless Data Scientist. Simply upload a raw CSV, and the swarm will autonomously ingest the data, formulate strategic business hypotheses, write its own Python/Pandas code, execute it in a secure local environment, and generate interactive visual dashboards.

Features
* Zero-Prompt Orchestration: The user uploads a CSV and clicks one button. The AI handles the strategy, coding, and reporting without further prompting.
* Self-Healing Execution Loop: If the LLM generates buggy code, the Executor Node catches the Python traceback, feeds the error back into the Coder Node, and forces the AI to debug and rewrite its own code until it executes successfully.
* Interactive Visual Dashboards: The AI dynamically writes `plotly.express` code to generate interactive, hoverable charts based on its findings.
* Real-World Automations: The pipeline automatically pushes anomalies and at-risk customer data to Make.com via Webhooks, triggering live Slack alerts and HubSpot CRM updates.

System Architecture (LangGraph)
1. Profiler Node: Extracts metadata, column headers, and statistical summaries from the raw CSV.
2. Strategist Node: Generates highly targeted, actionable business hypotheses based purely on the metadata.
3. Coder Node: Writes executable Python (`pandas`, `plotly`) to answer the hypotheses.
4. Executor Node: Runs the generated code locally. If it fails, it routes the error back to the Coder (max 3 retries).
5. Reporter Node: Synthesizes the raw mathematical outputs into a professional, executive Markdown report.
6. Automator Node: Triggers third-party webhooks (Slack/CRM) for critical data anomalies.

Installation & Setup

1. Clone the repository: 
   ```bash
   git clone https://[github.com/Abhirup188/autonomous-multi-agent-data-analyst](https://github.com/Abhirup188/Autonomous-Multi-Agent-Data-Analyst).git
   cd autonomous-data-analyst
