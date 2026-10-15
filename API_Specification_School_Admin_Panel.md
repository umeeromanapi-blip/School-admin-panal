# API Specification — School Management Admin Panel

**Project:** School Management Admin Panel  
**Practical Work:** Practical Work 1  
**Version:** 1.0  
**Backend:** Django  
**Database:** SQLite  
**Interface:** HTML and CSS with Django templates

---

## 1. Purpose

This document defines the application routes and optional JSON API endpoints for the School Management Admin Panel.

The assignment requires a working web interface for Dashboard, Add Student, View Students, Edit Student, and Delete Student. The primary implementation can use Django views and HTML forms. A separate REST API is **not required** by the assignment unless the project is extended to use one.

## 2. Scope

The system manages student records containing:

- Student Name
- Admission Number
- Class
- Contact Number

The application must support Create, Read, Update, and Delete (CRUD) operations.

## 3. Architecture Decision

### Recommended for this practical

Use Django server-rendered pages, Django forms or ModelForms, Django ORM, and SQLite. Browser forms submit to Django views, and the views return HTML pages or redirects.

### Optional API extension

If a JSON API is desired, implement the endpoints in this document using Django views (or Django REST Framework if explicitly installed and configured). Do not add Django REST Framework only for the sake of this document unless the project needs it.

## 4. Student Data Model

Example JSON representation:

```json
{
  "id": 1,
  "student_name": "Ali Khan",
  "admission_number": "ADM-001",
  "student_class": "Class 8",
  "contact_number": "03001234567"
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | Integer | Generated | Primary key |
| `student_name` | String | Yes | Maximum 150 characters |
| `admission_number` | String | Yes | Unique; maximum 30 characters |
| `student_class` | String | Yes | Maximum 50 characters |
| `contact_number` | String | Yes | Maximum 20 characters; store as text to preserve leading zeros |

## 5. HTML Page Routes

These routes are suggested. If the existing project uses different routes, keep its actual route naming consistent and document it.

| Method | Endpoint | Purpose | Expected result |
|---|---|---|---|
| `GET` | `/` | Dashboard | HTML page with total student count |
| `GET` | `/students/` | View students | HTML table of student records |
| `GET` | `/students/add/` | Add form | Empty student form |
| `POST` | `/students/add/` | Create student | Validate and save; redirect on success |
| `GET` | `/students/<id>/edit/` | Edit form | Form populated with selected student |
| `POST` | `/students/<id>/edit/` | Update student | Validate and update; redirect on success |
| `GET` | `/students/<id>/delete/` | Delete confirmation | Confirmation page; no deletion occurs |
| `POST` | `/students/<id>/delete/` | Delete student | Delete selected record and redirect |

All POST forms must include Django's CSRF token. Deletion must never be performed through a GET request.

## 6. Optional JSON API Endpoints

These endpoints are optional and should be added only if a JSON API is required.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/students/` | Return all student records |
| `POST` | `/api/students/` | Create a student |
| `GET` | `/api/students/<id>/` | Return one student |
| `PUT` or `PATCH` | `/api/students/<id>/` | Update a student |
| `DELETE` | `/api/students/<id>/` | Delete a student |

### 6.1 List Students

**Request**

```http
GET /api/students/
Accept: application/json
```

**Successful response — `200 OK`**

```json
[
  {
    "id": 1,
    "student_name": "Ali Khan",
    "admission_number": "ADM-001",
    "student_class": "Class 8",
    "contact_number": "03001234567"
  }
]
```

If there are no records, return an empty array: `[]`.

### 6.2 Create Student

**Request**

```http
POST /api/students/
Content-Type: application/json
```

```json
{
  "student_name": "Ali Khan",
  "admission_number": "ADM-001",
  "student_class": "Class 8",
  "contact_number": "03001234567"
}
```

**Successful response — `201 Created`**

Return the created record, including its generated `id`.

### 6.3 Retrieve One Student

**Request**

