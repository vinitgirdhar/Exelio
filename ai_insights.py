import os
import json
import logging
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict, Any

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

class DataInsight(BaseModel):
    title: str
    description: str
    insight_type: str  # 'trend', 'pattern', 'anomaly', 'summary'
    confidence: float

class DataSummary(BaseModel):
    total_rows: int
    columns_analyzed: List[str]
    key_insights: List[DataInsight]
    recommendations: List[str]

def analyze_data_with_ai(data_entries, upload_filename: str) -> DataSummary:
    """
    Analyze uploaded data using Gemini AI to provide intelligent insights
    """
    try:
        # Convert data entries to DataFrame for analysis
        data_rows = []
        for entry in data_entries:
            try:
                row_data = json.loads(entry.data_json)
                data_rows.append(row_data)
            except json.JSONDecodeError:
                continue
        
        if not data_rows:
            raise ValueError("No valid data found for AI analysis")
        
        df = pd.DataFrame(data_rows)
        
        # Prepare data summary for AI analysis
        data_summary = {
            "filename": upload_filename,
            "total_rows": len(df),
            "columns": list(df.columns),
            "data_types": {col: str(df[col].dtype) for col in df.columns},
            "sample_data": df.head(5).to_dict('records'),
            "basic_stats": {}
        }
        
        # Add basic statistics for numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            stats = df[col].describe()
            data_summary["basic_stats"][col] = {
                "mean": float(stats['mean']) if not pd.isna(stats['mean']) else None,
                "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                "std": float(stats['std']) if not pd.isna(stats['std']) else None,
                "min": float(stats['min']) if not pd.isna(stats['min']) else None,
                "max": float(stats['max']) if not pd.isna(stats['max']) else None
            }
        
        # Create AI prompt for analysis
        system_prompt = """
        You are an expert data analyst. Analyze the provided Excel data and provide intelligent insights.
        Focus on:
        1. Key trends and patterns in the data
        2. Interesting correlations or relationships
        3. Potential anomalies or outliers
        4. Business recommendations based on the data
        5. Suggested visualizations that would be most effective
        
        Respond with actionable insights that would help a business user understand their data better.
        """
        
        user_prompt = f"""
        Please analyze this Excel data and provide insights:
        
        File: {upload_filename}
        Total Rows: {data_summary['total_rows']}
        Columns: {', '.join(data_summary['columns'])}
        
        Data Types: {json.dumps(data_summary['data_types'], indent=2)}
        
        Sample Data (first 5 rows):
        {json.dumps(data_summary['sample_data'], indent=2)}
        
        Basic Statistics for Numeric Columns:
        {json.dumps(data_summary['basic_stats'], indent=2)}
        
        Please provide insights in JSON format with this structure:
        {{
            "total_rows": {data_summary['total_rows']},
            "columns_analyzed": {json.dumps(data_summary['columns'])},
            "key_insights": [
                {{
                    "title": "Insight Title",
                    "description": "Detailed description of the insight",
                    "insight_type": "trend|pattern|anomaly|summary",
                    "confidence": 0.85
                }}
            ],
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2"
            ]
        }}
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=DataSummary,
            ),
        )
        
        if response.text:
            analysis_result = json.loads(response.text)
            return DataSummary(**analysis_result)
        else:
            raise ValueError("Empty response from AI model")
            
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        # Return fallback analysis
        return DataSummary(
            total_rows=len(data_entries),
            columns_analyzed=[],
            key_insights=[
                DataInsight(
                    title="Analysis Error",
                    description=f"Unable to perform AI analysis: {str(e)}",
                    insight_type="summary",
                    confidence=0.0
                )
            ],
            recommendations=["Please check your data format and try again."]
        )

def generate_chart_recommendations(columns: List[str], sample_data: List[Dict]) -> List[Dict[str, str]]:
    """
    Use AI to recommend the best chart types for the data
    """
    try:
        system_prompt = """
        You are a data visualization expert. Based on the column names and sample data provided,
        recommend the most effective chart types and axis combinations.
        Consider data types, relationships, and visualization best practices.
        """
        
        user_prompt = f"""
        Based on these columns and sample data, recommend the best chart configurations:
        
        Columns: {', '.join(columns)}
        Sample Data: {json.dumps(sample_data[:3], indent=2)}
        
        Please suggest 3-4 effective chart configurations in JSON format:
        [
            {{
                "chart_type": "bar|line|scatter|pie",
                "x_axis": "column_name",
                "y_axis": "column_name", 
                "title": "Suggested Chart Title",
                "reasoning": "Why this visualization is effective"
            }}
        ]
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            ),
        )
        
        if response.text:
            return json.loads(response.text)
        else:
            return []
            
    except Exception as e:
        logging.error(f"Chart recommendation error: {e}")
        return []

def get_data_quality_insights(data_entries) -> Dict[str, Any]:
    """
    Analyze data quality and provide insights
    """
    try:
        data_rows = []
        for entry in data_entries:
            try:
                row_data = json.loads(entry.data_json)
                data_rows.append(row_data)
            except json.JSONDecodeError:
                continue
        
        if not data_rows:
            return {"error": "No valid data found"}
        
        df = pd.DataFrame(data_rows)
        
        quality_report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_data": {},
            "data_types": {},
            "unique_values": {},
            "quality_score": 0.0
        }
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_percentage = (missing_count / len(df)) * 100
            
            quality_report["missing_data"][col] = {
                "count": int(missing_count),
                "percentage": round(missing_percentage, 2)
            }
            
            quality_report["data_types"][col] = str(df[col].dtype)
            quality_report["unique_values"][col] = int(df[col].nunique())
        
        # Calculate overall quality score
        total_missing = sum(info["percentage"] for info in quality_report["missing_data"].values())
        avg_missing = total_missing / len(df.columns) if len(df.columns) > 0 else 0
        quality_report["quality_score"] = max(0, 100 - avg_missing)
        
        return quality_report
        
    except Exception as e:
        logging.error(f"Data quality analysis error: {e}")
        return {"error": str(e)}