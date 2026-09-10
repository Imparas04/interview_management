"""
ATS scoring engine.

Every function here returns (percentage, explanation_dict) - never just a
bare number - so the caller can store WHY a score came out the way it did,
per the spec's "must explain HOW the score was calculated" requirement.

Weights (must sum to 1.0):
    Skills Match     -> 40%
    Experience Match -> 20%
    Education Match  -> 10%
    Projects         -> 10%
    Certifications   -> 10%
    Keywords         -> 10%
"""
import re

WEIGHTS = {
    'skills': 0.40,
    'experience': 0.20,
    'education': 0.10,
    'projects': 0.10,
    'certifications': 0.10,
    'keywords': 0.10,
}

EXPERIENCE_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|year)', re.IGNORECASE)
EDUCATION_KEYWORDS = [
    'b.tech', 'btech', 'bachelor', 'b.e', 'be ', 'bca', 'bsc', 'b.sc',
    'm.tech', 'mtech', 'master', 'mca', 'msc', 'm.sc', 'mba', 'phd', 'diploma',
]


def score_skills_match(candidate_skill_names, job_skills):
    """
    job_skills: list of (skill_name, weight) tuples from JobSkill.
    Weighted overlap - a skill worth weight=3 that's missing hurts more
    than a weight=1 skill missing, matching the "weight" field's purpose.
    """
    if not job_skills:
        return 100.0, {"note": "Job has no required skills listed.", "matched": [], "missing": []}

    candidate_set = {s.lower() for s in candidate_skill_names}
    total_weight = sum(weight for _, weight in job_skills)
    matched_weight = 0
    matched, missing = [], []

    for skill_name, weight in job_skills:
        if skill_name.lower() in candidate_set:
            matched_weight += weight
            matched.append(skill_name)
        else:
            missing.append(skill_name)

    pct = round((matched_weight / total_weight) * 100, 2) if total_weight else 0.0
    return pct, {"matched": matched, "missing": missing, "matched_weight": matched_weight, "total_weight": total_weight}


def extract_experience_years(text):
    """Returns the highest 'X years' figure mentioned in the resume, or None."""
    matches = EXPERIENCE_PATTERN.findall(text or "")
    if not matches:
        return None
    return max(float(m) for m in matches)


def score_experience_match(resume_text, exp_min, exp_max):
    years = extract_experience_years(resume_text)
    if years is None:
        return 0.0, {"note": "No experience duration found in resume text.", "candidate_years": None, "required": f"{exp_min}-{exp_max}"}

    if exp_min <= years <= exp_max:
        pct = 100.0
    elif years > exp_max:
        # Overqualified isn't penalized as heavily as underqualified
        pct = 85.0
    else:
        gap = exp_min - years
        pct = max(0.0, 100 - (gap * 40))  # each missing year costs 40 points

    return round(pct, 2), {"candidate_years": years, "required_min": exp_min, "required_max": exp_max}


def score_education_match(resume_text, education_required):
    if not education_required or not education_required.strip():
        return 100.0, {"note": "Job has no specific education requirement."}

    text_lower = (resume_text or "").lower()
    required_lower = education_required.lower()

    required_terms = [kw for kw in EDUCATION_KEYWORDS if kw in required_lower]
    if not required_terms:
        required_terms = [required_lower.strip()]

    found = [term for term in required_terms if term in text_lower]
    pct = 100.0 if found else 30.0  # not zero - resume may state education differently than our keyword list

    return pct, {"required": education_required, "matched_terms": found}


def score_projects(resume_text):
    """
    Counts mentions of 'project' as a simple proxy for project experience.
    Rule-based and transparent rather than trying to parse actual project
    descriptions - explainable, matches spec intent.
    """
    count = len(re.findall(r'\bproject', resume_text or "", re.IGNORECASE))
    pct = min(100.0, count * 25.0)
    return round(pct, 2), {"project_mentions": count}


def score_certifications(resume_text):
    count = len(re.findall(r'\bcertifi', resume_text or "", re.IGNORECASE))
    pct = min(100.0, count * 50.0)
    return round(pct, 2), {"certification_mentions": count}


def score_keywords(resume_text, keywords_csv):
    if not keywords_csv or not keywords_csv.strip():
        return 100.0, {"note": "Job has no specific keywords listed."}

    keywords = [k.strip() for k in keywords_csv.split(',') if k.strip()]
    if not keywords:
        return 100.0, {"note": "Job has no specific keywords listed."}

    text_lower = (resume_text or "").lower()
    found = [k for k in keywords if k.lower() in text_lower]
    pct = round((len(found) / len(keywords)) * 100, 2)
    return pct, {"matched_keywords": found, "total_keywords": keywords}


def calculate_ats_score(resume, job, candidate_skill_names):
    """
    Main entry point. Returns a dict ready to be saved onto an ATSResult row.
    """
    job_skills = [(js.skill_name, js.weight) for js in job.required_skills.all()]

    skills_pct, skills_detail = score_skills_match(candidate_skill_names, job_skills)
    exp_pct, exp_detail = score_experience_match(resume.parsed_text, job.experience_min, job.experience_max)
    edu_pct, edu_detail = score_education_match(resume.parsed_text, job.education_required)
    proj_pct, proj_detail = score_projects(resume.parsed_text)
    cert_pct, cert_detail = score_certifications(resume.parsed_text)
    kw_pct, kw_detail = score_keywords(resume.parsed_text, job.keywords)

    overall = (
        skills_pct * WEIGHTS['skills'] +
        exp_pct * WEIGHTS['experience'] +
        edu_pct * WEIGHTS['education'] +
        proj_pct * WEIGHTS['projects'] +
        cert_pct * WEIGHTS['certifications'] +
        kw_pct * WEIGHTS['keywords']
    )

    return {
        'skills_match_pct': skills_pct,
        'experience_match_pct': exp_pct,
        'education_match_pct': edu_pct,
        'projects_pct': proj_pct,
        'certifications_pct': cert_pct,
        'keywords_pct': kw_pct,
        'overall_score': round(overall, 2),
        'explanation': {
            'weights_used': WEIGHTS,
            'skills': skills_detail,
            'experience': exp_detail,
            'education': edu_detail,
            'projects': proj_detail,
            'certifications': cert_detail,
            'keywords': kw_detail,
        },
    }
