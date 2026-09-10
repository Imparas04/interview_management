# Interview Management System — Backend

## Setup (Windows)

1. Extract this zip to your desired folder (e.g. Desktop).
2. Open cmd/terminal inside the extracted `interview_management` folder.
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Open `.env` and set `DB_PASSWORD` to your actual MySQL root password
   (and change `SECRET_KEY` to any random string).
6. Create the MySQL database (in MySQL shell or Workbench):
   ```sql
   CREATE DATABASE interview_management_db CHARACTER SET utf8mb4;
   ```
7. Generate and apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
8. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
9. Seed initial departments:
   ```
   python manage.py seed_departments
   ```
10. Run the server:
    ```
    python manage.py runserver
    ```
11. Visit `http://127.0.0.1:8000/admin/` and log in.

## Notes
- `Django>=5.2,<6.0` is pinned in `requirements.txt` on purpose — Django 6.1
  requires MySQL 8.4+, and most local installs are still on MySQL 8.0.x.
- Never commit `.env` — it's already in `.gitignore`.

---

## Phase 2 — Auth endpoints
```
POST /api/auth/register/   {username, email, password} -> 201 + user
POST /api/auth/login/      {username, password} -> {access, refresh, user}
POST /api/auth/refresh/    {refresh} -> {access}
GET  /api/auth/me/         (Authorization: Bearer <access>) -> user
```

## Phase 3 — Departments endpoints
```
GET    /api/departments/          any logged-in user
POST   /api/departments/          admin only
GET    /api/departments/{id}/     any logged-in user
PUT/PATCH /api/departments/{id}/  admin only
DELETE /api/departments/{id}/     admin only
```

## Phase 4 — Jobs endpoints
```
GET    /api/jobs/                 any logged-in user (candidates see only status=open)
POST   /api/jobs/                 admin/HR only
GET    /api/jobs/{id}/            any logged-in user
PUT/PATCH /api/jobs/{id}/         admin/HR only
DELETE /api/jobs/{id}/            admin/HR only
```
Filters: `?department=<id>`, `?job_type=full_time`, `?status=open`, `?search=python`

Sample create request:
```json
{
  "title": "Python Django Developer",
  "department": 1,
  "description": "Backend role building REST APIs.",
  "experience_min": 0,
  "experience_max": 2,
  "education_required": "B.Tech/BCA",
  "keywords": "backend, api, rest",
  "num_openings": 3,
  "location": "Pune",
  "job_type": "full_time",
  "status": "open",
  "application_deadline": "2026-10-15",
  "required_skills": [
    {"skill_name": "Python", "weight": 3},
    {"skill_name": "Django", "weight": 3},
    {"skill_name": "MySQL", "weight": 2}
  ]
}
```

## Phase 5 — Candidate Profile endpoints
```
GET/PUT/PATCH /api/candidates/me/       candidate only - own profile (auto-created on first GET)
GET           /api/candidates/          HR/Admin/Interviewer only - list all candidate profiles
GET           /api/candidates/{id}/     HR/Admin/Interviewer only - view one profile
```
Filters: `?recommended_department=<id>`, `?search=username_or_email`

`recommended_department` is read-only from the API - filled in automatically by the ATS engine in Phase 9.

## Phase 6 — Resume Upload & Parsing endpoints
```
POST /api/resumes/upload/          candidate only - multipart file upload, key: "file"
GET  /api/resumes/                 candidate: own only; HR/Admin/Interviewer: all
GET  /api/resumes/{id}/            same rule
GET  /api/resumes/{id}/download/   same rule - streams the actual file
```
Supported: PDF, DOCX only. Max size: 5MB. Parsing runs synchronously on upload.

Test with curl (Windows cmd):
```
curl -X POST http://127.0.0.1:8000/api/resumes/upload/ ^
  -H "Authorization: Bearer CANDIDATE_TOKEN" ^
  -F "file=@C:\path\to\resume.pdf"
```

## Phase 7 — Skill Extraction endpoints
```
POST /api/ats/resumes/{resume_id}/extract-skills/     candidate (own resume) or HR/Admin/Interviewer
GET  /api/ats/candidates/{candidate_id}/skills/       candidate (own) or HR/Admin/Interviewer
```
Extraction is rule-based (whole-word match against `ats/skills_data.py`, including synonyms like "js" -> "JavaScript"). To recognize a new skill later, just add it to `KNOWN_SKILLS` (and any aliases to `SKILL_SYNONYMS`) in that file — no other code changes needed.

Re-running extraction on a resume REPLACES the candidate's stored skill list with the fresh result (keeps it aligned to their latest resume).

## Phase 8 — ATS Score endpoints
```
POST /api/ats/score/                body: {"resume_id": 1, "job_id": 2} -> calculates + stores ATSResult
GET  /api/ats/results/{id}/         view one stored result (owner or HR/Admin/Interviewer)
GET  /api/ats/results/?job=<id>     all scores for a job (HR/Admin/Interviewer, candidate sees only their own)
GET  /api/ats/results/?resume=<id>  all scores for a resume
```
Prerequisites before scoring: resume must be parsed successfully (Phase 6) AND skills must already be extracted (Phase 7) - scoring does not silently trigger either step.

