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
4. **Status Tracking**: Three-tier status system based on read state and completion
5. **Admin Reply**: Admin can respond to requests with text replies
6. **Request Deletion**: Admin can delete requests with confirmation
7. **Map Integration**: Leaflet.js with OpenStreetMap for viewing request locations
8. **PWA**: Installable on mobile devices

## Request Statuses (Tajik)
Effective status is determined by admin_read_at and status fields:
- **Нав (New)**: Protocol not yet read by admin (admin_read_at is NULL)
- **Дар тафтиш (Under Review)**: Protocol read but not completed (admin_read_at is set, status != 'completed')
- **Иҷро шуд (Completed)**: Protocol marked as completed (status == 'completed')

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

## Request Numbering
- **Registration Number (reg_number)**: Auto-generated as NAZ-YYYY-NNNN (e.g., NAZ-2025-0001)
- **Document Number (document_number)**: Auto-generated as DOC-YYYY-NNNN (e.g., DOC-2025-0001)
- Both numbers are generated atomically with retry mechanism to prevent duplicates

## Admin Panel Structure
- **Панели Админ (Admin Home)**: Shows worker cards with new protocol counters (Нав)
- **Протоколҳо (Protocols)**: All requests table with search/filter (formerly Dashboard)
- **Омор (Statistics)**: Analytics with charts and download options (Word/Excel)
- **Харита (Map)**: Geographic view of all requests
- **Мавзӯъҳо (Topics)**: Manage request topics
- **Корбарон (Workers)**: Manage users

## Statistics Export
- Download statistics in Word (.docx) or Excel (.xlsx) format
- Available from both general statistics page and individual worker pages
- Includes request counts, completion rates, and topic breakdowns

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
- December 2025: Added clickable user names in admin panel to view all requests by specific user
- December 2025: New SVG favicon with shield/camera design matching brand identity
- December 2025: Updated PWA icons with new shield/camera design for mobile install
- December 2025: Added ProxyFix middleware for proper URL handling with custom domains
- December 2025: Added live search with autocomplete on admin dashboard (searches by reg_number, document_number, username, topic, comment)
- December 2025: Document number (DOC-YYYY-NNNN) is now auto-generated alongside registration number
- December 2025: Added file upload support for WEBP images
- December 2025: Redesigned admin homepage with worker cards showing unread protocol counters
- December 2025: Moved protocols table to dedicated "Протоколҳо" page
- December 2025: Added admin_read_at field for tracking read status of requests
- December 2025: Added statistics download feature in Word and Excel formats
- December 2025: Worker statistics download available from user requests page
- December 2025: Unified three-tier status system: Нав (new/unread) → Дар тафтиш (read/under review) → Иҷро шуд (completed)
- December 2025: Added quick complete button (checkmark) on protocols and user requests tables
- December 2025: Added avatar upload feature for workers with preview in form and display in worker cards
