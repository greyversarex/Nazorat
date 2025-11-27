# Systemi Darkhostho - Request Management System

## Overview
A Progressive Web Application (PWA) for managing citizen requests/tickets. Built with Python Flask, SQLAlchemy, and Bootstrap 5. The interface is fully localized in Tajik language.

## Project Structure
```
├── app.py              # Main Flask application factory
├── models.py           # SQLAlchemy database models
├── routes/             # Blueprint routes
│   ├── __init__.py
│   ├── main.py         # Main routes (index, manifest, sw)
│   ├── auth.py         # Authentication routes
│   ├── admin.py        # Admin dashboard routes
│   └── user.py         # User dashboard routes
├── templates/          # Jinja2 templates
│   ├── base.html       # Base template with Bootstrap 5
│   ├── auth/           # Login/Register templates
│   ├── admin/          # Admin dashboard templates
│   └── user/           # User dashboard templates
├── static/
│   ├── css/style.css   # Custom styles
│   ├── js/app.js       # Main JavaScript
│   ├── js/sw.js        # Service Worker for PWA
│   ├── manifest.json   # PWA manifest
│   ├── icons/          # PWA icons
│   └── uploads/        # User uploaded media (excluded from git)
├── instance/           # SQLite database location (excluded from git)
└── .gitignore          # Git ignore file
```

## User Roles
- **Admin**: Can manage topics, view all requests, change request statuses, view users
- **User**: Can submit requests with location and media, view own requests

## Default Admin Account
- Username: `admin`
- Password: `admin123`

## Key Features
1. **Authentication**: Flask-Login with bcrypt password hashing
2. **Topic Management**: Admin can CRUD topics
3. **Request Submission**: Users submit requests with:
   - Topic selection
   - Geolocation (via browser Geolocation API)
   - Comments
   - Photo/Video uploads
4. **Status Tracking**: New → In Progress → Completed/Rejected
5. **Map Integration**: Leaflet.js with OpenStreetMap for viewing request locations
6. **PWA**: Installable on mobile devices

## Request Statuses (Tajik)
- `new` = Нав
- `in_progress` = Дар баррасӣ
- `completed` = Иҷро шуд
- `rejected` = Рад шуд

## Running the Application
```bash
python app.py
```
The app runs on port 5000.

## Deployment Notes
- `.gitignore` excludes `instance/` (database) and `static/uploads/` (media)
- This ensures production data is not overwritten when pushing code updates

## Recent Changes
- November 2024: Initial implementation with all core features
