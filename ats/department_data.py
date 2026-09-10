"""
Maintainable department -> signature skills mapping for rule-based
department recommendation (Phase 9). To tune a department's matching
later, just edit its skill list here - no other code changes needed.
"""

DEPARTMENT_SKILL_MAP = {
    "Python Development": ["Python", "Django", "Django REST Framework", "Flask", "FastAPI", "MySQL", "REST API"],
    "Web Development": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js", "Node.js", "Bootstrap"],
    "Data Analytics": ["SQL", "Excel", "Power BI", "Tableau", "Pandas", "Data Analysis", "NumPy"],
    "Data Science": ["Python", "Pandas", "NumPy", "Machine Learning", "scikit-learn", "Power BI", "SQL", "Data Analysis"],
    "AI/ML": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLTK", "spaCy", "scikit-learn"],
    "Java Development": ["Java", "Spring Boot", "Hibernate", "MySQL", "REST API", "Microservices"],
    "Testing / QA": ["Selenium", "JUnit", "PyTest", "Manual Testing", "Automation Testing"],
    "DevOps": ["Docker", "Kubernetes", "Jenkins", "AWS", "Azure", "GCP", "Linux", "CI/CD", "Git"],
    "UI/UX": ["HTML", "CSS", "Bootstrap", "Tailwind CSS", "Figma"],
    "HR": ["Excel", "Communication", "Recruitment"],
}
