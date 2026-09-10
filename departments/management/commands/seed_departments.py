from django.core.management.base import BaseCommand
from departments.models import Department

INITIAL_DEPARTMENTS = [
    "Python Development",
    "Web Development",
    "Data Analytics",
    "Data Science",
    "AI/ML",
    "Java Development",
    "Testing / QA",
    "DevOps",
    "UI/UX",
    "HR",
]


class Command(BaseCommand):
    help = "Seeds the 10 initial departments required by the project spec."

    def handle(self, *args, **options):
        created_count = 0
        for name in INITIAL_DEPARTMENTS:
            obj, created = Department.objects.get_or_create(name=name)
            if created:
                created_count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} new department(s) created, "
                f"{len(INITIAL_DEPARTMENTS) - created_count} already existed."
            )
        )
