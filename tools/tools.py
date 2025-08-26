# tools.py
import pandas as pd
from google.adk.tools import FunctionTool
from typing import Dict, Any

def read_csv_data(file_path: str) -> Dict[str, Any]:
    """
    Reads a CSV file and returns the data as a dictionary.

    Args:
        file_path: The absolute path to the CSV file.

    Returns:
        A dictionary containing the data from the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        return {
            "status": "success",
            "data": df.to_dict('records') # 'records' format is good for LLMs
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"File not found at: {file_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred while reading the CSV: {e}"
        }