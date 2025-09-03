"""
Unit tests for the Data Visualization Agent
"""

import unittest
import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from standalone_viz import (
    get_schema, 
    interpret_query_with_schema, 
    execute_task_on_df, 
    run_dash_query,
    to_python_scalar
)


class TestDataVisualizationAgent(unittest.TestCase):
    """Test cases for the data visualization agent functionality"""

    def setUp(self):
        """Set up test data"""
        # Create a sample dataframe for testing
        self.test_data = pd.DataFrame({
            'app_name': ['App-A', 'App-B', 'App-A', 'App-C', 'App-B'],
            'criticality': ['High', 'Medium', 'High', 'Low', 'Critical'],
            'solution_category': ['Patch', 'Config', 'Patch', 'Upgrade', 'Patch'],
            'scan_date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'vulnerability_count': [5, 3, 8, 1, 12]
        })

    def test_get_schema(self):
        """Test schema extraction functionality"""
        schema_result = get_schema()
        self.assertIn('schema_description', schema_result)
        
        schema = schema_result['schema_description']
        self.assertIn('columns', schema)
        self.assertIn('dtypes', schema)
        self.assertIn('sample', schema)
        
        # Check that we have the expected columns
        expected_columns = ['app_id', 'app_name', 'vulnerability_id', 'vulnerability_name', 
                          'vulnerability_solution', 'solution_category', 'criticality', 'scan_date']
        for col in expected_columns:
            self.assertIn(col, schema['columns'])

    def test_to_python_scalar(self):
        """Test numpy scalar conversion"""
        import numpy as np
        
        # Test with numpy scalar
        np_scalar = np.int64(42)
        result = to_python_scalar(np_scalar)
        self.assertEqual(result, 42)
        self.assertIsInstance(result, int)
        
        # Test with regular Python value
        regular_value = "test"
        result = to_python_scalar(regular_value)
        self.assertEqual(result, "test")

    def test_interpret_query_bar_chart(self):
        """Test query interpretation for bar charts"""
        schema = {
            'columns': ['app_name', 'criticality', 'solution_category'],
            'dtypes': {'app_name': 'object', 'criticality': 'object', 'solution_category': 'object'}
        }
        
        query = "create a bar chart of apps by criticality"
        result = interpret_query_with_schema(query, schema)
        
        self.assertEqual(result['chart_type'], 'bar')
        # Should detect both app and criticality columns
        all_relevant_columns = result['columns'] + ([result.get('group_by')] if result.get('group_by') else [])
        self.assertTrue(any('app' in col.lower() for col in all_relevant_columns) or 
                       any('critical' in col.lower() for col in all_relevant_columns))

    def test_interpret_query_pie_chart(self):
        """Test query interpretation for pie charts"""
        schema = {
            'columns': ['app_name', 'criticality', 'solution_category'],
            'dtypes': {'app_name': 'object', 'criticality': 'object', 'solution_category': 'object'}
        }
        
        query = "show me a pie chart of solution categories"
        result = interpret_query_with_schema(query, schema)
        
        self.assertEqual(result['chart_type'], 'pie')
        self.assertIn('solution_category', result['columns'])

    def test_interpret_query_histogram(self):
        """Test query interpretation for histograms"""
        schema = {
            'columns': ['app_name', 'criticality', 'solution_category'],
            'dtypes': {'app_name': 'object', 'criticality': 'object', 'solution_category': 'object'}
        }
        
        query = "create a histogram of criticality distribution"
        result = interpret_query_with_schema(query, schema)
        
        self.assertEqual(result['chart_type'], 'histogram')
        self.assertIn('criticality', result['columns'])

    def test_interpret_query_table(self):
        """Test query interpretation for tables"""
        schema = {
            'columns': ['app_name', 'criticality', 'solution_category'],
            'dtypes': {'app_name': 'object', 'criticality': 'object', 'solution_category': 'object'}
        }
        
        query = "show me the raw data as a table"
        result = interpret_query_with_schema(query, schema)
        
        self.assertEqual(result['chart_type'], 'table')

    def test_interpret_query_aggregation_detection(self):
        """Test detection of aggregation keywords"""
        schema = {
            'columns': ['app_name', 'criticality'],
            'dtypes': {'app_name': 'object', 'criticality': 'object'}
        }
        
        # Test count aggregation
        query = "count the number of apps by criticality"
        result = interpret_query_with_schema(query, schema)
        self.assertEqual(result['aggregation'], 'count')
        
        # Test average aggregation
        query = "show average risk by app"
        result = interpret_query_with_schema(query, schema)
        self.assertEqual(result['aggregation'], 'average')

    def test_interpret_query_grouping_detection(self):
        """Test detection of grouping keywords"""
        schema = {
            'columns': ['app_name', 'criticality'],
            'dtypes': {'app_name': 'object', 'criticality': 'object'}
        }
        
        query = "show vulnerabilities by app_name"
        result = interpret_query_with_schema(query, schema)
        self.assertEqual(result['group_by'], 'app_name')

    def test_run_dash_query_success(self):
        """Test successful query execution"""
        test_query = {
            "query": "show me a table of scan dates"
        }
        
        result = run_dash_query(test_query)
        
        # Should not have error
        self.assertNotIn('error', result)
        
        # Should have expected fields
        self.assertIn('visualization_type', result)
        self.assertIn('query_info', result)

    def test_run_dash_query_invalid_input(self):
        """Test query execution with invalid input"""
        # Test with None input
        result = run_dash_query(None)
        self.assertIn('error', result)
        
        # Test with empty input
        result = run_dash_query({})
        self.assertIn('error', result)

    def test_chart_type_detection_edge_cases(self):
        """Test edge cases in chart type detection"""
        schema = {
            'columns': ['app_name', 'criticality'],
            'dtypes': {'app_name': 'object', 'criticality': 'object'}
        }
        
        # Test with multiple chart type keywords
        query = "create a bar chart and pie chart of apps"
        result = interpret_query_with_schema(query, schema)
        # Should pick the first one found
        self.assertIn(result['chart_type'], ['bar', 'pie'])
        
        # Test with no chart type keywords
        query = "apps and their criticality levels"
        result = interpret_query_with_schema(query, schema)
        # Should default to table
        self.assertEqual(result['chart_type'], 'table')

    def test_column_semantic_matching(self):
        """Test semantic matching of column names"""
        schema = {
            'columns': ['app_name', 'vulnerability_id', 'criticality', 'solution_category'],
            'dtypes': {'app_name': 'object', 'vulnerability_id': 'object', 
                      'criticality': 'object', 'solution_category': 'object'}
        }
        
        # Test app-related queries
        query = "show applications with high severity"
        result = interpret_query_with_schema(query, schema)
        self.assertTrue(any('app' in col.lower() for col in result['columns']) or 
                       any('app' in str(result.get('group_by', '')).lower() for col in result['columns']))
        
        # Test vulnerability-related queries
        query = "display vulnerabilities by category"
        result = interpret_query_with_schema(query, schema)
        self.assertTrue(len(result['columns']) > 0)


