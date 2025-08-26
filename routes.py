import os
import json
import pandas as pd
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import logging

from app import app, db
from models import User, Upload, DataEntry, Chart
from utils import allowed_file, parse_excel_file, generate_chart_data
from ai_insights import analyze_data_with_ai, generate_chart_recommendations, get_data_quality_insights

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with upload history"""
    uploads = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.upload_time.desc()).all()
    
    # Calculate statistics
    total_uploads = len(uploads)
    successful_uploads = len([u for u in uploads if u.parsed])
    total_size = sum(u.file_size or 0 for u in uploads)
    
    return render_template('dashboard.html', 
                         uploads=uploads,
                         total_uploads=total_uploads,
                         successful_uploads=successful_uploads,
                         total_size=total_size)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """File upload page"""
    if request.method == 'POST':
        try:
            # Check if file is present
            if 'file' not in request.files:
                flash('No file selected.', 'danger')
                return render_template('upload.html')
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No file selected.', 'danger')
                return render_template('upload.html')
            
            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload .xls or .xlsx files only.', 'danger')
                return render_template('upload.html')
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            file.save(filepath)
            file_size = os.path.getsize(filepath)
            
            # Create upload record
            upload = Upload(
                user_id=current_user.id,
                filename=unique_filename,
                original_filename=filename,
                file_size=file_size
            )
            
            db.session.add(upload)
            db.session.commit()
            
            # Parse Excel file
            try:
                success, message = parse_excel_file(filepath, upload.id)
                
                if success:
                    upload.parsed = True
                    flash('File uploaded and parsed successfully!', 'success')
                else:
                    upload.parse_error = message
                    flash(f'File uploaded but parsing failed: {message}', 'warning')
                
                db.session.commit()
                return redirect(url_for('view_data', upload_id=upload.id))
                
            except Exception as e:
                upload.parse_error = str(e)
                db.session.commit()
                logging.error(f"Parsing error: {e}")
                flash('File uploaded but parsing failed. Please check the file format.', 'danger')
                
        except RequestEntityTooLarge:
            flash('File too large. Maximum size is 16MB.', 'danger')
        except Exception as e:
            logging.error(f"Upload error: {e}")
            flash('Upload failed. Please try again.', 'danger')
    
    return render_template('upload.html')

@app.route('/data/<int:upload_id>')
@login_required
def view_data(upload_id):
    """View uploaded data and create visualizations"""
    upload = Upload.query.filter_by(id=upload_id, user_id=current_user.id).first()
    
    if not upload:
        flash('Upload not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if not upload.parsed:
        flash('This file has not been parsed successfully.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Get data entries
    data_entries = DataEntry.query.filter_by(upload_id=upload_id).limit(100).all()
    
    if not data_entries:
        flash('No data found in this upload.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Parse first few rows for preview
    preview_data = []
    columns = []
    
    for entry in data_entries[:10]:  # Show first 10 rows
        try:
            row_data = json.loads(entry.data_json)
            preview_data.append(row_data)
            if not columns and isinstance(row_data, dict):
                columns = list(row_data.keys())
        except json.JSONDecodeError:
            continue
    
    # Generate AI chart recommendations
    chart_recommendations = generate_chart_recommendations(columns, preview_data)
    
    return render_template('visualize.html', 
                         upload=upload,
                         preview_data=preview_data,
                         columns=columns,
                         chart_recommendations=chart_recommendations)

@app.route('/api/chart-data/<int:upload_id>')
@login_required
def api_chart_data(upload_id):
    """API endpoint to get chart data"""
    upload = Upload.query.filter_by(id=upload_id, user_id=current_user.id).first()
    
    if not upload or not upload.parsed:
        return jsonify({'error': 'Upload not found or not parsed'}), 404
    
    chart_type = request.args.get('chart_type', 'bar')
    auto = request.args.get('auto') == 'true'
    
    if auto:
        # Automatically select best columns
        from utils import auto_select_columns
        x_axis, y_axis = auto_select_columns(upload_id, chart_type)
        
        if not x_axis or not y_axis:
            return jsonify({'error': 'Unable to automatically select columns. Data may not have suitable columns for this chart type.'}), 400
    else:
        x_axis = request.args.get('x_axis')
        y_axis = request.args.get('y_axis')
        
        if not x_axis or not y_axis:
            return jsonify({'error': 'X and Y axis parameters required'}), 400
    
    try:
        chart_data = generate_chart_data(upload_id, x_axis, y_axis, chart_type)
        
        if auto:
            # Return both the chart data and selected columns
            return jsonify({
                'chart_data': chart_data,
                'x_axis': x_axis,
                'y_axis': y_axis
            })
        else:
            return jsonify(chart_data)
    except Exception as e:
        logging.error(f"Chart data error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/save-chart', methods=['POST'])
@login_required
def save_chart():
    """Save chart configuration"""
    upload_id = request.form.get('upload_id')
    chart_type = request.form.get('chart_type')
    x_axis = request.form.get('x_axis')
    y_axis = request.form.get('y_axis')
    title = request.form.get('title', '')
    
    if not all([upload_id, chart_type, x_axis, y_axis]):
        flash('Missing required chart parameters.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify upload belongs to user
    upload = Upload.query.filter_by(id=upload_id, user_id=current_user.id).first()
    if not upload:
        flash('Invalid upload.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Save chart
    chart = Chart(
        upload_id=upload_id,
        user_id=current_user.id,
        chart_type=chart_type,
        x_axis=x_axis,
        y_axis=y_axis,
        title=title
    )
    
    try:
        db.session.add(chart)
        db.session.commit()
        flash('Chart saved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Chart save error: {e}")
        flash('Failed to save chart.', 'danger')
    
    return redirect(url_for('view_data', upload_id=upload_id))

@app.route('/delete-upload/<int:upload_id>', methods=['POST'])
@login_required
def delete_upload(upload_id):
    """Delete an upload and its data"""
    upload = Upload.query.filter_by(id=upload_id, user_id=current_user.id).first()
    
    if not upload:
        flash('Upload not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Delete physical file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete from database (cascade will handle related records)
        db.session.delete(upload)
        db.session.commit()
        
        flash('Upload deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete error: {e}")
        flash('Failed to delete upload.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/ai-insights/<int:upload_id>')
@login_required
def ai_insights(upload_id):
    """Show AI-powered insights for uploaded data"""
    upload = Upload.query.filter_by(id=upload_id, user_id=current_user.id).first()
    
    if not upload:
        flash('Upload not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if not upload.parsed:
        flash('This file has not been parsed successfully.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Get all data entries for AI analysis
    data_entries = DataEntry.query.filter_by(upload_id=upload_id).all()
    
    if not data_entries:
        flash('No data found in this upload.', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        # Get AI insights
        ai_analysis = analyze_data_with_ai(data_entries, upload.original_filename)
        
        # Get data quality insights
        quality_report = get_data_quality_insights(data_entries)
        
        return render_template('ai_insights.html',
                             upload=upload,
                             ai_analysis=ai_analysis,
                             quality_report=quality_report)
                             
    except Exception as e:
        logging.error(f"AI insights error: {e}")
        flash('Unable to generate AI insights at this time.', 'warning')
        return redirect(url_for('view_data', upload_id=upload_id))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash('File too large. Maximum size is 16MB.', 'danger')
    return redirect(url_for('upload_file'))
