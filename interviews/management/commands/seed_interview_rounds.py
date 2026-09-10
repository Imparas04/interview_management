from django.core.management.base import BaseCommand
from interviews.models import InterviewRound

ROUNDS = [
    (1, "HR Screening"),
    (2, "Technical Interview"),
    (3, "Coding Assessment"),
    (4, "Managerial Interview"),
    (5, "Final HR"),
]


class Command(BaseCommand):
    help = "Seeds the 5 standard interview rounds required by the project spec."

    def handle(self, *args, **options):
        created_count = 0
        for order, name in ROUNDS:
            obj, created = InterviewRound.objects.get_or_create(order=order, defaults={'name': name})
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} new round(s) created."))
