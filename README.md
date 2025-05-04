# Influencer Sponsorship Coordination Platform

A web application that connects influencers with sponsors for marketing campaigns, built with Flask.

## Features

- Multi-role user system (Admin, Influencer, Sponsor)
- Campaign creation and management
- Ad request workflow
- Admin dashboard with analytics
- User profile management
- Responsive design

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository
   ```
   git clone <repository-url>
   cd ICSP
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages
   ```
   pip install -r requirements.txt
   ```

4. Set up the database
   ```
   # The application will automatically create the database on first run
   ```

### Running the Application

1. Run the Flask application
   ```
   python run.py
   ```

2. Access the application in your browser
   ```
   http://127.0.0.1:5000
   ```

## Deployment

To deploy the application to a production environment:

1. Set DEBUG=False in config.py
2. Use a production WSGI server (like Gunicorn)
3. Set up a production database (PostgreSQL recommended)
4. Configure a web server (like Nginx) for serving the application

## License

This project is licensed under the MIT License - see the LICENSE file for details. 