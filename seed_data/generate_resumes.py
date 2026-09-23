"""
generate_resumes.py
Builds 6 realistic, ATS-parseable resume PDFs into ./resumes/
Run once: python3 generate_resumes.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib import colors

OUT_DIR = os.path.join(os.path.dirname(__file__), "resumes")
os.makedirs(OUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()
name_style = ParagraphStyle("Name", parent=styles["Title"], fontSize=20, spaceAfter=2, alignment=TA_LEFT)
contact_style = ParagraphStyle("Contact", parent=styles["Normal"], fontSize=9.5, textColor=colors.HexColor("#4A5162"), spaceAfter=12)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#2E4374"))
body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14)
bullet = ParagraphStyle("Bullet", parent=styles["Normal"], fontSize=10, leading=14, leftIndent=10)

CANDIDATES = [
    {
        "file": "ananya_sharma_resume.pdf",
        "name": "Ananya Sharma",
        "contact": "ananya.sharma.dev@example.com | +91 98765 43210 | Pune, India | linkedin.com/in/ananyasharma",
        "summary": "Backend developer with 1.5 years of experience building REST APIs and scalable services in Python and Django. Comfortable across the stack from database design to deployment.",
        "skills": ["Python", "Django", "Django REST Framework", "MySQL", "PostgreSQL", "REST API",
                    "Git", "Docker", "Redis", "Celery", "AWS EC2", "Linux"],
        "education": ["B.Tech in Computer Science, Savitribai Phule Pune University — 2023, CGPA 8.4/10"],
        "experience": [
            ("Junior Backend Developer, CodeCraft Pvt Ltd — Jul 2023 to Present", [
                "Designed and maintained microservices in Django serving over 15,000 daily API requests.",
                "Implemented JWT-based authentication and role-based access control across services.",
                "Deployed and monitored applications on AWS EC2 using Docker containers.",
            ]),
            ("Backend Developer Intern, TechNova Solutions — Jan 2023 to Jun 2023", [
                "Built REST APIs using Django REST Framework for an internal inventory system.",
                "Optimized MySQL queries and added indexing, cutting average response time by 40%.",
                "Integrated Celery with Redis for asynchronous email and report-generation tasks.",
            ]),
        ],
        "projects": [
            ("E-commerce API Platform", "Django, DRF, PostgreSQL, Stripe API — Designed a multi-vendor REST backend with cart, checkout and payment webhooks."),
            ("Task Management System", "Django, Celery, Redis — Built a Kanban-style task tracker with background reminder emails."),
        ],
        "certifications": ["AWS Certified Cloud Practitioner (2023)"],
    },
    {
        "file": "rohan_verma_resume.pdf",
        "name": "Rohan Verma",
        "contact": "rohan.verma.java@example.com | +91 91234 56780 | Bengaluru, India | linkedin.com/in/rohanverma",
        "summary": "Java backend developer with hands-on internship experience building REST services with Spring Boot and Hibernate. Strong fundamentals in OOP and relational databases.",
        "skills": ["Java", "Spring Boot", "Spring MVC", "Hibernate", "MySQL", "REST API",
                    "Maven", "Git", "JUnit", "Data Structures", "Algorithms"],
        "education": ["B.E. in Information Technology, Visvesvaraya Technological University — 2024, CGPA 7.8/10"],
        "experience": [
            ("Java Developer Intern, InfoEdge Systems — Jan 2024 to Jun 2024", [
                "Developed REST APIs with Spring Boot for a customer-onboarding module.",
                "Used Hibernate ORM to map relational entities and handle transactions.",
                "Wrote unit and integration tests with JUnit, raising code coverage to 75%.",
            ]),
        ],
        "projects": [
            ("Library Management System", "Java, Spring Boot, MySQL — Full CRUD system for tracking books, members and fines."),
            ("Student Portal", "Java, Spring MVC, JSP — Academic records portal with role-based login for students and faculty."),
        ],
        "certifications": ["Oracle Certified Associate, Java SE 8 Programmer"],
    },
    {
        "file": "priya_nair_resume.pdf",
        "name": "Priya Nair",
        "contact": "priya.nair.frontend@example.com | +91 90000 11223 | Chennai, India | linkedin.com/in/priyanair",
        "summary": "Frontend developer with a year of experience crafting responsive, accessible interfaces in React. Enjoys working closely with designers to ship polished products.",
        "skills": ["JavaScript", "React", "Redux", "HTML5", "CSS3", "TypeScript",
                    "REST API", "Git", "Figma", "Tailwind CSS", "Webpack"],
        "education": ["Bachelor of Computer Applications, University of Madras — 2023, 82%"],
        "experience": [
            ("Frontend Developer, PixelWorks Studio — Aug 2023 to Present", [
                "Built responsive product UIs using React and Redux consumed by 20,000+ monthly users.",
                "Translated Figma designs into pixel-accurate, accessible components.",
                "Reduced initial page load by 30% through code-splitting and lazy loading.",
            ]),
        ],
        "projects": [
            ("Portfolio Website Builder", "React, Tailwind CSS — Drag-and-drop personal portfolio generator with live preview."),
            ("Recipe Sharing App", "React, Redux, REST API — Community recipe platform with search and favorites."),
        ],
        "certifications": ["Meta Front-End Developer Professional Certificate"],
    },
    {
        "file": "karan_mehta_resume.pdf",
        "name": "Karan Mehta",
        "contact": "karan.mehta.ds@example.com | +91 99887 76655 | Ahmedabad, India | linkedin.com/in/karanmehta",
        "summary": "Recent Data Science graduate with internship experience building classification models and dashboards in Python. Eager to apply statistical and ML fundamentals to real business problems.",
        "skills": ["Python", "Pandas", "NumPy", "Scikit-learn", "Machine Learning",
                    "Data Visualization", "Matplotlib", "Seaborn", "SQL", "Jupyter"],
        "education": ["B.Sc. in Data Science, Gujarat University — 2024, CGPA 8.1/10"],
        "experience": [
            ("Data Science Intern, Insightify Analytics — Feb 2024 to Apr 2024", [
                "Built a customer-churn classification model achieving 88% accuracy with scikit-learn.",
                "Performed exploratory data analysis on transactional data for a retail client.",
                "Created interactive dashboards using Matplotlib and Seaborn for stakeholder reviews.",
            ]),
        ],
        "projects": [
            ("House Price Prediction Model", "Python, Scikit-learn, Pandas — Regression model with feature engineering, RMSE improved 18%."),
            ("Customer Segmentation", "Python, K-Means Clustering — Segmented 5,000+ customers into actionable marketing groups."),
        ],
        "certifications": ["IBM Data Science Professional Certificate"],
    },
    {
        "file": "sneha_iyer_resume.pdf",
        "name": "Sneha Iyer",
        "contact": "sneha.iyer.devops@example.com | +91 98220 33445 | Hyderabad, India | linkedin.com/in/snehaiyer",
        "summary": "DevOps engineer with 3 years of experience automating CI/CD pipelines and managing containerized infrastructure on AWS. Passionate about reliability and reducing deployment friction.",
        "skills": ["AWS", "Docker", "Kubernetes", "Jenkins", "CI/CD", "Linux",
                    "Terraform", "Git", "Bash Scripting", "Ansible", "Monitoring"],
        "education": ["B.Tech in Computer Science, Osmania University — 2021, CGPA 8.6/10"],
        "experience": [
            ("DevOps Engineer, CloudSprint Technologies — Jul 2021 to Present", [
                "Managed CI/CD pipelines in Jenkins for 12+ microservices, cutting deployment time by 60%.",
                "Containerized legacy applications with Docker and orchestrated them on Kubernetes.",
                "Automated infrastructure provisioning on AWS using Terraform and Ansible playbooks.",
            ]),
        ],
        "projects": [
            ("Automated CI/CD Pipeline", "Jenkins, Docker, Kubernetes — End-to-end pipeline from commit to production with automated rollback."),
            ("Infrastructure as Code Setup", "Terraform, Ansible, AWS — Reproducible multi-environment infrastructure defined entirely in code."),
        ],
        "certifications": ["AWS Certified DevOps Engineer — Professional", "Certified Kubernetes Administrator (CKA)"],
    },
    {
        "file": "aditya_rao_resume.pdf",
        "name": "Aditya Rao",
        "contact": "aditya.rao.mern@example.com | +91 97654 32109 | Mumbai, India | linkedin.com/in/adityarao",
        "summary": "Full-stack developer with 2 years of experience building end-to-end web applications with the MERN stack, from database schema to deployed UI.",
        "skills": ["JavaScript", "Node.js", "Express.js", "React", "MongoDB", "REST API",
                    "Git", "HTML5", "CSS3", "JWT", "Socket.io"],
        "education": ["B.Tech in Computer Science, Mumbai University — 2023, CGPA 8.0/10"],
        "experience": [
            ("Full-stack Developer, Webnest Solutions — Jun 2023 to Present", [
                "Built full-stack web applications end to end using the MERN stack.",
                "Designed RESTful APIs with Node.js and Express, documented with Postman.",
                "Implemented JWT-based authentication and deployed apps on Heroku and Vercel.",
            ]),
        ],
        "projects": [
            ("Social Media Dashboard", "MERN stack — Analytics dashboard aggregating engagement metrics across platforms."),
            ("Real-time Chat Application", "Node.js, Socket.io, MongoDB — Group chat with typing indicators and message history."),
        ],
        "certifications": ["The Complete Web Developer Bootcamp Certificate"],
    },
]


def build_resume(c):
    path = os.path.join(OUT_DIR, c["file"])
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    story = [
        Paragraph(c["name"], name_style),
        Paragraph(c["contact"], contact_style),
        Paragraph("Summary", h2),
        Paragraph(c["summary"], body),
        Paragraph("Skills", h2),
        Paragraph(", ".join(c["skills"]), body),
        Paragraph("Experience", h2),
    ]
    for title, bullets in c["experience"]:
        story.append(Paragraph(f"<b>{title}</b>", body))
        story.append(ListFlowable([ListItem(Paragraph(b, bullet)) for b in bullets],
                                   bulletType="bullet", leftIndent=14))
        story.append(Spacer(1, 6))
    story.append(Paragraph("Projects", h2))
    for title, desc in c["projects"]:
        story.append(Paragraph(f"<b>{title}</b> — {desc}", body))
        story.append(Spacer(1, 4))
    story.append(Paragraph("Education", h2))
    for e in c["education"]:
        story.append(Paragraph(e, body))
    story.append(Paragraph("Certifications", h2))
    for cert in c["certifications"]:
        story.append(Paragraph(f"• {cert}", body))
    doc.build(story)
    print(f"Built {path}")


if __name__ == "__main__":
    for c in CANDIDATES:
        build_resume(c)
    print(f"\nDone — {len(CANDIDATES)} resumes in {OUT_DIR}/")
