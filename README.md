# Visualization Agent

This project implements a visualization agent using ADK (Agent Development Kit) to process natural language queries and generate data visualizations from CSV data.

## Project Structure

```
├── data/                  # Data files
│   └── qualys_vulns_sample_200.csv
├── functions/            # Core functionality
│   ├── __init__.py
│   └── db_tools.py      # Database and visualization tools
├── main_agent/          # Main agent implementation
│   ├── __init__.py
│   ├── agent.py         # Main agent definition
│   ├── ssl_config.py    # SSL configuration
│   └── test_agent.py    # Agent tests
├── subagents/           # Supporting agents
│   ├── __init__.py
│   ├── evaluate_result.py
│   └── rewrite_prompt.py
├── tools/               # Utility tools
│   ├── __init__.py
│   └── tools.py
├── .env                 # Environment variables
├── .gitignore          # Git ignore rules
├── adk.json            # ADK configuration
├── main.py             # Entry point
└── requirements.txt    # Python dependencies
```

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the agent:
```bash
adk web
```

## Features

- Natural language query processing
- Data visualization generation
- CSV data source support
- Multiple visualization types:
  - Bar charts
  - Pie charts
  - Line charts
  - Scatter plots
  - Histograms
  - Box plots
  - Tables

## Development

- Main agent configuration is in `main_agent/agent.py`
- Visualization tools are in `functions/db_tools.py`
- Supporting agents for query rewriting and evaluation are in `subagents/`
