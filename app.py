"""
Standalone Data Visualization App
This file provides a local testing interface for the visualization agent
without requiring Google ADK dependencies.
"""

import pandas as pd
import json
from typing import Dict, Any, Optional
from standalone_viz import get_schema, run_dash_query, interpret_query_with_schema


def run_visualization_test(query: str) -> Dict[str, Any]:
    """
    Test the visualization pipeline with a natural language query.
    
    Args:
        query: Natural language visualization request
        
    Returns:
        Dictionary containing visualization results and metadata
    """
    try:
        print(f"Processing query: {query}")
        
        # Step 1: Get schema
        schema_result = get_schema()
        if "error" in schema_result:
            return {"error": f"Schema error: {schema_result['error']}"}
        
        schema = schema_result["schema_description"]
        print(f"Schema loaded: {len(schema['columns'])} columns")
        
        # Step 2: Parse the query
        parsed_task = interpret_query_with_schema(query, schema)
        print(f"Parsed task: {parsed_task}")
        
        # Step 3: Generate visualization
        viz_result = run_dash_query({"query": query})
        if "error" in viz_result:
            return {"error": f"Visualization error: {viz_result['error']}"}
        
        # Return comprehensive result
        return {
            "summary": f"Generated {parsed_task['chart_type']} chart using columns: {parsed_task['columns']}",
            "visualization_query": parsed_task,
            "raw_result": viz_result,
            "result_evaluation": "Success" if viz_result else "Error"
        }
        
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def demo_queries():
    """Run demonstration queries to showcase the visualization capabilities."""
    
    demo_queries_list = [
        "Show the distribution of vulnerabilities by criticality",
        "Create a bar chart of vulnerabilities by app name",
        "Show me a pie chart of solution categories",
        "Display the scan dates as a table",
        "Create a histogram of vulnerability criticality"
    ]
    
    print("=" * 60)
    print("DATA VISUALIZATION AGENT DEMO")
    print("=" * 60)
    
    # Show schema first
    schema_result = get_schema()
    if "schema_description" in schema_result:
        schema = schema_result["schema_description"]
        print(f"\nAvailable data columns: {', '.join(schema['columns'])}")
        print(f"Sample data shape: {len(schema['sample'])} sample rows")
        print("\nSample data:")
        for i, sample in enumerate(schema['sample'][:2]):  # Show first 2 rows
            print(f"  Row {i+1}: {sample}")
    
    print("\n" + "=" * 60)
    print("RUNNING DEMO QUERIES")
    print("=" * 60)
    
    for i, query in enumerate(demo_queries_list, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        result = run_visualization_test(query)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success: {result['summary']}")
            if "visualization_query" in result:
                vq = result["visualization_query"]
                print(f"   Chart Type: {vq['chart_type']}")
                print(f"   Columns: {vq['columns']}")
                if vq.get('aggregation'):
                    print(f"   Aggregation: {vq['aggregation']}")
                if vq.get('group_by'):
                    print(f"   Group By: {vq['group_by']}")


def interactive_mode():
    """Run in interactive mode for custom queries."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print("Enter natural language queries for data visualization.")
    print("Type 'quit' to exit, 'demo' to run demo queries, 'schema' to show data schema.")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'demo':
                demo_queries()
                continue
            elif user_input.lower() == 'schema':
                schema_result = get_schema()
                if "schema_description" in schema_result:
                    print(json.dumps(schema_result["schema_description"], indent=2))
                continue
            elif not user_input:
                continue
            
            result = run_visualization_test(user_input)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ {result['summary']}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def run():
    """Main entry point for the application."""
    print("Data Visualization Agent - Standalone Mode")
    print("This app provides local testing without ADK dependencies.")
    
    try:
        # Quick validation that data file exists
        import os
        data_path = "data/qualys_vulns_sample_200.csv"
        if not os.path.exists(data_path):
            print(f"❌ Error: Data file not found at {data_path}")
            print("Please ensure the CSV file exists before running the app.")
            return
        
        # Check if data can be loaded
        df = pd.read_csv(data_path)
        print(f"✅ Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        
        print("\nChoose mode:")
        print("1. Demo mode (run pre-defined queries)")
        print("2. Interactive mode (enter your own queries)")
        
        choice = input("\nEnter choice (1 or 2, default=1): ").strip()
        
        if choice == "2":
            interactive_mode()
        else:
            demo_queries()
            
    except Exception as e:
        print(f"❌ Startup error: {str(e)}")


if __name__ == "__main__":
    run()