"""
Department recommendation engine (Phase 9).

Rule-based overlap scoring against the maintainable map in
department_data.py - deliberately not a fake/random confidence number.
confidence = (matched skills / that department's total signature skills) * 100
"""
from .department_data import DEPARTMENT_SKILL_MAP


def recommend_department(candidate_skill_names):
    """
    Returns (best_department_name, confidence_pct, explanation_dict) or
    (None, 0.0, explanation_dict) if the candidate has no recognizable
    skills at all.
    """
    candidate_set = {s.lower() for s in candidate_skill_names}
    scores = {}

    for dept_name, dept_skills in DEPARTMENT_SKILL_MAP.items():
        dept_set = {s.lower() for s in dept_skills}
        matched = candidate_set & dept_set
        confidence = round((len(matched) / len(dept_set)) * 100, 2) if dept_set else 0.0
        scores[dept_name] = {
            "confidence": confidence,
            "matched_skills": sorted(matched),
            "total_department_skills": len(dept_set),
        }

    if not any(v["confidence"] > 0 for v in scores.values()):
        return None, 0.0, {"note": "No matching skills found for any known department.", "scores": scores}

    best_dept = max(scores, key=lambda d: scores[d]["confidence"])
    return best_dept, scores[best_dept]["confidence"], {
        "chosen_department": best_dept,
        "matched_skills": scores[best_dept]["matched_skills"],
        "all_department_scores": {k: v["confidence"] for k, v in scores.items()},
    }
