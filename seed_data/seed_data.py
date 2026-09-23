"""
seed_data.py
Populates a fresh RecruitOS backend with realistic demo data via the REST API:
  - 6 departments + 6 matching open jobs
  - 6 candidates, each with a real resume PDF, profile, extracted skills,
    a department recommendation, and an application
  - Applications pushed through the pipeline to a mix of end states:
      Ananya  -> SELECTED   (2 interviews, strong feedback)
      Sneha   -> SELECTED   (2 interviews, strong feedback)
      Rohan   -> REJECTED   (rejected right after ATS analysis, no interview)
      Priya   -> REJECTED   (rejected after a weak technical interview)
      Karan   -> IN PROGRESS (shortlisted, sitting in HR screening)
      Aditya  -> IN PROGRESS (technical interview done, awaiting decision)

REQUIREMENTS BEFORE RUNNING
  1. `pip install requests`
  2. Your Django backend running and reachable at BASE_URL below.
  3. An existing ADMIN (or HR) user — register/superuser creation is out of
     scope of the public API, so create one via `python manage.py createsuperuser`
     or your own seed, and fill in ADMIN_USERNAME / ADMIN_PASSWORD below.
  4. An existing INTERVIEWER user (the public /api/auth/register/ endpoint
     only ever creates candidates) — create one via Django admin, then fill
     in INTERVIEWER_USERNAME / INTERVIEWER_PASSWORD / INTERVIEWER_USER_ID
     below. (INTERVIEWER_USER_ID is that user's numeric id, visible in
     Django admin's user list.)
  5. Resume PDFs already generated: run `python3 generate_resumes.py` first
     (creates ./resumes/*.pdf — already included in this zip).

Run:  python3 seed_data.py
Safe to re-run: candidates/jobs/departments that already exist are reused
instead of duplicated, though a re-run will try to push applications through
the pipeline again and may error harmlessly on transitions already made.
"""
import os
import sys
import time
from datetime import date, timedelta

import requests

# ─────────────────────────── CONFIG — fill these in ───────────────────────────
BASE_URL = "http://127.0.0.1:8000"

ADMIN_USERNAME = "admin_test"
ADMIN_PASSWORD = "12345678"

INTERVIEWER_USERNAME = "interviewer_test"
INTERVIEWER_PASSWORD = "12345678"
INTERVIEWER_USER_ID = 3  # <-- set this to the interviewer's numeric user id

RESUME_DIR = os.path.join(os.path.dirname(__file__), "resumes")
# ────────────────────────────────────────────────────────────────────────────


def log(msg):
    print(f"  {msg}")


def step(msg):
    print(f"\n=== {msg} ===")