```http
GET /api/students/1/
Accept: application/json
```

**Successful response — `200 OK`**

Return the selected student object. If the ID does not exist, return `404 Not Found`.

### 6.4 Update Student

**Request**

```http
PATCH /api/students/1/
Content-Type: application/json
```

```json
{
  "student_class": "Class 9",
  "contact_number": "03007654321"
}
```

**Successful response — `200 OK`**

Return the updated student object. `PATCH` changes only supplied fields; `PUT` may require the complete representation, depending on the implementation.

### 6.5 Delete Student

**Request**

```http
DELETE /api/students/1/
```

**Successful response**

Return `204 No Content` if following common REST conventions, or return `200 OK` with a confirmation message if that response style is chosen and documented. If the ID does not exist, return `404 Not Found`.

The normal HTML interface must still show a confirmation step before deletion.

## 7. Validation Rules

The server must enforce these rules for both HTML forms and optional API requests:

1. All four student fields are required.
2. `student_name` must not exceed 150 characters.
3. `admission_number` must not exceed 30 characters and must be unique.
4. `student_class` must not exceed 50 characters.
5. `contact_number` must not exceed 20 characters and should be stored as text.
6. Invalid data must not be saved.
7. A duplicate admission number must produce a clear validation error.

Example validation response for an optional JSON API:

**Status:** `400 Bad Request`

```json
{
  "errors": {
    "admission_number": [
      "A student with this admission number already exists."
    ]
  }
}
```

The exact JSON error format may vary depending on whether standard Django views or Django REST Framework is used. Document the actual format in the implementation.

## 8. HTTP Status Codes for the Optional API

| Status | Meaning |
|---|---|
| `200 OK` | Request succeeded |
| `201 Created` | Student was created |
| `204 No Content` | Student was deleted successfully with no response body |
| `400 Bad Request` | Submitted data is invalid |
| `404 Not Found` | Student ID or endpoint does not exist |
| `405 Method Not Allowed` | HTTP method is not supported |
| `500 Internal Server Error` | Unexpected server error; do not expose debug details to users |

## 9. Security Requirements

- Validate all data on the server.
- Use Django CSRF protection for browser-based POST forms.
- Do not perform destructive operations through GET requests.
- If a JSON API is added, define its authentication and authorization requirements before exposing it beyond local development.
- Do not expose detailed stack traces or secrets in production.
- Use fictional/sample student data during demonstrations.
- Keep Django `DEBUG` disabled in production.

## 10. API Testing Checklist

If the optional JSON API is implemented, verify:

- [ ] `GET /api/students/` returns a list.
- [ ] `POST /api/students/` creates a valid student.
- [ ] Missing required fields are rejected.
- [ ] Duplicate admission numbers are rejected.
- [ ] `GET /api/students/<id>/` returns the correct student.
- [ ] A nonexistent ID returns `404 Not Found`.
- [ ] `PATCH` or `PUT` updates the intended student.
- [ ] `DELETE` removes the intended student.
- [ ] Invalid input never changes the database.
- [ ] Authentication and CSRF behavior match the chosen implementation.

## 11. Instructions for Antigravity AI

Read this API Specification together with `School_Admin_Panel_SRS.docx`, `School_Admin_Panel_Software_Architecture_Design.docx`, and `README.md`.

First inspect the existing workspace. Implement the required Django HTML routes and CRUD behavior from the SRS. The assignment does not require a separate REST API, so do not add one unless it is useful or explicitly requested. If implementing the optional JSON API, follow the endpoint definitions and validation rules in this file, keep the existing HTML interface working, and document any differences in the actual routes or response formats.

Run available checks and test the CRUD operations where possible. Do not claim that endpoints have passed testing unless they have actually been verified.

---

## 12. Assignment Success Criteria

The practical work is successful when an administrator can add a student, view the saved record, update the record, and delete it when required. The application must use HTML/CSS for the interface, Django for backend functionality, and SQLite for storage.
