# Incident Management System

This is a RESTful API-based incident management system developed using Python and Django REST Framework (DRF) for the backend and Postgresql as the database. The frontend is developed using React.js (or any other language you prefer). This system allows users to register, log in, and create incidents, with functionalities like auto-filling location based on the pin code and ensuring unique incident IDs.

## Features

- User Registration and Login
- Forgot Password functionality
- Incident Management (Create, View, Edit)
- Auto-generate unique Incident IDs
- Search functionality for incidents using Incident ID
- Role-based access: Users can only view and edit their incidents
- Non-editable closed incidents

## Technologies Used

- **Backend:** Python 3.8+, Django, Django REST Framework
- **Database:** PostgreSQL
- **Frontend:** Postman


## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Postman

### Installation

2. Create and activate the virtual environment:

   - python -m venv venv
   - source venv/bin/activate  # On Windows use `venv\Scripts\activate`


3. Install the required packages:

   - pip install -r requirements.txt
   - Write the valid credentials in .env file

4. Run database migrations:

   - python manage.py makemigrations
   - python manage.py migrate

5. Access the application:

   - Open your web browser and navigate to http://127.0.0.1:8000/.



