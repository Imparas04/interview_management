# Recruitment & Interview Management System

A full-stack recruitment platform that takes a candidate from resume upload
all the way to selection — resume parsing, ATS scoring, department
recommendation, application pipeline tracking, and interview scheduling,
with dedicated dashboards for Admins, HR, Interviewers, and Candidates.

## About

Hiring teams juggle resumes, spreadsheets, and email threads across the
whole recruitment cycle. This project brings that into one system: a
candidate uploads a resume, the platform parses it and scores it against a
job's requirements (ATS-style), HR moves the application through a defined
pipeline, interviews get scheduled with automatic conflict checks, and
interviewers submit structured feedback — all visible in real time from
role-specific dashboards.

## Features

- **Role-based access** — Admin, HR, Interviewer, and Candidate each get a
  dedicated dashboard and permission set.
- **Resume parsing** — PDF/DOCX upload with automatic text extraction and
  skill detection.
- **ATS scoring engine** — weighted match across skills, experience,
  education, projects, certifications, and keywords.
- **Department recommendation** — suggests the best-fit department for a
  candidate based on their resume.
- **Job management** — post openings with weighted required skills,
  experience range, and application deadlines.
- **Application pipeline** — a defined status state machine (Applied → ATS
  Analysis → Shortlisted → HR Screening → Technical/Coding/Managerial
  Rounds → Final HR → Selected/Rejected).
- **Interview scheduling** — with automatic double-booking conflict checks
  for interviewers.
- **Interviewer feedback** — structured scoring (technical knowledge,
  communication, problem solving, coding, confidence) with a recommendation.
- **Candidate ranking** — candidates ranked by ATS score per job opening.
- **Notifications** — application, interview, and feedback updates.
- **Analytics dashboards** — department-wise candidate distribution and
  pipeline funnel charts.

## Tech Stack

**Backend:** Django, Django REST Framework, Simple JWT authentication, MySQL
**Frontend:** HTML, CSS, vanilla JavaScript, Chart.js, FullCalendar

## Project Structure

```
interview_management/
├── backend/            # Django project — REST API, models, ATS logic
├── frontend/           # Static HTML/CSS/JS client (role-based dashboards)
└── seed_data/          # Script + sample resumes to populate demo data
```

## Getting Started

### Backend

```
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/`.

### Frontend

The frontend is static — no build step. Serve the `frontend/` folder with
any static file server, for example:

```
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500/` in the browser. Make sure `API_BASE` in
`frontend/js/api.js` points at your running backend.

### Demo data (optional)

To populate the system with sample candidates, jobs, and applications
already moved through the pipeline, see `seed_data/README.md`.

## User Roles

| Role        | Can do |
|-------------|--------|
| Admin       | Manage departments, jobs, candidates, view analytics |
| HR          | Manage jobs, review applications, schedule interviews, move candidates through the pipeline |
| Interviewer | View assigned interviews, submit feedback |
| Candidate   | Build profile, upload resume, browse jobs, apply, track application status |

## Screenshots

_Add screenshots of the dashboards here once available._

## Author

Built by **Chris (Paras Manoj Choudhary)** — Engineering student, DY Patil
University Talsande.