def login(username, password):
    r = requests.post(f"{BASE_URL}/api/auth/login/", json={"username": username, "password": password})
    if not r.ok:
        raise RuntimeError(f"Login failed for {username}: {r.status_code} {r.text}")
    return r.json()["access"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def api(method, path, token=None, json=None, files=None, ok_statuses=(200, 201, 204)):
    """Thin wrapper: returns parsed JSON (or None) on success, raises with body text on failure."""
    headers = auth_headers(token) if token else {}
    url = f"{BASE_URL}{path}"
    r = requests.request(method, url, headers=headers, json=json, files=files)
    if r.status_code not in ok_statuses:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
    if r.status_code == 204 or not r.content:
        return None
    return r.json()


def as_list(data):
    return data if isinstance(data, list) else data.get("results", [])


# ─────────────────────────── Departments & Jobs ───────────────────────────
DEPARTMENTS = [
    {"name": "Python Development", "description": "Backend services in Python/Django."},
    {"name": "Java Development", "description": "Backend services in Java/Spring."},
    {"name": "Frontend Development", "description": "Client-side web applications."},
    {"name": "Data Science", "description": "Analytics, ML and data products."},
    {"name": "DevOps", "description": "Infrastructure, CI/CD and reliability."},
    {"name": "Full Stack Development", "description": "End-to-end MERN/MEAN product teams."},
]

JOBS = [
    {"key": "python-backend", "title": "Backend Developer (Python/Django)", "dept": "Python Development",
     "job_type": "full_time", "exp": (1, 3), "openings": 2,
     "description": "Own REST APIs end to end using Django and DRF, from schema design to production deployment.",
     "keywords": "django, rest framework, mysql, postgresql, docker",
     "skills": [("Python", 3), ("Django", 3), ("REST API", 2), ("MySQL", 2), ("Docker", 1)]},
    {"key": "java-backend", "title": "Backend Developer (Java/Spring Boot)", "dept": "Java Development",
     "job_type": "full_time", "exp": (2, 4), "openings": 1,
     "description": "Build and scale backend services with Spring Boot, Hibernate and MySQL.",
     "keywords": "spring boot, hibernate, mysql, java",
     "skills": [("Java", 3), ("Spring Boot", 3), ("Hibernate", 2), ("MySQL", 2)]},
    {"key": "react-frontend", "title": "Frontend Developer (React)", "dept": "Frontend Development",
     "job_type": "full_time", "exp": (1, 3), "openings": 2,
     "description": "Ship responsive, accessible interfaces in React working closely with product and design.",
     "keywords": "react, redux, javascript, css",
     "skills": [("React", 3), ("JavaScript", 3), ("Redux", 2), ("CSS3", 1)]},
    {"key": "data-scientist", "title": "Data Scientist", "dept": "Data Science",
     "job_type": "full_time", "exp": (0, 2), "openings": 1,
     "description": "Build predictive models and dashboards that drive product and business decisions.",
     "keywords": "machine learning, pandas, scikit-learn, python",
     "skills": [("Python", 2), ("Machine Learning", 3), ("Pandas", 2), ("Scikit-learn", 2)]},
    {"key": "devops-engineer", "title": "DevOps Engineer", "dept": "DevOps",
     "job_type": "full_time", "exp": (2, 5), "openings": 1,
     "description": "Own CI/CD pipelines and container infrastructure on AWS at scale.",
     "keywords": "aws, docker, kubernetes, jenkins, terraform",
     "skills": [("AWS", 3), ("Docker", 2), ("Kubernetes", 3), ("Jenkins", 2)]},
    {"key": "mern-fullstack", "title": "Full Stack Developer (MERN)", "dept": "Full Stack Development",
     "job_type": "full_time", "exp": (1, 3), "openings": 2,
     "description": "Build features end to end across a Node.js/Express API and a React frontend.",
     "keywords": "node.js, express, react, mongodb",
     "skills": [("Node.js", 3), ("React", 2), ("MongoDB", 2), ("Express.js", 2)]},
]

# ─────────────────────────── Candidates ───────────────────────────
CANDIDATES = [
    {
        "username": "ananya.sharma", "email": "ananya.sharma.dev@example.com", "password": "Candidate@123",
        "resume": "ananya_sharma_resume.pdf", "job_key": "python-backend",
        "phone": "+91 9876543210", "dob": "2001-04-12", "address": "Pune, Maharashtra",
        "summary": "Backend developer with 1.5 years building REST APIs in Python and Django.",
        "linkedin": "https://linkedin.com/in/ananyasharma", "portfolio": "",
        "plan": "selected_two_interviews",
    },
    {
        "username": "rohan.verma", "email": "rohan.verma.java@example.com", "password": "Candidate@123",
        "resume": "rohan_verma_resume.pdf", "job_key": "java-backend",
        "phone": "+91 9123456780", "dob": "2002-01-20", "address": "Bengaluru, Karnataka",
        "summary": "Java backend developer, internship experience with Spring Boot and Hibernate.",
        "linkedin": "https://linkedin.com/in/rohanverma", "portfolio": "",
        "plan": "rejected_early",
    },
    {
        "username": "priya.nair", "email": "priya.nair.frontend@example.com", "password": "Candidate@123",
        "resume": "priya_nair_resume.pdf", "job_key": "react-frontend",
        "phone": "+91 9000011223", "dob": "2001-09-05", "address": "Chennai, Tamil Nadu",
        "summary": "Frontend developer with a year of React experience.",
        "linkedin": "https://linkedin.com/in/priyanair", "portfolio": "",
        "plan": "rejected_after_interview",
    },
    {
        "username": "karan.mehta", "email": "karan.mehta.ds@example.com", "password": "Candidate@123",
        "resume": "karan_mehta_resume.pdf", "job_key": "data-scientist",
        "phone": "+91 9988776655", "dob": "2003-03-15", "address": "Ahmedabad, Gujarat",
        "summary": "Recent Data Science graduate, internship experience in classification models.",
        "linkedin": "https://linkedin.com/in/karanmehta", "portfolio": "",
        "plan": "in_progress_pre_interview",
    },
    {
        "username": "sneha.iyer", "email": "sneha.iyer.devops@example.com", "password": "Candidate@123",
        "resume": "sneha_iyer_resume.pdf", "job_key": "devops-engineer",
        "phone": "+91 9822033445", "dob": "1999-11-30", "address": "Hyderabad, Telangana",
        "summary": "DevOps engineer with 3 years automating CI/CD and AWS infrastructure.",
        "linkedin": "https://linkedin.com/in/snehaiyer", "portfolio": "",
        "plan": "selected_two_interviews",
    },
    {
        "username": "aditya.rao", "email": "aditya.rao.mern@example.com", "password": "Candidate@123",
        "resume": "aditya_rao_resume.pdf", "job_key": "mern-fullstack",
        "phone": "+91 9765432109", "dob": "2001-07-22", "address": "Mumbai, Maharashtra",
        "summary": "Full-stack developer, 2 years building end-to-end apps with the MERN stack.",
        "linkedin": "https://linkedin.com/in/adityarao", "portfolio": "",
        "plan": "in_progress_post_interview",
    },
]


def ensure_departments(admin_token):
    step("Departments")
    existing = {d["name"]: d["id"] for d in as_list(api("GET", "/api/departments/", admin_token))}
    for d in DEPARTMENTS:
        if d["name"] in existing:
            log(f"exists: {d['name']}")
            continue
        created = api("POST", "/api/departments/", admin_token,
                       json={"name": d["name"], "description": d["description"], "is_active": True})
        existing[d["name"]] = created["id"]
        log(f"created: {d['name']}")
    return existing


def ensure_jobs(admin_token, dept_ids):
    step("Jobs")
    existing_jobs = {j["title"]: j for j in as_list(api("GET", "/api/jobs/", admin_token))}
    job_map = {}
    deadline = (date.today() + timedelta(days=45)).isoformat()
    for j in JOBS:
        if j["title"] in existing_jobs:
            log(f"exists: {j['title']}")
            job_map[j["key"]] = existing_jobs[j["title"]]
            continue
        body = {
            "title": j["title"], "department": dept_ids[j["dept"]], "job_type": j["job_type"],
            "description": j["description"], "experience_min": j["exp"][0], "experience_max": j["exp"][1],
            "education_required": "B.Tech/BCA/B.Sc or equivalent", "num_openings": j["openings"],
            "location": "Remote / Hybrid", "application_deadline": deadline, "keywords": j["keywords"],
            "status": "open",
            "required_skills": [{"skill_name": s, "weight": w} for s, w in j["skills"]],
        }
        created = api("POST", "/api/jobs/", admin_token, json=body)
        job_map[j["key"]] = created
        log(f"created: {j['title']}")
    return job_map


def get_rounds(admin_token):
    rounds = as_list(api("GET", "/api/interviews/rounds/", admin_token))
    by_key = {}
    for r in rounds:
        name = r["name"].lower()
        if "technical" in name:
            by_key["technical"] = r
        elif "managerial" in name or "manager" in name:
            by_key["managerial"] = r
    if "technical" not in by_key and rounds:
        by_key["technical"] = rounds[0]
    if "managerial" not in by_key and rounds:
        by_key["managerial"] = rounds[-1]
    return by_key


def register_or_login(c):
    reg = requests.post(f"{BASE_URL}/api/auth/register/", json={
        "username": c["username"], "email": c["email"], "password": c["password"],
    })
    if reg.status_code in (200, 201):
        log("registered")
    else:
        log(f"register skipped ({reg.status_code}) — assuming already exists")
    return login(c["username"], c["password"])


def upload_resume(token, filename):
    path = os.path.join(RESUME_DIR, filename)
    with open(path, "rb") as f:
        r = requests.post(f"{BASE_URL}/api/resumes/upload/", headers=auth_headers(token),
                           files={"file": (filename, f, "application/pdf")})
    if not r.ok:
        raise RuntimeError(f"resume upload failed: {r.status_code} {r.text[:300]}")
    return r.json()


STATUS_CHAIN = ["applied", "ats_analysis", "shortlisted", "hr_screening",
                "technical_round", "coding_round", "managerial_round", "final_hr", "selected"]


def advance_status(admin_token, application_id, target):
    """Walk the application forward through STATUS_CHAIN up to (and including) target."""
    idx = STATUS_CHAIN.index(target)
    for s in STATUS_CHAIN[1:idx + 1]:
        try:
            api("PATCH", f"/api/applications/{application_id}/status/", admin_token, json={"status": s})
            log(f"  status -> {s}")
        except RuntimeError as e:
            log(f"  ! couldn't move to {s}: {e}")
            return


def reject(admin_token, application_id):
    try:
        api("PATCH", f"/api/applications/{application_id}/status/", admin_token, json={"status": "rejected"})
        log("  status -> rejected")
    except RuntimeError as e:
        log(f"  ! couldn't reject: {e}")


def schedule_interview(admin_token, application_id, round_id, day_offset, time_str):
    body = {
        "application": application_id, "round": round_id, "interviewer": INTERVIEWER_USER_ID,
        "scheduled_date": (date.today() + timedelta(days=day_offset)).isoformat(),
        "scheduled_time": time_str, "duration_minutes": 45,
        "location_or_link": "https://meet.google.com/demo-interview", "status": "confirmed",
    }
    return api("POST", "/api/interviews/", admin_token, json=body)


def submit_feedback(interviewer_token, interview_id, scores, recommendation):
    body = {"interview": interview_id, "recommendation": recommendation, **scores}
    return api("POST", "/api/interviews/feedback/", interviewer_token, json=body)


def run_candidate(admin_token, interviewer_token, job_map, rounds, c, day_offset):
    step(f"Candidate: {c['username']} ({c['plan']})")

    token = register_or_login(c)

    api("PATCH", "/api/candidates/me/", token, json={
        "phone": c["phone"], "date_of_birth": c["dob"], "address": c["address"],
        "summary": c["summary"], "linkedin_url": c["linkedin"], "portfolio_url": c["portfolio"],
    })
    log("profile filled")

    resume = upload_resume(token, c["resume"])
    resume_id = resume["id"]
    log(f"resume uploaded (id={resume_id}, status={resume.get('parsing_status')})")

    try:
        skills_res = api("POST", f"/api/ats/resumes/{resume_id}/extract-skills/", token)
        log(f"skills extracted: {skills_res.get('count', '?')}")
    except RuntimeError as e:
        log(f"! skill extraction failed: {e}")

    me = api("GET", "/api/candidates/me/", token)
    candidate_id = me["id"]

    try:
        rec = api("POST", f"/api/ats/candidates/{candidate_id}/recommend-department/", token)
        log(f"recommended department: {rec.get('recommended_department')} ({rec.get('confidence')}%)")
    except RuntimeError as e:
        log(f"! department recommendation failed: {e}")

    job = job_map[c["job_key"]]
    try:
        application = api("POST", "/api/applications/", token, json={"job": job["id"], "resume": resume_id})
        log(f"applied to {job['title']} (application id={application['id']})")
    except RuntimeError as e:
        log(f"! application failed, trying to find existing one: {e}")
        mine = as_list(api("GET", "/api/applications/", token))
        application = next((a for a in mine if a["job"] == job["id"]), None)
        if not application:
            log("! no application found — skipping rest of this candidate")
            return
    application_id = application["id"]

    try:
        score = api("POST", "/api/ats/score/", admin_token, json={"resume_id": resume_id, "job_id": job["id"]})
        log(f"ATS score: {score.get('overall_score')}")
    except RuntimeError as e:
        log(f"! ATS scoring failed: {e}")

    plan = c["plan"]

    if plan == "rejected_early":
        advance_status(admin_token, application_id, "ats_analysis")
        reject(admin_token, application_id)
        return

    if plan == "in_progress_pre_interview":
        advance_status(admin_token, application_id, "hr_screening")
        return

    # Everything past this point needs to reach technical_round and hold an interview.
    advance_status(admin_token, application_id, "technical_round")

    tech_round = rounds.get("technical")
    if not tech_round or not interviewer_token:
        log("! no technical round / interviewer available — stopping before interview")
        return

    iv1 = schedule_interview(admin_token, application_id, tech_round["id"], day_offset, "10:00:00")
    log(f"technical interview scheduled (id={iv1['id']})")

    if plan == "rejected_after_interview":
        submit_feedback(interviewer_token, iv1["id"], {
            "technical_knowledge": 3, "communication": 5, "problem_solving": 3, "coding": 2, "confidence": 4,
        }, "reject")
        log("weak feedback submitted")
        reject(admin_token, application_id)
        return

    if plan == "in_progress_post_interview":
        submit_feedback(interviewer_token, iv1["id"], {
            "technical_knowledge": 6, "communication": 7, "problem_solving": 6, "coding": 6, "confidence": 6,
        }, "next_round")
        log("mixed feedback submitted, moving to coding_round")
        advance_status(admin_token, application_id, "coding_round")
        return

    if plan == "selected_two_interviews":
        submit_feedback(interviewer_token, iv1["id"], {
            "technical_knowledge": 9, "communication": 8, "problem_solving": 9, "coding": 8, "confidence": 8,
        }, "select")
        log("strong technical feedback submitted")
        advance_status(admin_token, application_id, "managerial_round")

        mgr_round = rounds.get("managerial")
        if mgr_round:
            iv2 = schedule_interview(admin_token, application_id, mgr_round["id"], day_offset + 3, "14:00:00")
            log(f"managerial interview scheduled (id={iv2['id']})")
            submit_feedback(interviewer_token, iv2["id"], {
                "technical_knowledge": 8, "communication": 9, "problem_solving": 8, "coding": 7, "confidence": 9,
            }, "select")
            log("strong managerial feedback submitted")

        advance_status(admin_token, application_id, "selected")
        log("candidate SELECTED")
        return


def main():
    step("Logging in as admin")
    admin_token = login(ADMIN_USERNAME, ADMIN_PASSWORD)
    log("ok")

    interviewer_token = None
    if INTERVIEWER_USER_ID:
        try:
            step("Logging in as interviewer")
            interviewer_token = login(INTERVIEWER_USERNAME, INTERVIEWER_PASSWORD)
            log("ok")
        except RuntimeError as e:
            print(f"  ! interviewer login failed, interviews will be skipped: {e}")
    else:
        print("  ! INTERVIEWER_USER_ID not set — interviews will be skipped for all candidates.")

    dept_ids = ensure_departments(admin_token)
    job_map = ensure_jobs(admin_token, dept_ids)
    rounds = get_rounds(admin_token) if interviewer_token else {}

    for i, c in enumerate(CANDIDATES):
        try:
            run_candidate(admin_token, interviewer_token, job_map, rounds, c, day_offset=2 + i * 2)
        except Exception as e:
            print(f"  !! candidate {c['username']} failed hard: {e}")
        time.sleep(0.2)

    step("Done")
    print("6 candidates seeded. Log in as HR/Admin in the frontend to see the pipeline filled in.")


if __name__ == "__main__":
    if not os.path.isdir(RESUME_DIR) or not os.listdir(RESUME_DIR):
        print("No resumes found — run `python3 generate_resumes.py` first.")
        sys.exit(1)
    main()
