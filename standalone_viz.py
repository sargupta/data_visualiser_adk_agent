"""
Standalone visualization tools that work without Google ADK dependencies.
This module contains the core visualization logic extracted from db_tools.py
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import json
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import os

logger = logging.getLogger(__name__)

# Helper: convert numpy scalars to native Python types
def to_python_scalar(value):
    if isinstance(value, (np.generic,)):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value

# Initialize DataFrame
try:
    df = pd.read_csv("data/qualys_vulns_sample_200.csv")
    logger.info("[CSV Tool] Successfully loaded CSV data")
except Exception as e:
    logger.error(f"[CSV Tool] Error loading CSV: {str(e)}")
    df = pd.DataFrame()  # fallback to empty DataFrame

def get_schema(input: Optional[dict] = None) -> dict:
    """
    Get schema information from the CSV data.
    
    Args:
        input (Optional[dict]): Not used for CSV files
    Returns:
        dict: schema description
    """
    try:
        # Prepare JSON-serializable sample rows
        sample_df = df.head(3).copy()
        sample_df = sample_df.where(pd.notnull(sample_df), None)

        sample_records = []
        for record in sample_df.to_dict(orient='records'):
            sample_records.append({k: to_python_scalar(v) for k, v in record.items()})

        schema = {
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'sample': sample_records
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
        'asset': ['asset', 'host', 'endpoint', 'system'],
        'app': ['app', 'application', 'software'],
        'critical': ['critical', 'criticality', 'severity']
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
                col for col in schema['columns'] 
                if pd.api.types.is_numeric_dtype(df[col].dtype)
            ]
            if numeric_cols:
                columns = [numeric_cols[0]]
        
        elif result["chart_type"] == "scatter":
            # For scatter plots, try to find two numeric columns
            numeric_cols = [
                col for col in schema['columns'] 
                if pd.api.types.is_numeric_dtype(df[col].dtype)
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
            # For histogram, return as DataFrame, not Series
            return df[[columns[0]]]
            
        if chart_type == "scatter":
            if len(columns) >= 2:
                return df[columns[:2]]  # Take first two columns
            return df[[columns[0]]]  # Return as DataFrame, not Series
            
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

def generate_chart_image(result_df, parsed_task):
    """Generate a matplotlib/seaborn chart and return as base64 encoded image"""
    try:
        chart_type = parsed_task["chart_type"]
        columns = parsed_task["columns"]
        aggregation = parsed_task.get("aggregation")
        group_by = parsed_task.get("group_by")
        
        # Set up the plot
        plt.figure(figsize=(10, 6))
        
        if chart_type == "bar":
            x_col = group_by if group_by else columns[0]
            y_col = columns[0] if group_by else "count"
            title = f"Bar Chart of {y_col} by {x_col}" if group_by else f"Bar Chart of {x_col}"
            
            if group_by:
                sns.barplot(data=result_df, x=x_col, y=y_col)
            else:
                result_df[x_col].value_counts().plot(kind='bar')
            plt.title(title)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
        elif chart_type == "pie":
            names_col = group_by if group_by else columns[0]
            values_col = columns[0] if group_by else "count"
            title = f"Distribution of {values_col} by {names_col}"
            
            if group_by:
                plt.pie(result_df[values_col], labels=result_df[names_col], autopct='%1.1f%%')
            else:
                value_counts = result_df[names_col].value_counts()
                plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
            plt.title(title)
            
        elif chart_type == "line":
            x_col = group_by if group_by else columns[0]
            y_col = columns[0] if group_by else "count"
            title = f"Trend of {y_col} by {x_col}"
            
            if group_by:
                sns.lineplot(data=result_df, x=x_col, y=y_col)
            else:
                result_df[x_col].value_counts().sort_index().plot(kind='line')
            plt.title(title)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
        elif chart_type == "scatter":
            if len(columns) >= 2:
                plt.scatter(result_df[columns[0]], result_df[columns[1]])
                plt.xlabel(columns[0])
                plt.ylabel(columns[1])
                plt.title(f"Scatter Plot: {columns[1]} vs {columns[0]}")
            else:
                plt.scatter(range(len(result_df)), result_df[columns[0]])
                plt.ylabel(columns[0])
                plt.title(f"Scatter Plot of {columns[0]}")
            plt.tight_layout()
            
        elif chart_type == "histogram":
            # For categorical data, create a count histogram
            if df[columns[0]].dtype == 'object':
                value_counts = df[columns[0]].value_counts()
                plt.bar(value_counts.index, value_counts.values, edgecolor='black')
                plt.xlabel(columns[0])
                plt.ylabel('Count')
                plt.title(f"Distribution of {columns[0]}")
                plt.xticks(rotation=45)
            else:
                plt.hist(result_df[columns[0]], bins=20, edgecolor='black')
                plt.xlabel(columns[0])
                plt.ylabel('Frequency')
                plt.title(f"Distribution of {columns[0]}")
            plt.tight_layout()
            
        elif chart_type == "box":
            plt.boxplot(result_df[columns[0]])
            plt.ylabel(columns[0])
            plt.title(f"Box Plot of {columns[0]}")
            plt.tight_layout()
            
        else:  # Default to table - create a text representation
            plt.figure(figsize=(12, 8))
            plt.axis('off')
            table_data = result_df.head(10).values.tolist()
            table_data.insert(0, list(result_df.columns))
            
            table = plt.table(cellText=table_data, loc='center', cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1.2, 1.5)
            plt.title("Data Table")
        
        # Convert plot to base64 image
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_base64
        
    except Exception as e:
        logger.error(f"Error generating chart image: {str(e)}")
        # Return a simple error image
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, f'Error generating chart: {str(e)}', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.axis('off')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_base64

def run_dash_query(input: Optional[dict] = None) -> dict:
    """
    Process a natural language query and return visualization results.
    
    Args:
        input (dict): A dictionary with a natural language query provided by the model.
    Returns:
        dict: A serializable visualization result with metadata and data.
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

        # Step 4: Generate visualization data
        chart_type = parsed_task["chart_type"]
        columns = parsed_task["columns"]
        aggregation = parsed_task.get("aggregation")
        group_by = parsed_task.get("group_by")
        
        # Generate chart image
        chart_image = generate_chart_image(result_df, parsed_task)
        
        # Create serializable response
        if chart_type == "table":
            # For tables, return the data directly
            safe_df = result_df.where(pd.notnull(result_df), None)
            rows = []
            for rec in safe_df.to_dict(orient="records"):
                rows.append({k: to_python_scalar(v) for k, v in rec.items()})
            
            return {
                "visualization_type": "table",
                "columns": list(result_df.columns),
                "data": rows,
                "chart_image": chart_image,
                "query_info": {
                    "chart_type": chart_type,
                    "columns_used": columns,
                    "aggregation": aggregation,
                    "group_by": group_by
                }
            }
        else:
            # For charts, return the processed data
            return {
                "visualization_type": "chart",
                "chart_type": chart_type,
                "chart_image": chart_image,
                "raw_data": result_df.where(pd.notnull(result_df), None).to_dict(orient="records"),
                "query_info": {
                    "chart_type": chart_type,
                    "columns_used": columns,
                    "aggregation": aggregation,
                    "group_by": group_by
                }
            }

        logger.info(f"[Dash Tool] Visualization data generated.")

    except Exception as ex:
        logger.error(f"[Dash Tool] Error: {str(ex)}")
        return {"error": str(ex)}