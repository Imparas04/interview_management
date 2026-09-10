"""
Rule-based skill extraction.

Deliberately NOT using an NLP/AI model here - spec explicitly prioritizes
explainable, rule-based matching over "unnecessarily complicated AI APIs
if a reliable rule-based implementation is possible." This is a whole-word,
case-insensitive match against the maintainable list in skills_data.py.
"""
import re
from .skills_data import KNOWN_SKILLS, SKILL_SYNONYMS


def _build_pattern(term):
    """
    Whole-word match so 'Go' doesn't match inside 'Google', and skills
    containing special characters (C++, Node.js) are escaped properly.
    """
    escaped = re.escape(term)
    return re.compile(rf'(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])', re.IGNORECASE)


def extract_skills(text):
    """
    Returns a sorted list of canonical skill names found in `text`.
    Checks both the canonical KNOWN_SKILLS list and all known synonyms,
    always reporting back the canonical name so downstream matching
    (Phase 8 scoring against JobSkill) has one consistent name to compare.
    """
    if not text:
        return []

    found = set()

    for skill in KNOWN_SKILLS:
        if _build_pattern(skill).search(text):
            found.add(skill)

    for alias, canonical in SKILL_SYNONYMS.items():
        if _build_pattern(alias).search(text):
            found.add(canonical)

    return sorted(found)
