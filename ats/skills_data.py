"""
Master skills list for rule-based extraction.

To add a new recognizable skill later: add its canonical name to
KNOWN_SKILLS, and (optionally) any aliases people commonly write instead,
to SKILL_SYNONYMS. Nothing else in the codebase needs to change - the
extraction engine (skill_extraction.py) reads from this file only.
"""

KNOWN_SKILLS = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Go", "Ruby", "Swift", "Kotlin",
    # Web / Backend frameworks
    "Django", "Django REST Framework", "Flask", "FastAPI", "Spring Boot", "Node.js", "Express.js",
    "React", "Angular", "Vue.js", "Next.js",
    # Frontend
    "HTML", "CSS", "Bootstrap", "Tailwind CSS", "jQuery",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Redis", "SQL",
    # Data / AI-ML
    "Pandas", "NumPy", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "scikit-learn", "Power BI", "Tableau", "Data Analysis", "NLTK", "spaCy",
    # DevOps / Tools
    "Git", "GitHub", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure", "GCP", "Linux", "CI/CD",
    # APIs / Concepts
    "REST API", "GraphQL", "Microservices", "Hibernate", "JWT",
    # Testing / QA
    "Selenium", "JUnit", "PyTest", "Manual Testing", "Automation Testing",
    # Other
    "Agile", "Scrum", "Excel",
]

# Common alternate ways people write a skill -> canonical name in KNOWN_SKILLS
SKILL_SYNONYMS = {
    "js": "JavaScript",
    "reactjs": "React",
    "react.js": "React",
    "nodejs": "Node.js",
    "node": "Node.js",
    "vuejs": "Vue.js",
    "expressjs": "Express.js",
    "postgres": "PostgreSQL",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "drf": "Django REST Framework",
    "tf": "TensorFlow",
    "sklearn": "scikit-learn",
    "k8s": "Kubernetes",
    "restful api": "REST API",
    "rest apis": "REST API",
    "c plus plus": "C++",
}
