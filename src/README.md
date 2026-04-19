# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get active announcements (public)                                  |
| GET    | `/announcements/manage?teacher_username=<username>`              | Get all announcements (authenticated users only)                   |
| POST   | `/announcements?teacher_username=<username>`                     | Create announcement (expiration date required)                     |
| PUT    | `/announcements/{announcement_id}?teacher_username=<username>`   | Update announcement                                                 |
| DELETE | `/announcements/{announcement_id}?teacher_username=<username>`   | Delete announcement                                                 |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Data is persisted in MongoDB and initialized with sample activities, teacher users, and an example announcement.
