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
                    # Only rename if truly unnamed (pandas auto-generated names)
                    if col.startswith('Unnamed:') or col == '' or col == 'nan' or col == 'None':
                        # Try to use first row as header if it contains text
                        if len(df) > 0:
                            first_row_val = df.iloc[0, i]
                            if pd.notna(first_row_val) and str(first_row_val).strip():
                                cleaned_columns.append(str(first_row_val).strip())
                            else:
                                cleaned_columns.append(f"Column_{i+1}")
                        else:
                            cleaned_columns.append(f"Column_{i+1}")
                    else:
                        # Keep the original column name
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
        
        logging.info(f"Generating {chart_type} chart with X={x_axis}, Y={y_axis}")
        
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
                
                # Check if columns exist (handle case variations)
                # Try exact match first
                x_col = x_axis if x_axis in row_data else None
                y_col = y_axis if y_axis in row_data else None
                
                # If not found, try case-insensitive match
                if not x_col:
                    for key in row_data.keys():
                        if key.lower() == x_axis.lower():
                            x_col = key
                            break
                if not y_col:
                    for key in row_data.keys():
                        if key.lower() == y_axis.lower():
                            y_col = key
                            break
                
                if not x_col:
                    missing_columns.add(x_axis)
                    continue
                if not y_col:
                    missing_columns.add(y_axis)
                    continue
                    
                x_val = row_data[x_col]
                y_val = row_data[y_col]
                
                # Skip None values
                if x_val is not None and y_val is not None:
                    # For pie charts, x can be text, y must be numeric
                    if chart_type == 'pie':
                        try:
                            y_val = float(str(y_val).replace(',', ''))  # Remove commas from numbers
                            data_rows.append({'x': str(x_val), 'y': y_val})
                        except (ValueError, TypeError):
                            non_numeric_count += 1
                            continue
                    else:
                        # For other charts, try to convert y_val to numeric
                        try:
                            y_val = float(str(y_val).replace(',', ''))  # Remove commas from numbers
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
                raise ValueError(f"The Y-axis column '{y_axis}' does not contain numeric data suitable for charting")
            else:
                raise ValueError(f"No valid data found for columns {x_axis} and {y_axis}")
        
        # Create DataFrame for processing
        df = pd.DataFrame(data_rows)
        
        if chart_type == 'pie':
            # For pie charts, group by x and sum y values
            grouped = df.groupby('x')['y'].sum().reset_index()
            grouped = grouped.sort_values('y', ascending=False)  # Sort by value
            
            # Smart categorization: Group small slices into "Others"
            total = grouped['y'].sum()
            threshold = 0.03  # 3% threshold
            
            main_data = []
            others_value = 0
            
            for _, row in grouped.iterrows():
                percentage = (row['y'] / total) if total > 0 else 0
                if percentage >= threshold or len(main_data) < 5:  # Keep at least top 5
                    main_data.append({'label': str(row['x']), 'value': row['y']})
                else:
                    others_value += row['y']
            
            # Add "Others" category if needed
            if others_value > 0:
                main_data.append({'label': 'Others', 'value': others_value})
            
            labels = [item['label'] for item in main_data]
            values = [item['value'] for item in main_data]
            
            # Calculate percentages for display
            percentages = [(v / total * 100) if total > 0 else 0 for v in values]
            
            # Modern color palette
            modern_colors = [
                '#6366F1', '#8B5CF6', '#EC4899', '#EF4444', '#F97316',
                '#F59E0B', '#10B981', '#06B6D4', '#3B82F6', '#6B7280',
                '#84CC16', '#F43F5E', '#8B5A2B', '#6366F1', '#14B8A6'
            ]
            
            # Create gradient colors (darker shades for borders)
            border_colors = [color.replace('#', '#aa') if not color.startswith('#aa') else color for color in modern_colors]
            
            return {
                'type': 'pie',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': values,
                        'backgroundColor': modern_colors[:len(values)],
                        'borderColor': border_colors[:len(values)],
                        'borderWidth': 2,
                        'hoverBorderWidth': 3,
                        'hoverBorderColor': '#fff',
                        'percentages': percentages
                    }]
                },
                'total_records': len(df),
                'x_axis': x_axis,
                'y_axis': y_axis
            }
        
        elif chart_type in ['bar', 'line']:
            # Group and aggregate data
            if chart_type == 'bar':
                # For bar charts, group by x and sum y values
                grouped = df.groupby('x')['y'].sum().reset_index()
                grouped = grouped.sort_values('y', ascending=False)  # Sort by value
            else:
                # For line charts, keep original order
                grouped = df.drop_duplicates(subset=['x']).sort_values('x')
            
            labels = grouped['x'].tolist()
            values = grouped['y'].tolist()
            
            # Modern colors for consistency
            primary_color = '#6366F1'  # Modern indigo
            
            return {
                'type': chart_type,
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': y_axis,
                        'data': values,
                        'backgroundColor': primary_color if chart_type == 'bar' else 'rgba(99, 102, 241, 0.1)',
                        'borderColor': primary_color,
                        'borderWidth': 2,
                        'fill': chart_type == 'line',
                        'tension': 0.3 if chart_type == 'line' else 0,  # Smooth line curves
                        'pointBackgroundColor': primary_color,
                        'pointBorderColor': '#fff',
                        'pointBorderWidth': 2,
                        'pointRadius': 4,
                        'pointHoverRadius': 6
                    }]
                },
                'total_records': len(df),
                'x_axis': x_axis,
                'y_axis': y_axis
            }
        
        elif chart_type == 'scatter':
            return {
                'type': 'scatter',
                'data': {
                    'datasets': [{
                        'label': f'{y_axis} vs {x_axis}',
                        'data': [{'x': row['x'], 'y': row['y']} for row in data_rows],
                        'backgroundColor': 'rgba(236, 72, 153, 0.6)',  # Modern pink with transparency
                        'borderColor': '#EC4899',
                        'borderWidth': 1,
                        'pointRadius': 5,
                        'pointHoverRadius': 7,
                        'pointHoverBackgroundColor': '#EC4899',
                        'pointHoverBorderColor': '#fff',
                        'pointHoverBorderWidth': 2
                    }]
                },
                'total_records': len(df),
                'x_axis': x_axis,
                'y_axis': y_axis
            }
        
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
            
    except Exception as e:
        logging.error(f"Chart generation error: {e}")
        raise e