class TestVisualizationIntegration(unittest.TestCase):
    """Integration tests for the complete visualization pipeline"""

    def test_complete_pipeline_bar_chart(self):
        """Test complete pipeline for bar chart generation"""
        query = {"query": "create a bar chart of solution categories"}
        result = run_dash_query(query)
        
        if 'error' not in result:
            self.assertIn('visualization_type', result)
            self.assertIn('query_info', result)
            query_info = result['query_info']
            self.assertEqual(query_info['chart_type'], 'bar')

    def test_complete_pipeline_pie_chart(self):
        """Test complete pipeline for pie chart generation"""
        query = {"query": "show me a pie chart of criticality levels"}
        result = run_dash_query(query)
        
        if 'error' not in result:
            self.assertIn('visualization_type', result)
            self.assertIn('query_info', result)
            query_info = result['query_info']
            self.assertEqual(query_info['chart_type'], 'pie')

    def test_complete_pipeline_table(self):
        """Test complete pipeline for table generation"""
        query = {"query": "display the app names as a table"}
        result = run_dash_query(query)
        
        if 'error' not in result:
            self.assertIn('visualization_type', result)
            self.assertEqual(result['visualization_type'], 'table')
            self.assertIn('data', result)
            self.assertIsInstance(result['data'], list)


if __name__ == '__main__':
    # Set up test environment
    print("Running Data Visualization Agent Tests...")
    print("=" * 50)
    
    # Check if data file exists
    if not os.path.exists('data/qualys_vulns_sample_200.csv'):
        print("⚠️  Warning: Test data file not found. Some tests may fail.")
    
    # Run tests
    unittest.main(verbosity=2)