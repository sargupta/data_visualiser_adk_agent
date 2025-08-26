from google.adk.tools.base_tool import BaseTool
from google.adk.tools.function_tool import FunctionTool
import ast
import logging
import pandas as pd
from typing import Optional
from dash import dcc, html
import plotly.express as px
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Initialize DataFrame
try:
    df = pd.read_csv("data/qualys_vulns_sample_200.csv")
    logger.info("[CSV Tool] Successfully loaded CSV data")
except Exception as e:
    logger.error(f"[CSV Tool] Error loading CSV: {str(e)}")
    df = pd.DataFrame()  # fallback to empty DataFrame


def get_schema(input: Optional[dict] = None) -> dict:
    """
    Args:
        input (Optional[dict]): Not used for CSV files
    Returns:
        dict: schema description
    """
    try:
        schema = {
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'sample': df.head(3).to_dict()
        }
        logger.info(f"[CSV Tool] Schema retrieved: {schema}")
        return {"schema_description": schema}
    except Exception as ex:
        logger.error(f"[CSV Tool] Error getting schema: {str(ex)}")
        return {"error": str(ex)}



def interpret_query_with_schema(query, schema):
    """Interpret natural language query to determine visualization parameters"""
    query = query.lower()
    result = {
        "chart_type": "table",  # default
        "columns": [],
        "aggregation": None,
        "group_by": None
    }
    
    # Determine chart type first since we'll need it for column selection
    chart_types = {
        "bar": ["bar chart", "bar plot", "barchart", "barplot"],
        "pie": ["pie chart", "pie plot", "piechart", "pieplot"],
        "line": ["line chart", "line plot", "linechart", "lineplot", "trend"],
        "scatter": ["scatter plot", "scatter chart", "scatterplot", "correlation"],
        "histogram": ["histogram", "distribution"],
        "box": ["box plot", "boxplot", "box and whisker"],
        "table": ["table", "raw data"]
    }
    
    for chart, patterns in chart_types.items():
        if any(pattern in query for pattern in patterns):
            result["chart_type"] = chart
            break
            
    # Map common natural language terms to potential column names
    column_mappings = {
        # Generic analysis terms
        'risk': ['risk', 'risk_score', 'risk_level', 'severity'],
        'category': ['category', 'type', 'classification', 'group'],
        'status': ['status', 'state', 'condition'],
        'date': ['date', 'timestamp', 'created_at', 'modified_at', 'time'],
        'count': ['count', 'number', 'quantity', 'amount'],
        # Domain specific (Qualys vulnerabilities)
        'vulnerability': ['vulnerability', 'vuln', 'cve', 'weakness'],
        'severity': ['severity', 'criticality', 'impact'],
        'threat': ['threat', 'risk', 'danger'],
        'patch': ['patch', 'fix', 'solution', 'remediation'],
        'asset': ['asset', 'host', 'endpoint', 'system']
    }
    
    # First try exact column matches
    columns = [col for col in schema['columns'] if col.lower() in query]
    
    # If no exact matches, try semantic matching
    if not columns:
        # Look for semantic matches using the mappings
        for concept, related_terms in column_mappings.items():
            if any(term in query for term in related_terms):
                # Find columns that might match this concept
                potential_cols = [
                    col for col in schema['columns'] 
                    if any(term in col.lower() for term in related_terms)
                ]
                if potential_cols:
                    columns.extend(potential_cols)
    
    # If still no columns found, make intelligent default choices based on chart type
    if not columns:
        if result["chart_type"] in ["pie", "bar", "line"]:
            # For these charts, prefer categorical columns with reasonable cardinality
            categorical_cols = [
                col for col, dtype in schema['dtypes'].items() 
                if dtype == 'object' or dtype == 'category'
            ]
            if categorical_cols:
                # Check value counts to find a good categorical column
                for col in categorical_cols:
                    if 2 <= df[col].nunique() <= 20:  # reasonable number of categories
                        columns = [col]
                        break
                if not columns:
                    columns = [categorical_cols[0]]
        
        elif result["chart_type"] in ["histogram", "box"]:
            # For these charts, prefer numeric columns
            numeric_cols = [
                col for col, dtype in schema['dtypes'].items() 
                if pd.api.types.is_numeric_dtype(dtype)
            ]
            if numeric_cols:
                columns = [numeric_cols[0]]
        
        elif result["chart_type"] == "scatter":
            # For scatter plots, try to find two numeric columns
            numeric_cols = [
                col for col, dtype in schema['dtypes'].items() 
                if pd.api.types.is_numeric_dtype(dtype)
            ]
            if len(numeric_cols) >= 2:
                columns = numeric_cols[:2]
        
        # Final fallback
        if not columns:
            columns = [schema['columns'][0]]
    
    result["columns"] = columns
    
    # Detect aggregation
    agg_keywords = {
        "count": ["count", "number of"],
        "sum": ["sum", "total"],
        "average": ["average", "mean"],
        "max": ["maximum", "highest", "max"],
        "min": ["minimum", "lowest", "min"]
    }
    
    for agg, patterns in agg_keywords.items():
        if any(pattern in query for pattern in patterns):
            result["aggregation"] = agg
            break
    
    # Detect grouping
    if "by" in query or "grouped by" in query or "group by" in query:
        # Look for column name after "by"
        query_parts = query.split("by")
        if len(query_parts) > 1:
            for col in schema['columns']:
                if col.lower() in query_parts[1].lower():
                    result["group_by"] = col
                    break
    
    return result