def auto_select_columns(upload_id, chart_type):
    """Automatically select best columns for the given chart type"""
    try:
        # Get data entries
        data_entries = DataEntry.query.filter_by(upload_id=upload_id).limit(100).all()
        
        if not data_entries:
            return None, None
        
        # Parse first few rows to understand data structure
        data_rows = []
        columns_info = {}
        
        for entry in data_entries[:20]:  # Sample first 20 rows
            try:
                row_data = json.loads(entry.data_json)
                data_rows.append(row_data)
                
                # Analyze column types
                for col, value in row_data.items():
                    if col not in columns_info:
                        columns_info[col] = {'numeric': 0, 'text': 0, 'total': 0, 'sample_values': []}
                    
                    columns_info[col]['total'] += 1
                    if value is not None and str(value).strip() != '':
                        try:
                            # Try to convert to float, handling commas in numbers
                            float(str(value).replace(',', ''))
                            columns_info[col]['numeric'] += 1
                        except (ValueError, TypeError):
                            columns_info[col]['text'] += 1
                        
                        if len(columns_info[col]['sample_values']) < 5:
                            columns_info[col]['sample_values'].append(str(value))
            except json.JSONDecodeError:
                continue
        
        # Identify numeric and text columns
        numeric_columns = []
        text_columns = []
        all_columns = []
        
        for col, info in columns_info.items():
            # Skip columns that are mostly empty
            if info['total'] > 0 and (info['numeric'] > 0 or info['text'] > 0):
                all_columns.append(col)
                # Check if it's mostly numeric (more numeric than text values)
                if info['numeric'] > info['text']:
                    numeric_columns.append(col)
                elif info['text'] > 0:
                    text_columns.append(col)
        
        # Log column analysis
        logging.info(f"Column analysis: All={all_columns}, Numeric={numeric_columns}, Text={text_columns}")
        
        # Select columns based on chart type
        x_axis = None
        y_axis = None
        
        if chart_type == 'pie':
            # For pie charts, need a category and a value
            # Filter out mostly empty unnamed columns
            valid_text_cols = [col for col in text_columns if not col.startswith('Unnamed:') or columns_info[col]['text'] > 2]
            valid_numeric_cols = [col for col in numeric_columns if not col.startswith('Unnamed:') or columns_info[col]['numeric'] > 2]
            
            # If no valid columns, use all columns
            if not valid_text_cols:
                valid_text_cols = text_columns
            if not valid_numeric_cols:
                valid_numeric_cols = numeric_columns
            
            # First try text column for categories and numeric for values
            if valid_text_cols and valid_numeric_cols:
                x_axis = valid_text_cols[0]  # Category
                y_axis = valid_numeric_cols[0]  # Value
            # If only numeric columns exist, use them
            elif len(valid_numeric_cols) >= 2:
                x_axis = valid_numeric_cols[0]
                y_axis = valid_numeric_cols[1]
            # Use any available columns with data
            elif len(all_columns) >= 2:
                # Pick columns with most data
                sorted_cols = sorted(all_columns, key=lambda c: columns_info[c]['total'], reverse=True)
                x_axis = sorted_cols[0]
                y_axis = sorted_cols[1] if len(sorted_cols) > 1 else sorted_cols[0]
            # Last resort - use any column
            elif len(all_columns) >= 1:
                x_axis = all_columns[0]
                y_axis = all_columns[0]
        elif chart_type == 'bar':
            # For bar charts, similar to pie
            if text_columns and numeric_columns:
                x_axis = text_columns[0]  # Category
                y_axis = numeric_columns[0]  # Value
            elif len(numeric_columns) >= 2:
                x_axis = numeric_columns[0]
                y_axis = numeric_columns[1]
        elif chart_type == 'line':
            # For line charts, prefer numeric for both or text for x and numeric for y
            if len(numeric_columns) >= 2:
                x_axis = numeric_columns[0]
                y_axis = numeric_columns[1]
            elif text_columns and numeric_columns:
                x_axis = text_columns[0]
                y_axis = numeric_columns[0]
        elif chart_type == 'scatter':
            # For scatter plots, need two numeric columns
            if len(numeric_columns) >= 2:
                x_axis = numeric_columns[0]
                y_axis = numeric_columns[1]
        
        return x_axis, y_axis
        
    except Exception as e:
        logging.error(f"Auto column selection error: {e}")
        return None, None

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
