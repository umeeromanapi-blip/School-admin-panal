# School Management Admin Panel — Enterprise Campus ERP

A full-featured, web-based School Management Admin Panel and Enterprise Campus ERP built for **Practical Work 1**. The application allows school administrators to manage student records, faculty, academic curriculum, fees, attendance, timetables, library circulation, campus transport, and student hostels through an ultra-premium glassmorphism user interface and robust Django backend.

---

## Project Overview

- **Backend:** Python 3.12, Django 6.1.2
- **Database:** SQLite (`db.sqlite3`) with ACID transactions and schema migrations
- **Frontend:** Vanilla CSS3 Design System with Glassmorphism, CSS Custom Properties, Responsive Grids, Google Fonts (`Inter`), and inline SVG iconography
- **Testing:** 116 automated unit and integration tests across 5 Epics (100% pass rate)
- **Live Local URL:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 5 Epics Architecture & Feature Scope

### 🎓 Epic 1: Core Student Records & System Foundation (`students`)
- **Executive Dashboard:** Institutional metrics, total student count, quick actions, operational status indicators.
- **Student CRUD:** Add, View, Edit, and Delete student records with confirmation pages.
- **Validation Rules:** Required field enforcement, case-insensitive whitespace trimming, automatic uppercase admission number normalization, text-based phone numbers preserving leading zeros.
- **Optional REST API:** Complete JSON REST endpoints (`/api/students/` and `/api/students/<id>/`) supporting `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.

### 👨‍🏫 Epic 2: Faculty, Fees, Attendance & Reports (`teachers`, `fees`, `attendance`)
- **Faculty Directory:** Teacher profiles, employee IDs, subject specializations, qualifications, and salaries.
- **Fee Management:** Invoicing, fee categories (Tuition, Admission, Sports, Lab), payment status tracking (`Paid`, `Pending`, `Partial`), and downloadable receipt printouts.
- **Attendance Register:** Daily attendance marking (`Present`, `Absent`, `Late`, `Excused`) with aggregate attendance percentages.
- **Analytics & Reports:** Visual financial breakdown and student demographics.

### 📚 Epic 3: Academics, Exams, Grading & Notice Board (`exams`, `announcements`)
- **Academic Subjects:** Departmental subject catalog with course codes and credit hours.
- **Examinations:** Term exam scheduling, dates, and maximum marks.
- **Marks & Report Cards:** Automated grade calculation (A+, A, B, C, D, F) with printable student report cards.
- **Campus Notice Board:** School-wide announcements with priority levels (`High`, `Normal`, `Urgent`).

### ⏰ Epic 4: Bell Schedules, Timetable & Library Catalog (`timetable`, `library`)
- **Bell Schedule & Periods:** Configurable school periods with start/end time validation and break detection.
- **Timetable Matrix:** Weekly schedule planner with automated teacher conflict and classroom clash detection.
- **Library Catalog:** Book inventory management with ISBN, category, shelf location, and copy tracking.
- **Circulation & Overdue Fines:** Book checkout, return workflows, and automated overdue fine calculations.

### 🚌 Epic 5: Campus Fleet Logistics & Residential Services (`transport`, `hostel`)
- **Transport Fleet & Routes:** School buses and vans tracking, driver profiles, route itineraries, and monthly fares.
- **Transport Passes:** Active boarding pass allocations for daily commuting students.
- **Hostel Dormitories:** Hall residency management (Boys, Girls, Faculty), room capacities, and monthly rent.
- **Resident Allocations:** Student bed check-in with automated capacity constraint enforcement (zero-overbooking guarantee).

---

## Actual Project Structure

```text
school admin panal/
├── manage.py
├── db.sqlite3
├── README.md
├── School_Admin_Panel_SRS.docx
├── School_Admin_Panel_Software_Architecture_Design.docx
├── API_Specification_School_Admin_Panel.md
├── school_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── students/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── student_list.html
│   │   ├── student_detail.html
│   │   ├── student_form.html
│   │   └── student_confirm_delete.html
│   ├── teachers/
│   ├── fees/
│   ├── attendance/
│   ├── exams/
│   ├── announcements/
│   ├── timetable/
│   ├── library/
│   ├── transport/
│   └── hostel/
├── students/               # Epic 1: Students & Core System
├── teachers/               # Epic 2: Faculty Management
├── fees/                   # Epic 2: Fee Invoicing & Receipts
├── attendance/             # Epic 2: Daily Attendance
├── exams/                  # Epic 3: Exams, Subjects & Marks
├── announcements/          # Epic 3: Notice Board Alerts
├── timetable/              # Epic 4: Periods & Timetable Matrix
├── library/                # Epic 4: Books & Circulation
├── transport/              # Epic 5: Fleet & Transport Routes
└── hostel/                 # Epic 5: Hostels, Rooms & Allocations
```

---

## Setup & Running Locally

### 1. Requirements
- Python 3.10+
- Django 5.x / 6.x

### 2. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed Sample Data (Optional)
To populate the database with comprehensive demonstration records:
```bash
python manage.py seed_epic2     # Teachers, Fees, Attendance
python manage.py seed_epic3     # Subjects, Exams, Marks, Notices
python manage.py seed_epic4     # Periods, Timetable, Books, Loans
python manage.py seed_epic5     # Transport Vehicles, Routes, Hostels, Rooms
```

### 4. Run Automated Test Suite
To execute all 116 automated unit and integration tests across all 5 Epics:
```bash
python manage.py test --verbosity=2
```

To run a specific Epic test suite:
```bash
python manage.py test students.tests          # Epic 1 (21 tests)
python manage.py test students.tests_epic2    # Epic 2 (37 tests)
python manage.py test students.tests_epic3    # Epic 3 (22 tests)
python manage.py test students.tests_epic4    # Epic 4 (15 tests)
python manage.py test students.tests_epic5    # Epic 5 (21 tests)
```

### 5. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in any modern web browser.

---

## Core Routes & Endpoints

### HTML Web Application
| Section | Route | Method | Description |
|---|---|---|---|
| Dashboard | `/` | GET | Executive overview with real-time student count |
| Students List | `/students/` | GET | Paginated student records table with search |
| Add Student | `/students/add/` | GET, POST | Student registration form with CSRF protection |
| Edit Student | `/students/<id>/edit/` | GET, POST | Update existing student record |
| Delete Student | `/students/<id>/delete/` | GET, POST | Confirmation page (GET) and permanent removal (POST) |
| Teachers | `/teachers/` | GET | Faculty directory |
| Fees | `/fees/` | GET | Fee invoices, receipts, and collection status |
| Attendance | `/attendance/` | GET | Daily attendance register |
| Examinations | `/exams/` | GET | Scheduled exams and report cards |
| Notice Board | `/announcements/` | GET | Campus alerts and notifications |
| Timetable | `/timetable/` | GET | Weekly class timetable grid |
| Library | `/library/` | GET | Books catalog and circulation manager |
| Transport Fleet | `/transport/` | GET | Fleet vehicles, bus routes, and boarding passes |
| Hostels | `/hostel/` | GET | Dormitory halls, rooms, and boarder allocations |

### Optional JSON REST API (`students`)
| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/api/students/` | List all student records | `200 OK` |
| `POST` | `/api/students/` | Create student from JSON body | `201 Created` |
| `GET` | `/api/students/<id>/` | Retrieve specific student | `200 OK` / `404 Not Found` |
| `PATCH` / `PUT` | `/api/students/<id>/` | Update student details | `200 OK` / `400 Bad Request` |
| `DELETE` | `/api/students/<id>/` | Remove student record | `204 No Content` |

---

## Testing & Verification Checklist

- [x] Django system check passes with 0 issues (`python manage.py check`).
- [x] All database migrations are cleanly applied with zero discrepancies.
- [x] The Dashboard opens and displays the exact, real-time student count.
- [x] A valid student can be registered via form and saved to SQLite.
- [x] Required fields reject empty submissions and whitespace.
- [x] Duplicate admission numbers are rejected with clear error feedback.
- [x] Existing student records can be updated via edit form.
- [x] Delete operations strictly require confirmation and use `POST` (safe from accidental GET deletions).
- [x] Cancelling deletion keeps records intact.
- [x] Confirming deletion removes records permanently.
- [x] Student records persist in `db.sqlite3` across development server restarts.
- [x] All navigation links, buttons, and sub-module routes return HTTP `200 OK`.
- [x] All 116 automated unit and integration tests pass with 100% success rate.