Scoring weights: Skills 40%, Experience 20%, Education 10%, Projects 10%, Certifications 10%, Keywords 10%. Every sub-score's `explanation` is stored in the response - e.g. which required skills matched/were missing, how many years of experience were detected vs required, which keywords were found. Nothing is a random or opaque number.

Re-scoring the same resume+job pair updates the existing ATSResult rather than creating duplicates.

## Phase 9 — Department Recommendation
```
POST /api/ats/candidates/{candidate_id}/recommend-department/
```
Candidate (own) or HR/Admin. Uses currently extracted skills (Phase 7) against the maintainable map in `ats/department_data.py`, picks the highest-overlap department, and saves `recommended_department` + `recommended_department_confidence` + explanation onto the CandidateProfile. Visible via `GET /api/candidates/me/` or `/api/candidates/{id}/`.

## Phase 10 — Applications (status state machine)
```
GET  /api/applications/                 candidate: own; HR/Admin: all. Filters: ?job=<id>&status=applied
POST /api/applications/                 candidate only - body: {"job": <id>, "resume": <id>}
GET  /api/applications/{id}/            owner or HR/Admin/Interviewer
PATCH /api/applications/{id}/status/    HR/Admin only - body: {"status": "shortlisted"}
```
Status can ONLY move forward through the fixed workflow (or to `rejected` from any non-terminal state) - defined in `applications/transitions.py`. Skipping steps (e.g. `applied` -> `selected` directly) returns `400` with the allowed next states listed.

Workflow: `applied` -> `ats_analysis` -> `shortlisted` -> `hr_screening` -> `technical_round` -> `coding_round` -> `managerial_round` -> `final_hr` -> `selected`/`rejected`

## Phase 11 — Candidate Ranking
```
GET /api/applications/rank/?job=<job_id>
```
HR/Admin only. Ranks every application for that job by its Phase 8 ATS score, descending, deterministic (unscored candidates sorted last, ties broken by application order - never random).

---

## Phase 15 — Advanced Search
```
GET /api/candidates/search/?name=&email=&skill=&department=&job=&min_ats_score=&application_status=
```
HR/Admin only. All params optional and combinable, e.g.:
`/api/candidates/search/?department=3&min_ats_score=80&skill=Python`

## Phase 16 — Analytics
```
GET /api/analytics/overview/              HR/Admin - total/shortlisted/interviews/selected/rejected/pending + department-wise breakdown
GET /api/analytics/candidate-summary/     candidate only - their own applied/shortlisted/interview counts
```
All numbers computed live from the database - never calculated in the frontend.

## Phase 17 — Testing
```
python manage.py test
```
Covers: registration can't self-assign a role, login/permissions, department/job CRUD permissions, candidates only seeing open jobs, the application status state machine (valid transitions succeed, skipping steps is rejected, terminal states can't move), interviewer double-booking conflict detection, skill extraction (including whole-word matching and synonym resolution), ATS scoring sub-functions, and department recommendation.

## Phase 18 — Deployment
- `Procfile` included for Render/Railway (`web: gunicorn interview_management.wsgi`, runs `migrate` on release).
- `whitenoise` serves static files in production - `python manage.py collectstatic` before deploying.
- Set these environment variables on your hosting platform (same names as `.env`): `SECRET_KEY`, `DEBUG=False`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `ALLOWED_HOSTS` (comma-separated real domain(s), not `*`, once live).
- Use a managed MySQL instance (Railway/PlanetScale/AWS RDS) matching the `mysqlclient` driver already in `requirements.txt`.
- Frontend deploys separately (static hosting - Netlify/Vercel/GitHub Pages) and points its API base URL at wherever this backend is hosted; `CORS_ALLOW_ALL_ORIGINS` should be narrowed to the frontend's real domain before going live.

---

**All 18 phases are now implemented.** Full endpoint list is documented phase-by-phase above.

## Phase 12 — Interview Scheduling
```
GET  /api/interviews/rounds/            any authenticated user - list of round types
GET  /api/interviews/                   role-scoped (candidate: own; interviewer: assigned; HR/Admin: all)
POST /api/interviews/                   HR/Admin only - conflict-checked
GET/PATCH /api/interviews/{id}/         role-scoped read, HR/Admin write
```
Sample create body:
```json
{
  "application": 1,
  "round": 2,
  "interviewer": 5,
  "scheduled_date": "2026-09-20",
  "scheduled_time": "11:00:00",
  "duration_minutes": 45,
  "location_or_link": "https://meet.google.com/xyz",
  "status": "scheduled"
}
```
An interviewer cannot be double-booked - overlapping time ranges for the same interviewer are rejected with `400` (enforced in `interviews/conflicts.py`).

First seed the 5 standard rounds:
```
python manage.py seed_interview_rounds
```

## Phase 13 — Interview Feedback
```
POST /api/interviews/feedback/          interviewer only, own assigned interview
GET  /api/interviews/feedback/list/?interview=<id>     HR/Admin/Interviewer (not candidate)
```
`overall_score` is computed automatically (average of the 5 sub-scores) - never sent in the request. Submitting feedback automatically marks the Interview `completed`. Because each round is a separate Interview row, feedback history across rounds is never overwritten.

## Phase 14 — Notifications
```
GET   /api/notifications/                   own notifications only
PATCH /api/notifications/{id}/read/         mark one read
POST  /api/notifications/mark-all-read/
```
Auto-created when: a candidate applies (all HR notified), an interview is scheduled (candidate + interviewer both notified).
