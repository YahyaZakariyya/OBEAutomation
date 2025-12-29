# OBE Automation API Documentation

## Overview

This API provides RESTful endpoints for the OBE (Outcome-Based Education) Automation system. All endpoints require authentication and return JSON responses.

**Base URL:** `/api/`

**Authentication:** Session-based authentication (Django sessions)

**Pagination:** All list endpoints support pagination with 50 items per page

**Filtering & Search:** Most endpoints support search and filtering via query parameters

---

## Table of Contents

- [Programs API](#programs-api)
- [Users API](#users-api)
- [Courses API](#courses-api)
- [Sections API](#sections-api)
- [Assessments API](#assessments-api)
- [Questions API](#questions-api)
- [Student Scores API](#student-scores-api)
- [CLOs API](#clos-api)
- [PLOs API](#plos-api)
- [PLO-CLO Mappings API](#plo-clo-mappings-api)
- [Dashboard APIs](#dashboard-apis)
- [Common Parameters](#common-parameters)
- [Error Handling](#error-handling)

---

## Programs API

### List Programs
```
GET /api/programs/
```

**Query Parameters:**
- `search`: Search by program title or abbreviation
- `type`: Filter by program type (UG, GR, PG)
- `ordering`: Sort by field (e.g., `program_abbreviation`, `-program_title`)
- `page`: Page number for pagination

**Response:**
```json
{
  "count": 10,
  "next": "http://example.com/api/programs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "program_title": "Computer Science",
      "program_abbreviation": "CS",
      "program_type": "UG",
      "program_incharge_name": "Dr. John Doe"
    }
  ]
}
```

### Get Program Details
```
GET /api/programs/{id}/
```

**Response:**
```json
{
  "id": 1,
  "program_title": "Computer Science",
  "program_abbreviation": "CS",
  "program_type": "UG",
  "program_incharge": {
    "id": 5,
    "username": "john.doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "faculty",
    "full_name": "John Doe"
  },
  "program_incharge_id": 5
}
```

### Create Program
```
POST /api/programs/
Content-Type: application/json

{
  "program_title": "Software Engineering",
  "program_abbreviation": "SE",
  "program_type": "UG",
  "program_incharge_id": 5
}
```

### Update Program
```
PUT /api/programs/{id}/
Content-Type: application/json

{
  "program_title": "Software Engineering",
  "program_abbreviation": "SE",
  "program_type": "UG",
  "program_incharge_id": 5
}
```

### Delete Program
```
DELETE /api/programs/{id}/
```

### Program Custom Actions

#### Get Courses for Program
```
GET /api/programs/{id}/courses/
```

#### Get Sections for Program
```
GET /api/programs/{id}/sections/
```

#### Get PLOs for Program
```
GET /api/programs/{id}/plos/
```

---

## Users API

### List Users
```
GET /api/users/
```

**Query Parameters:**
- `search`: Search by username, first name, or last name
- `role`: Filter by role (admin, faculty, student)
- `view_all`: For faculty, set to `true` to see all users
- `ordering`: Sort by field

**Role-based filtering:**
- Students can only see themselves
- Faculty can see students in their sections
- Admins can see all users

**Response:**
```json
{
  "count": 100,
  "next": "http://example.com/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "student1",
      "first_name": "John",
      "last_name": "Smith",
      "email": "john@example.com",
      "role": "student",
      "full_name": "John Smith"
    }
  ]
}
```

### Get Current User
```
GET /api/users/me/
```

Returns the authenticated user's profile.

### Get User Sections
```
GET /api/users/{id}/sections/
```

Returns enrolled sections for students, taught sections for faculty.

---

## Courses API

### List Courses
```
GET /api/courses/
```

**Query Parameters:**
- `search`: Search by course ID or name
- `program_id`: Filter by program
- `credit_hours`: Filter by credit hours
- `ordering`: Sort by field

**Response:**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "course_id": "CS101",
      "name": "Introduction to Programming",
      "credit_hours": 3
    }
  ]
}
```

### Get Course Details
```
GET /api/courses/{id}/
```

**Response:**
```json
{
  "id": 1,
  "course_id": "CS101",
  "name": "Introduction to Programming",
  "credit_hours": 3,
  "programs": [
    {
      "id": 1,
      "program_title": "Computer Science",
      "program_abbreviation": "CS",
      "program_type": "UG"
    }
  ],
  "clos_count": 5,
  "sections_count": 3
}
```

### Course Custom Actions

#### Get CLOs for Course
```
GET /api/courses/{id}/clos/
```

#### Get Sections for Course
```
GET /api/courses/{id}/sections/
```

#### Get Programs for Course
```
GET /api/courses/{id}/programs/
```

---

## Sections API

### List Sections
```
GET /api/sections/
```

**Query Parameters:**
- `course_id`: Filter by course
- `program_id`: Filter by program
- `faculty_id`: Filter by faculty
- `semester`: Filter by semester (1-10)
- `batch`: Filter by batch (Spring, Summer, Fall)
- `year`: Filter by year
- `status`: Filter by status (in_progress, complete)
- `view_all`: For faculty, set to `true` to see all sections

**Role-based filtering:**
- Students see only their enrolled sections
- Faculty see their taught sections (unless `view_all=true`)

**Response:**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "course": {
        "id": 1,
        "course_id": "CS101",
        "name": "Introduction to Programming",
        "credit_hours": 3
      },
      "program": {
        "id": 1,
        "program_abbreviation": "CS",
        "program_type": "UG"
      },
      "faculty": {
        "id": 5,
        "username": "john.doe",
        "full_name": "Dr. John Doe"
      },
      "semester": "1",
      "section": "A",
      "batch": "Fall",
      "year": "2024",
      "status": "in_progress",
      "section_display": "Introduction to Programming - 1"
    }
  ]
}
```

### Section Custom Actions

#### Get Students in Section
```
GET /api/sections/{id}/students/
```

#### Add Student to Section
```
POST /api/sections/{id}/add_student/
Content-Type: application/json

{
  "student_id": 10
}
```

#### Remove Student from Section
```
POST /api/sections/{id}/remove_student/
Content-Type: application/json

{
  "student_id": 10
}
```

#### Get Assessments for Section
```
GET /api/sections/{id}/assessments/
```

#### Get Assessment Breakdown for Section
```
GET /api/sections/{id}/assessment_breakdown/
```

---

## Assessments API

### List Assessments
```
GET /api/assessments/
```

**Query Parameters:**
- `section_id`: Filter by section
- `type`: Filter by type (quiz, assignment, midterm, final, lab, project)
- `ordering`: Sort by field

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "title": "Midterm Exam",
      "section_display": "CS101 - Fall 2024",
      "date": "2024-10-15",
      "type": "midterm",
      "type_display": "Midterm",
      "weightage": 30.0,
      "total_marks": 100.0
    }
  ]
}
```

### Assessment Custom Actions

#### Get Questions for Assessment
```
GET /api/assessments/{id}/questions/
```

#### Get Assessment Statistics
```
GET /api/assessments/{id}/statistics/
```

**Response:**
```json
{
  "total_marks": 100,
  "questions_count": 10,
  "students_count": 30,
  "average_score": 75.5,
  "average_percentage": 75.5,
  "student_scores": [
    {
      "student_id": 1,
      "student_name": "John Smith",
      "score": 85,
      "percentage": 85.0
    }
  ]
}
```

---

## Questions API

### List Questions
```
GET /api/questions/
```

**Query Parameters:**
- `assessment_id`: Filter by assessment
- `clo_id`: Filter by CLO

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "assessment_display": "Midterm Exam - CS101",
      "marks": 10.0,
      "clos": [
        {
          "id": 1,
          "CLO": 1,
          "heading": "Understand basic programming concepts"
        }
      ]
    }
  ]
}
```

### Question Custom Actions

#### Get Scores for Question
```
GET /api/questions/{id}/scores/
```

#### Get Question Statistics
```
GET /api/questions/{id}/statistics/
```

---

## Student Scores API

### List Student Scores
```
GET /api/student-scores/
```

**Query Parameters:**
- `student_id`: Filter by student
- `question_id`: Filter by question
- `assessment_id`: Filter by assessment
- `section_id`: Filter by section

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "student": {
        "id": 10,
        "username": "student1",
        "full_name": "John Smith"
      },
      "question_marks": 10.0,
      "marks_obtained": 8.5
    }
  ]
}
```

### Bulk Create/Update Scores
```
POST /api/student-scores/bulk_create/
Content-Type: application/json

{
  "scores": [
    {
      "student_id": 1,
      "question_id": 10,
      "marks_obtained": 8.5
    },
    {
      "student_id": 2,
      "question_id": 10,
      "marks_obtained": 9.0
    }
  ]
}
```

**Response:**
```json
{
  "created": [...],
  "updated": [...],
  "errors": []
}
```

---

## CLOs API

### List CLOs
```
GET /api/clos/
```

**Query Parameters:**
- `course_id`: Filter by course

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "course_name": "Introduction to Programming",
      "CLO": 1,
      "heading": "Understand programming basics",
      "description": "Students will be able to...",
      "weightage": 20.0
    }
  ]
}
```

### CLO Custom Actions

#### Get PLO Mappings for CLO
```
GET /api/clos/{id}/plo_mappings/
```

#### Get Questions for CLO
```
GET /api/clos/{id}/questions/
```

---

## PLOs API

### List PLOs
```
GET /api/plos/
```

**Query Parameters:**
- `program_id`: Filter by program

**Response:**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "program_name": "CS",
      "PLO": 1,
      "heading": "Problem Solving",
      "description": "Graduates will be able to...",
      "weightage": 15.0
    }
  ]
}
```

### PLO Custom Actions

#### Get CLO Mappings for PLO
```
GET /api/plos/{id}/clo_mappings/
```

---

## PLO-CLO Mappings API

### List Mappings
```
GET /api/plo-clo-mappings/
```

**Query Parameters:**
- `program_id`: Filter by program
- `course_id`: Filter by course
- `plo_id`: Filter by PLO
- `clo_id`: Filter by CLO

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "program_name": "CS",
      "course_name": "Introduction to Programming",
      "plo_number": 1,
      "clo_number": 1,
      "weightage": 80.0
    }
  ]
}
```

---

## Dashboard APIs

### Admin Dashboard
```
GET /api/dashboards/admin/
```

Returns comprehensive statistics for administrators.

### Student Dashboard
```
GET /api/dashboards/student/
```

Returns student-specific data including enrolled sections and performance.

### Faculty Dashboard
```
GET /api/dashboards/faculty/
```

Returns faculty-specific data including taught sections and student performance.

---

## Common Parameters

### Pagination
All list endpoints support pagination:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50)