def execute_task_on_df(parsed_task):
    """Execute the parsed query on the DataFrame"""
    chart_type = parsed_task["chart_type"]
    columns = parsed_task["columns"]
    aggregation = parsed_task["aggregation"]
    group_by = parsed_task["group_by"]
    
    try:
        if chart_type == "table":
            return df[columns].head(10)
        
        if chart_type == "histogram":
            # For histogram, we only need the data as is
            return df[columns[0]]
            
        if chart_type == "scatter":
            if len(columns) >= 2:
                return df[columns[:2]]  # Take first two columns
            return df[columns[0]]
            
        # For aggregated charts (bar, pie, line)
        if group_by:
            if aggregation == "count":
                data = df.groupby(group_by)[columns[0]].count().reset_index()
            elif aggregation == "sum":
                data = df.groupby(group_by)[columns[0]].sum().reset_index()
            elif aggregation == "average":
                data = df.groupby(group_by)[columns[0]].mean().reset_index()
            elif aggregation == "max":
                data = df.groupby(group_by)[columns[0]].max().reset_index()
            elif aggregation == "min":
                data = df.groupby(group_by)[columns[0]].min().reset_index()
            else:
                data = df.groupby(group_by)[columns[0]].count().reset_index()
        else:
            # Simple value counts for categorical data
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], "count"]
            
        return data
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return df[columns].head(10)  # Fallback to simple table

def generate_dash_components(result_df, parsed_task=None):
    """Generate Dash visualization components based on the query results"""
    if parsed_task is None:
        parsed_task = {"chart_type": "table", "columns": []}
        
    chart_type = parsed_task["chart_type"]
    columns = parsed_task["columns"]
    aggregation = parsed_task.get("aggregation")
    group_by = parsed_task.get("group_by")
    
    try:
        # Handle different chart types
        if chart_type == "bar":
            x_col = group_by if group_by else columns[0]
            y_col = columns[0] if group_by else "count"
            title = f"Bar Chart of {y_col} by {x_col}" if group_by else f"Bar Chart of {x_col}"
            fig = px.bar(result_df, x=x_col, y=y_col, title=title)
            
        elif chart_type == "pie":
            names_col = group_by if group_by else columns[0]
            values_col = columns[0] if group_by else "count"
            title = f"Distribution of {values_col} by {names_col}"
            fig = px.pie(result_df, names=names_col, values=values_col, title=title)
            
        elif chart_type == "line":
            x_col = group_by if group_by else columns[0]
            y_col = columns[0] if group_by else "count"
            title = f"Trend of {y_col} by {x_col}"
            fig = px.line(result_df, x=x_col, y=y_col, title=title)
            
        elif chart_type == "scatter":
            if len(columns) >= 2:
                fig = px.scatter(result_df, x=columns[0], y=columns[1],
                               title=f"Scatter Plot: {columns[1]} vs {columns[0]}")
            else:
                fig = px.scatter(result_df, x=columns[0], y="count",
                               title=f"Scatter Plot of {columns[0]}")
                
        elif chart_type == "histogram":
            fig = px.histogram(result_df, x=columns[0],
                             title=f"Distribution of {columns[0]}")
            
        elif chart_type == "box":
            fig = px.box(result_df, y=columns[0],
                        title=f"Box Plot of {columns[0]}")
            
        else:  # Default to table
            return html.Table([
                html.Thead(html.Tr([html.Th(col) for col in result_df.columns])),
                html.Tbody([
                    html.Tr([html.Td(result_df.iloc[i][col]) for col in result_df.columns])
                    for i in range(len(result_df))
                ])
            ])
        
        # Add common layout settings
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode='closest'
        )
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        # Fallback to table view
        return html.Table([
            html.Thead(html.Tr([html.Th(col) for col in result_df.columns])),
            html.Tbody([
                html.Tr([html.Td(result_df.iloc[i][col]) for col in result_df.columns])
                for i in range(min(10, len(result_df)))
            ])
        ])

def run_dash_query(input: Optional[dict] = None) -> dict:
    """
    Args:
        input (dict): A dictionary with a natural language query provided by the model.
    Returns:
        dict: A Dash-compatible output or error message.
    """
    user_query = input.get("query")

    logger.info(f"[Dash Tool] User Query: {user_query}")

    try:
        # Step 1: Get schema
        schema_result = get_schema()
        schema = schema_result.get("schema_description")

        if not schema:
            raise ValueError("Schema could not be retrieved.")

        # Step 2: Interpret query using schema
        parsed_task = interpret_query_with_schema(user_query, schema)

        # Step 3: Execute task on DataFrame
        result_df = execute_task_on_df(parsed_task)

        # Step 4: Generate Dash components
        dash_output = generate_dash_components(result_df, parsed_task)

        logger.info(f"[Dash Tool] Dash Output generated.")

        return {"dash_output": dash_output}
    except Exception as ex:
        logger.error(f"[Dash Tool] Error: {str(ex)}")
        return {"error": str(ex)}


# Create the function tools
get_schema_tool = FunctionTool(get_schema)
run_dash_query_tool = FunctionTool(run_dash_query)

# Make sure tools are available for import
__all__ = ['get_schema_tool', 'run_dash_query_tool']