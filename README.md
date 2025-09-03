# Data Visualization Agent

This project implements a sophisticated visualization agent using ADK (Agent Development Kit) to process natural language queries and generate data visualizations from CSV data. The project includes both ADK-powered and standalone versions for maximum flexibility.

## 🚀 Features

- **Natural Language Processing**: Understands complex visualization requests in plain English
- **Multiple Chart Types**: Bar charts, pie charts, line charts, scatter plots, histograms, box plots, and tables
- **Smart Column Detection**: Semantic matching and intelligent defaults for data columns
- **Dual Architecture**: ADK-powered agent system + standalone testing environment
- **Interactive Interface**: Both demo and interactive modes for easy exploration
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Robust error handling with graceful degradation

## 📊 Supported Visualizations

- **Bar Charts**: Categorical comparisons and counts
- **Pie Charts**: Distribution and proportion analysis
- **Line Charts**: Trends and time-series data
- **Scatter Plots**: Correlation and relationship analysis
- **Histograms**: Frequency distributions
- **Box Plots**: Statistical summaries and outlier detection
- **Tables**: Raw data display with filtering

## 🏗 Project Structure

```
├── data/                           # Data files
│   └── qualys_vulns_sample_200.csv  # Sample vulnerability data
├── functions/                      # ADK-dependent core functionality
│   └── db_tools.py                # Original visualization tools
├── main_agent/                     # ADK agent implementation
│   ├── agent.py                   # Main agent with Gemini 2.5 Pro
│   └── ssl_config.py              # SSL configuration
├── subagents/                      # Supporting agents
│   ├── evaluate_result.py         # Result evaluation agent
│   └── rewrite_prompt.py          # Query rewriting agent
├── standalone_viz.py               # 🆕 ADK-free visualization engine
├── enhanced_app.py                 # 🆕 Enhanced standalone app
├── test_viz_agent.py               # 🆕 Unit tests
├── REVIEW.md                       # 🆕 Comprehensive code review
└── requirements.txt                # Dependencies
```

## 🛠 Setup & Installation

### Option 1: Standalone Mode (Recommended for Testing)

1. **Clone and navigate to the repository**:
   ```bash
   git clone <repository-url>
   cd data_visualiser_adk_agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the enhanced application**:
   ```bash
   python enhanced_app.py
   ```

### Option 2: ADK Mode (Production)

1. **Install Google ADK** (requires access):
   ```bash
   pip install google-adk
   ```

2. **Run with ADK**:
   ```bash
   adk web
   ```

## 🎯 Usage Examples

### Demo Mode
Run pre-defined queries to see the agent in action:
```bash
python enhanced_app.py
# Choose option 1 for demo mode
```

### Interactive Mode
Enter your own natural language queries:
```bash
python enhanced_app.py
# Choose option 2 for interactive mode

# Example queries:
> show me a pie chart of solution categories
> create a bar chart of vulnerabilities by app name
> display apps with high criticality vulnerabilities
> show the distribution of criticality levels
```

### Sample Queries You Can Try

- **"Show the distribution of vulnerabilities by criticality"**
  → Creates a histogram showing frequency of each criticality level

- **"Create a bar chart of apps by vulnerability count"**
  → Generates a bar chart comparing vulnerability counts across applications

- **"Display solution categories as a pie chart"**
  → Shows the breakdown of solution types (Patch, Configuration, Upgrade)

- **"Show me all high criticality vulnerabilities in a table"**
  → Filters and displays high-severity vulnerabilities in tabular format

- **"Create a scatter plot of apps vs criticality"**
  → Shows relationship between applications and their vulnerability criticality

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_viz_agent.py
```

The tests cover:
- Schema extraction and validation
- Query interpretation and parsing
- Chart type detection
- Column semantic matching
- Complete visualization pipeline
- Error handling and edge cases

## 📈 Data Schema

The sample dataset contains vulnerability management data with:

| Column | Description | Type |
|--------|-------------|------|
| `app_id` | Application identifier | String |
| `app_name` | Application name | String |
| `vulnerability_id` | CVE or QID identifier | String |
| `vulnerability_name` | Vulnerability description | String |
| `vulnerability_solution` | Remediation steps | String |
| `solution_category` | Fix type (Patch/Config/Upgrade) | String |
| `criticality` | Severity level (Critical/High/Medium/Low) | String |
| `scan_date` | Discovery timestamp | String |

## 🏗 Architecture Overview

### ADK Agent System
- **Main Agent**: Orchestrates visualization using Gemini 2.5 Pro
- **Rewrite Prompt Agent**: Refines ambiguous user queries
- **Evaluate Result Agent**: Assesses visualization effectiveness
- **Function Tools**: Schema extraction and visualization generation

### Standalone System
- **Query Parser**: Interprets natural language using semantic matching
- **Visualization Engine**: Generates charts using Matplotlib/Seaborn
- **Data Processor**: Handles aggregation, grouping, and filtering
- **Interactive Interface**: User-friendly CLI with rich formatting

## 🔧 Development

### Adding New Chart Types
1. Update `chart_types` dictionary in `interpret_query_with_schema()`
2. Add rendering logic in `generate_chart_image()`
3. Update documentation and tests

### Extending Data Sources
1. Modify `get_schema()` function for new data formats
2. Update column mapping in semantic matching
3. Add appropriate data validation

### Customizing Query Processing
1. Enhance `column_mappings` for domain-specific terms
2. Add new aggregation types in `agg_keywords`
3. Improve grouping detection logic

## 📝 Logging

The application generates detailed logs in `viz_agent.log` including:
- Query processing steps
- Schema extraction results
- Visualization generation details
- Error messages and stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite to ensure everything passes
5. Submit a pull request with detailed description

## 📋 Requirements

- Python 3.8+
- pandas 2.2.2+
- matplotlib 3.10.0+
- seaborn 0.13.0+
- plotly 5.22.0+
- dash 2.16.1+

## 🆘 Troubleshooting

### Common Issues

1. **Data file not found**: Ensure `data/qualys_vulns_sample_200.csv` exists
2. **Import errors**: Install all dependencies with `pip install -r requirements.txt`
3. **Visualization errors**: Check log file for detailed error messages
4. **ADK not available**: Use standalone mode for local development

### Getting Help

- Check the `REVIEW.md` file for comprehensive analysis
- Review test cases in `test_viz_agent.py` for usage examples
- Enable debug logging for detailed troubleshooting
- Run in demo mode to verify basic functionality

## 📄 License

This project is part of a data visualization agent development initiative.
