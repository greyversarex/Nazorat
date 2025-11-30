# Nazorat - Request Management System

## Overview
A Progressive Web Application (PWA) for managing citizen requests/tickets. Built with Python Flask, SQLAlchemy, PostgreSQL, and Bootstrap 5. The interface is fully localized in Tajik language.

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
4. **Status Tracking**: Under Review → Completed (two statuses only)
5. **Admin Reply**: Admin can respond to requests with text replies
6. **Request Deletion**: Admin can delete requests with confirmation
7. **Map Integration**: Leaflet.js with OpenStreetMap for viewing request locations
8. **PWA**: Installable on mobile devices

## Request Statuses (Tajik)
- `under_review` = Дар тафтиш (Under review)
- `completed` = Иҷро шуд (Completed)

## Running the Application
```bash
python app.py
```
The app runs on port 5000.

## Database
- Uses PostgreSQL (Replit's built-in database) for reliable data persistence
- Connection via DATABASE_URL environment variable
- Tables: users, topics, requests

## Deployment Notes
- `.gitignore` excludes `static/uploads/` (media files)
- Database is managed by Replit PostgreSQL and persists automatically

## Security Features
1. **CSRF Protection**: Flask-WTF CSRFProtect on all POST forms
2. **Open Redirect Prevention**: Login route validates redirect URLs to prevent attacks
3. **Password Hashing**: bcrypt for secure password storage
4. **Session Management**: Flask-Login with secure session handling

## Recent Changes
- November 2024: Initial implementation with all core features
- November 2025: Added CSRF protection and open redirect vulnerability fix
- November 2025: Removed open registration; user creation now admin-only via admin panel
- November 2025: Simplified statuses to only "Дар тафтиш" (under review) and "Иҷро шуд" (completed)
- November 2025: Added admin reply functionality with timestamp
- November 2025: Added request deletion with confirmation modal
- November 2025: Dashboard rows are now clickable to view request details
- November 2025: Action buttons changed to Reply and Delete only
- November 2025: Unified cyan/teal (#0891b2) color scheme across entire interface
- November 2025: Mobile-responsive tables (card layout on small screens)
- November 2025: Migrated from SQLite to PostgreSQL for reliable data persistence
- November 2025: Added Statistics (Омор) page with interactive charts, date filtering, and visual analytics
