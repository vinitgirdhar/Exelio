import os
import json
import pandas as pd
import logging
from app import db
from models import DataEntry

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_excel_file(filepath, upload_id):
    """Parse Excel file and store data in database"""
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(filepath)
        total_rows = 0
        
        for sheet_name in excel_file.sheet_names:
            try:
                # Read sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Skip empty sheets
                if df.empty:
                    continue
                
                # Clean column names and handle unnamed columns
                df.columns = df.columns.astype(str)
                cleaned_columns = []
                for i, col in enumerate(df.columns):
                    col = col.strip()
                    if col.startswith('Unnamed:') or col == '' or col == 'nan':
                        cleaned_columns.append(f"Column_{i+1}")
                    else:
                        cleaned_columns.append(col)
                df.columns = cleaned_columns
                
                # Convert to records and store
                for index, row in df.iterrows():
                    # Convert row to dictionary, handling NaN values
                    row_dict = {}
                    for col, value in row.items():
                        if pd.isna(value):
                            row_dict[col] = None
                        elif isinstance(value, (pd.Timestamp, pd.Timestamp)):
                            row_dict[col] = value.isoformat()
                        else:
                            row_dict[col] = str(value)
                    
                    # Create data entry
                    data_entry = DataEntry(
                        upload_id=upload_id,
                        sheet_name=sheet_name,
                        row_index=index,
                        data_json=json.dumps(row_dict)
                    )
                    db.session.add(data_entry)
                    total_rows += 1
                
            except Exception as sheet_error:
                logging.error(f"Error processing sheet {sheet_name}: {sheet_error}")
                continue
        
        db.session.commit()
        
        if total_rows == 0:
            return False, "No valid data found in any sheets"
        
        return True, f"Successfully parsed {total_rows} rows from {len(excel_file.sheet_names)} sheets"
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Excel parsing error: {e}")
        return False, f"Failed to parse Excel file: {str(e)}"

def generate_chart_data(upload_id, x_axis, y_axis, chart_type):
    """Generate chart data for visualization"""
    try:
        # Validate input columns
        if not x_axis or not y_axis:
            raise ValueError("Please select both X and Y axis columns")
            
        # Check for invalid column names (removed since we're now handling Column_ names)
        # Allow Column_ names but warn about them
        if x_axis.startswith('Column_') or y_axis.startswith('Column_'):
            pass  # Allow renamed columns
        
        # Get data entries
        data_entries = DataEntry.query.filter_by(upload_id=upload_id).all()
        
        if not data_entries:
            raise ValueError("No data found for this upload")
        
        # Parse data
        data_rows = []
        missing_columns = set()
        non_numeric_count = 0
        
        for entry in data_entries:
            try:
                row_data = json.loads(entry.data_json)
                
                # Check if columns exist
                if x_axis not in row_data:
                    missing_columns.add(x_axis)
                    continue
                if y_axis not in row_data:
                    missing_columns.add(y_axis)
                    continue
                    
                x_val = row_data[x_axis]
                y_val = row_data[y_axis]
                
                # Skip None values
                if x_val is not None and y_val is not None:
                    # Try to convert y_val to numeric
                    try:
                        y_val = float(y_val)
                    except (ValueError, TypeError):
                        non_numeric_count += 1
                        continue
                    
                    data_rows.append({'x': str(x_val), 'y': y_val})
            except json.JSONDecodeError:
                continue
        
        if missing_columns:
            raise ValueError(f"Column(s) not found: {', '.join(missing_columns)}")
            
        if not data_rows:
            if non_numeric_count > 0:
                raise ValueError(f"The Y-axis column '{y_axis}' does not contain numeric data")
            else:
                raise ValueError(f"No valid data found for the selected columns")
        
        # Create DataFrame for processing
        df = pd.DataFrame(data_rows)
        
        if chart_type == 'pie':
            # For pie charts, group by x and sum y values
            grouped = df.groupby('x')['y'].sum().reset_index()
            labels = grouped['x'].tolist()
            values = grouped['y'].tolist()
            
            return {
                'type': 'pie',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': values,
                        'backgroundColor': [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                        ]
                    }]
                }
            }
        
        elif chart_type in ['bar', 'line']:
            # Group and aggregate data
            if chart_type == 'bar':
                # For bar charts, group by x and sum y values
                grouped = df.groupby('x')['y'].sum().reset_index()
            else:
                # For line charts, keep original order
                grouped = df.drop_duplicates(subset=['x']).sort_values('x')
            
            labels = grouped['x'].tolist()
            values = grouped['y'].tolist()
            
            return {
                'type': chart_type,
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': y_axis,
                        'data': values,
                        'backgroundColor': '#36A2EB' if chart_type == 'bar' else 'transparent',
                        'borderColor': '#36A2EB',
                        'borderWidth': 2,
                        'fill': chart_type == 'line'
                    }]
                }
            }
        
        elif chart_type == 'scatter':
            return {
                'type': 'scatter',
                'data': {
                    'datasets': [{
                        'label': f'{y_axis} vs {x_axis}',
                        'data': [{'x': row['x'], 'y': row['y']} for row in data_rows],
                        'backgroundColor': '#FF6384',
                        'borderColor': '#FF6384'
                    }]
                }
            }
        
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
            
    except Exception as e:
        logging.error(f"Chart generation error: {e}")
        raise e

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

# Add the format_file_size function to Jinja2 global functions
from app import app
app.jinja_env.globals.update(format_file_size=format_file_size)
