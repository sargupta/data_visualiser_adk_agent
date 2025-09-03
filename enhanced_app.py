"""
Enhanced Data Visualization App with better error handling and logging
"""

import pandas as pd
import json
import logging
from typing import Dict, Any, Optional
from standalone_viz import get_schema, run_dash_query, interpret_query_with_schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('viz_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_visualization_test(query: str) -> Dict[str, Any]:
    """
    Test the visualization pipeline with a natural language query.
    
    Args:
        query: Natural language visualization request
        
    Returns:
        Dictionary containing visualization results and metadata
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # Step 1: Get schema
        schema_result = get_schema()
        if "error" in schema_result:
            error_msg = f"Schema error: {schema_result['error']}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        schema = schema_result["schema_description"]
        logger.info(f"Schema loaded: {len(schema['columns'])} columns")
        
        # Step 2: Parse the query
        parsed_task = interpret_query_with_schema(query, schema)
        logger.info(f"Parsed task: {parsed_task}")
        
        # Step 3: Generate visualization
        viz_result = run_dash_query({"query": query})
        if "error" in viz_result:
            error_msg = f"Visualization error: {viz_result['error']}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Return comprehensive result
        success_msg = f"Generated {parsed_task['chart_type']} chart using columns: {parsed_task['columns']}"
        logger.info(success_msg)
        
        return {
            "summary": success_msg,
            "visualization_query": parsed_task,
            "raw_result": viz_result,
            "result_evaluation": "Success" if viz_result else "Error"
        }
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}


def show_data_info():
    """Display information about the loaded data"""
    try:
        schema_result = get_schema()
        if "schema_description" in schema_result:
            schema = schema_result["schema_description"]
            print(f"\n📊 Dataset Information:")
            print(f"   Columns: {len(schema['columns'])}")
            print(f"   Available columns: {', '.join(schema['columns'])}")
            print(f"   Sample rows: {len(schema['sample'])}")
            
            # Show data types
            print(f"\n📋 Column Types:")
            for col, dtype in schema['dtypes'].items():
                print(f"   {col}: {dtype}")
            
            # Show sample data
            print(f"\n🔍 Sample Data (first 2 rows):")
            for i, sample in enumerate(schema['sample'][:2]):
                print(f"   Row {i+1}:")
                for key, value in sample.items():
                    print(f"     {key}: {value}")
                print()
        else:
            print("❌ Could not load dataset information")
    except Exception as e:
        print(f"❌ Error loading data info: {str(e)}")


def demo_queries():
    """Run demonstration queries to showcase the visualization capabilities."""
    
    demo_queries_list = [
        ("Show the distribution of vulnerabilities by criticality", "Shows how vulnerabilities are distributed across different severity levels"),
        ("Create a bar chart of vulnerabilities by app name", "Compares vulnerability counts across different applications"),
        ("Show me a pie chart of solution categories", "Displays the breakdown of solution types (patch, config, upgrade, etc.)"),
        ("Display the scan dates as a table", "Shows scan dates in tabular format"),
        ("Create a histogram of vulnerability criticality", "Shows frequency distribution of criticality levels"),
        ("Show apps with high criticality vulnerabilities", "Filters and displays high-severity vulnerabilities")
    ]
    
    print("=" * 70)
    print("🚀 DATA VISUALIZATION AGENT DEMO")
    print("=" * 70)
    
    show_data_info()
    
    print("=" * 70)
    print("🔍 RUNNING DEMO QUERIES")
    print("=" * 70)
    
    for i, (query, description) in enumerate(demo_queries_list, 1):
        print(f"\n{i}. 📝 Query: {query}")
        print(f"   📋 Purpose: {description}")
        print("   " + "-" * 40)
        
        result = run_visualization_test(query)
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Success: {result['summary']}")
            if "visualization_query" in result:
                vq = result["visualization_query"]
                print(f"   📊 Chart Type: {vq['chart_type']}")
                print(f"   📋 Columns: {', '.join(vq['columns']) if isinstance(vq['columns'], list) else vq['columns']}")
                if vq.get('aggregation'):
                    print(f"   📈 Aggregation: {vq['aggregation']}")
                if vq.get('group_by'):
                    print(f"   📦 Group By: {vq['group_by']}")


def interactive_mode():
    """Run in interactive mode for custom queries."""
    print("\n" + "=" * 70)
    print("💬 INTERACTIVE MODE")
    print("=" * 70)
    print("Enter natural language queries for data visualization.")
    print("Commands:")
    print("  🚪 'quit' or 'exit' - Exit the application")
    print("  🎯 'demo' - Run demo queries")
    print("  📊 'info' - Show dataset information")
    print("  📋 'help' - Show this help message")
    
    while True:
        try:
            user_input = input("\n🔍 > ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'demo':
                demo_queries()
                continue
            elif user_input.lower() == 'info':
                show_data_info()
                continue
            elif user_input.lower() == 'help':
                print("\n📖 Available Commands:")
                print("  🚪 quit, exit, q - Exit the application")
                print("  🎯 demo - Run demonstration queries")
                print("  📊 info - Show dataset information and schema")
                print("  📋 help - Show this help message")
                print("\n💡 Example queries:")
                print("  - Show me a bar chart of apps by criticality")
                print("  - Create a pie chart of solution categories")
                print("  - Display vulnerability counts by app")
                continue
            elif not user_input:
                continue
            
            result = run_visualization_test(user_input)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ {result['summary']}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error in interactive mode: {str(e)}", exc_info=True)
            print(f"❌ Unexpected error: {str(e)}")


def run():
    """Main entry point for the application."""
    print("🎯 Data Visualization Agent - Enhanced Standalone Mode")
    print("This app provides comprehensive local testing without ADK dependencies.")
    logger.info("Starting Data Visualization Agent")
    
    try:
        # Quick validation that data file exists
        import os
        data_path = "data/qualys_vulns_sample_200.csv"
        if not os.path.exists(data_path):
            error_msg = f"Data file not found at {data_path}"
            print(f"❌ Error: {error_msg}")
            print("Please ensure the CSV file exists before running the app.")
            logger.error(error_msg)
            return
        
        # Check if data can be loaded
        df = pd.read_csv(data_path)
        print(f"✅ Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Data loaded: {len(df)} rows, {len(df.columns)} columns")
        
        print("\n🎯 Choose mode:")
        print("  1️⃣  Demo mode (run pre-defined queries)")
        print("  2️⃣  Interactive mode (enter your own queries)")
        
        choice = input("\nEnter choice (1 or 2, default=1): ").strip()
        
        if choice == "2":
            interactive_mode()
        else:
            demo_queries()
            
    except Exception as e:
        error_msg = f"Startup error: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)


if __name__ == "__main__":
    run()