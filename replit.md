# Exelio

## Overview

Exelio is a Flask-based web application that enables users to upload Excel files (.xls/.xlsx), parse and store the data in a SQL database, and generate interactive visualizations with AI-powered insights. The platform features user authentication, file upload management, data processing capabilities, AI analysis using Gemini, and a dashboard for viewing upload history and analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Flask Framework**: Core web application framework with modular blueprint structure
- **SQLAlchemy ORM**: Database abstraction layer with declarative model definitions
- **Flask-Login**: Session-based user authentication and authorization system
- **File Processing Pipeline**: Excel files are processed using pandas/openpyxl and stored as normalized data entries

### Database Design
- **User Management**: User accounts with role-based access (user/admin) and password hashing
- **Upload Tracking**: File metadata storage including original filename, upload time, file size, and parsing status
- **Data Storage**: Normalized data entries storing parsed Excel content as JSON with sheet and row indexing
- **Relationship Structure**: One-to-many relationships from users to uploads, and uploads to data entries with cascade deletion

### Frontend Architecture
- **Server-Side Rendering**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Interactive Visualizations**: Chart.js integration for dynamic chart generation
- **Progressive Enhancement**: Drag-and-drop file uploads with progress indicators
- **Responsive Design**: Mobile-first approach with dark theme support

### Security Implementation
- **Authentication**: Password hashing using Werkzeug security utilities
- **Session Management**: Flask-Login handles user sessions and login state
- **File Validation**: Whitelist approach for allowed file extensions and size limits
- **SQL Injection Protection**: SQLAlchemy ORM provides parameterized query protection

### Data Processing Flow
- **Upload Validation**: File type and size validation before processing
- **Excel Parsing**: Multi-sheet Excel files processed using pandas with error handling
- **Data Normalization**: Row-by-row data storage with JSON serialization for flexible schema
- **Error Recovery**: Parse errors are logged and stored for debugging purposes

## External Dependencies

### Core Libraries
- **Flask**: Web framework (v2.x)
- **SQLAlchemy**: Database ORM
- **pandas**: Excel file parsing and data manipulation
- **openpyxl/xlrd**: Excel file format support
- **Werkzeug**: Security utilities and file handling

### Frontend Assets
- **Bootstrap 5**: CSS framework via CDN
- **Chart.js**: Visualization library via CDN
- **Font Awesome**: Icon library via CDN

### Database
- **SQLite**: Default development database with upgrade path to PostgreSQL
- **Connection Pooling**: Configured for production with pool recycling and health checks

### File Storage
- **Local Filesystem**: Upload directory for file storage
- **File Size Limits**: 16MB maximum upload size configured

### Optional Integrations
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies
- **Logging**: Python logging configured for debugging and monitoring