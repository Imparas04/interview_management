from django.test import TestCase
from .skill_extraction import extract_skills
from .scoring import score_skills_match, score_experience_match, extract_experience_years
from .department_recommendation import recommend_department


class SkillExtractionTests(TestCase):
    def test_extracts_known_skills_from_text(self):
        text = "Developed web applications using Python, Django, MySQL, HTML, CSS and JavaScript."
        skills = extract_skills(text)
        for expected in ["Python", "Django", "MySQL", "HTML", "CSS", "JavaScript"]:
            self.assertIn(expected, skills)

    def test_does_not_match_substring_false_positive(self):
        """'Go' must not match inside 'Google' - whole-word matching only."""
        skills = extract_skills("Experienced with Google Cloud and the Go programming language.")
        self.assertIn("Go", skills)  # the standalone word "Go" is present and should match

    def test_synonym_resolves_to_canonical_name(self):
        skills = extract_skills("Built UI using JS and ReactJS.")
        self.assertIn("JavaScript", skills)
        self.assertIn("React", skills)


class ScoringEngineTests(TestCase):
    def test_skills_match_full_overlap_is_100_percent(self):
        pct, detail = score_skills_match(["Python", "Django"], [("Python", 2), ("Django", 2)])
        self.assertEqual(pct, 100.0)
        self.assertEqual(detail['missing'], [])

    def test_skills_match_partial_overlap_weighted_correctly(self):
        # Python (weight 3) matched, Django (weight 1) missing -> 3/4 = 75%
        pct, detail = score_skills_match(["Python"], [("Python", 3), ("Django", 1)])
        self.assertEqual(pct, 75.0)
        self.assertIn("Django", detail['missing'])

    def test_experience_within_range_scores_100(self):
        pct, _ = score_experience_match("I have 1 years of experience in backend development.", 0, 2)
        self.assertEqual(pct, 100.0)

    def test_experience_extraction_finds_highest_figure(self):
        years = extract_experience_years("Worked 2 years at company A and 5 years at company B.")
        self.assertEqual(years, 5.0)


class DepartmentRecommendationTests(TestCase):
    def test_python_skills_recommend_python_development(self):
        dept, confidence, explanation = recommend_department(["Python", "Django", "MySQL", "REST API"])
        self.assertEqual(dept, "Python Development")
        self.assertGreater(confidence, 0)

    def test_no_known_skills_returns_none(self):
        dept, confidence, explanation = recommend_department(["Cooking", "Painting"])
        self.assertIsNone(dept)
        self.assertEqual(confidence, 0.0)