### Searching
Use the `search` parameter to search across relevant fields:
```
GET /api/courses/?search=programming
```

### Ordering
Use the `ordering` parameter to sort results:
```
GET /api/courses/?ordering=course_id      # Ascending
GET /api/courses/?ordering=-course_id     # Descending
```

### Filtering
Most endpoints support filtering via query parameters. See individual endpoint documentation for available filters.

---

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful GET, PUT, PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Error message here"
}
```

Or for validation errors:
```json
{
  "field_name": [
    "Error message for this field"
  ]
}
```

---

## Legacy API Endpoints

For backward compatibility, legacy endpoints are available under `/api/legacy/`:

- `/api/legacy/sections/`
- `/api/legacy/student/section/<section_id>/final_result/`
- `/api/legacy/faculty/section/<section_id>/final_result/`
- `/api/legacy/assessment-marks/`
- `/api/legacy/student-score/`
- `/api/legacy/courses/<program_id>/`
- `/api/legacy/get-course-id/`
- `/api/legacy/results/`
- `/api/legacy/clos/<course_id>/`
- `/api/legacy/faculty/section/<section_id>/clo_result/`
- `/api/legacy/student/section/<section_id>/clo_result/`

**Note:** These endpoints will be deprecated in future versions. Please migrate to the new API structure.

---

## Authentication

All API endpoints require authentication. The API uses Django session authentication.

To authenticate:
1. Log in through the Django admin interface or login page
2. Your session cookie will be used for subsequent API requests
3. Include the CSRF token in POST, PUT, PATCH, DELETE requests

**CSRF Token:**
```javascript
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Include in fetch requests
fetch('/api/programs/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data)
});
```

---

## Examples

### Complete CRUD Example

```javascript
// List programs
const response = await fetch('/api/programs/');
const data = await response.json();
console.log(data.results);

// Get single program
const program = await fetch('/api/programs/1/');
const programData = await program.json();

// Create program
const newProgram = await fetch('/api/programs/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        program_title: 'Data Science',
        program_abbreviation: 'DS',
        program_type: 'UG',
        program_incharge_id: 5
    })
});

// Update program
const updatedProgram = await fetch('/api/programs/1/', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        program_title: 'Data Science (Updated)',
        program_abbreviation: 'DS',
        program_type: 'UG',
        program_incharge_id: 5
    })
});

// Delete program
await fetch('/api/programs/1/', {
    method: 'DELETE',
    headers: {
        'X-CSRFToken': getCookie('csrftoken')
    }
});
```

---

## Browser API Explorer

Django REST Framework provides a browsable API interface. Visit any endpoint in your browser while logged in to explore the API interactively:

Example: `http://localhost:8000/api/programs/`

This interface allows you to:
- Browse available endpoints
- Test API calls directly from the browser
- View response formats
- Access documentation
