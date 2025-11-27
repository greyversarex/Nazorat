# Systemi Darkhostho - Request Management System

## Overview
A Progressive Web Application (PWA) for managing citizen requests/tickets. Built with Python Flask, SQLAlchemy, and Bootstrap 5. The interface is fully localized in Tajik language.

## Project Structure
```
├── app.py              # Main Flask application factory
├── extensions.py       # Flask extensions (db, bcrypt, login_manager, csrf)
├── models.py           # SQLAlchemy database models
├── routes/             # Blueprint routes
│   ├── __init__.py
│   ├── main.py         # Main routes (index, manifest, sw)
│   ├── auth.py         # Authentication routes (with open redirect protection)
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
- **Admin**: Can manage topics, create/delete users, view all requests, change request statuses
- **User**: Can submit requests with location and media, view own requests

Note: Open registration is disabled. Only admins can create new users from the admin panel.

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

## Security Features
1. **CSRF Protection**: Flask-WTF CSRFProtect on all POST forms
2. **Open Redirect Prevention**: Login route validates redirect URLs to prevent attacks
3. **Password Hashing**: bcrypt for secure password storage
4. **Session Management**: Flask-Login with secure session handling

## Recent Changes
- November 2024: Initial implementation with all core features
- November 2025: Added CSRF protection and open redirect vulnerability fix
- November 2025: Removed open registration; user creation now admin-only via admin panel
