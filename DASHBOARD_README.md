# Content Generation Dashboard

## Overview

This comprehensive dashboard provides a web-based interface for accessing and managing your content generation database. It offers multiple views for exploring sessions, analyzing data, and managing your content generation pipeline.

## Features

### 🏠 Overview Page
- Quick statistics and metrics
- Recent sessions summary
- System status at a glance

### 📊 Session Management
- Browse and select sessions
- View detailed session information
- Navigate to specific session data
- Session action buttons for quick access

### 🔍 Data Explorer
- Browse different data types:
  - Search Results
  - Twitter Results
  - Reviewer Outputs
  - Editor Outputs
- View raw API responses
- Detailed content exploration

### 📈 Analytics Dashboard
- Overall system analytics
- Session-specific analytics
- Twitter engagement analysis
- Content analysis (post lengths, etc.)
- Interactive charts and visualizations

### 🛠️ Database Tools
- Database information and statistics
- Maintenance operations (VACUUM, ANALYZE)
- Session deletion (with caution)
- Database optimization tools

### 📤 Export Functionality
- Export individual sessions or all data
- Multiple formats (JSON, CSV)
- Downloadable data packages
- Preview before download

## Installation

1. Install the required dependencies:
```bash
pip install -r dashboard_requirements.txt
```

2. Ensure your database is set up and accessible via the `database.py` module.

## Usage

### Running the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will be available at `http://localhost:8501`

### Navigation

Use the sidebar to navigate between different pages:
- **Overview**: Get a quick summary of your system
- **Sessions**: Manage and explore individual sessions
- **Data Explorer**: Deep dive into your data
- **Analytics**: View charts and statistics
- **Database Tools**: Maintain and optimize your database
- **Export**: Download your data

### Session Management

1. **Select a Session**: Use the dropdown to choose which session to work with
2. **View Details**: See session metadata and summary statistics
3. **Quick Actions**: Use the action buttons to navigate to specific views

### Data Exploration

1. **Choose a Session**: Select which session's data to explore
2. **Select Data Type**: Choose from search results, Twitter data, etc.
3. **Browse Content**: Expand items to see detailed information
4. **View Raw Data**: Access original API responses when available

### Analytics

1. **Overall Analytics**: Select "All Sessions" to see system-wide statistics
2. **Session Analytics**: Choose a specific session for detailed analysis
3. **Interactive Charts**: Use Plotly charts to explore data relationships
4. **Engagement Analysis**: Review Twitter engagement metrics

### Database Maintenance

1. **Monitor Size**: Check database file size and growth
2. **Vacuum Database**: Reclaim unused space
3. **Analyze Database**: Update query statistics
4. **Delete Sessions**: Remove unwanted sessions (use with caution)

### Data Export

1. **Choose Scope**: Export a single session or all data
2. **Select Format**: Choose JSON or CSV format
3. **Generate Export**: Create the export file
4. **Download**: Use the download button to save locally

## Security Notes

- The dashboard provides access to your entire database
- Session deletion is permanent and cannot be undone
- Database maintenance operations should be used carefully
- Consider access controls if deploying in a shared environment

## Troubleshooting

### Common Issues

1. **Database Not Found**: Ensure `cache_database.db` exists in the current directory
2. **Import Errors**: Install all dependencies from `dashboard_requirements.txt`
3. **No Data**: Run your content generation pipeline first to populate the database
4. **Slow Performance**: Use the database tools to vacuum and analyze

### Performance Tips

- Regular database maintenance improves performance
- Export large datasets in smaller chunks
- Use the session selector to focus on specific data sets
- Monitor database size and clean up old sessions when needed

## Dependencies

- `streamlit`: Web dashboard framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive charts and visualizations
- `sqlite3`: Database connectivity (included with Python)

## Integration

The dashboard integrates with your existing:
- `database.py`: Database handler and connection management
- `cache_database.db`: SQLite database file
- Content generation pipeline: Sessions and data

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure your database is properly initialized
4. Check the Streamlit logs for error messages 