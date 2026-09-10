"""
Interviewer scheduling conflict detection.

An interviewer cannot be double-booked - two interviews for the same
interviewer with overlapping time ranges on the same day are rejected.
Cancelled interviews are ignored (a cancelled slot frees up the time).
"""
from datetime import datetime, timedelta


def has_conflict(interviewer, scheduled_date, scheduled_time, duration_minutes, exclude_interview_id=None):
    from .models import Interview

    new_start = datetime.combine(scheduled_date, scheduled_time)
    new_end = new_start + timedelta(minutes=duration_minutes)

    existing = Interview.objects.filter(
        interviewer=interviewer,
        scheduled_date=scheduled_date,
    ).exclude(status=Interview.Status.CANCELLED)

    if exclude_interview_id:
        existing = existing.exclude(id=exclude_interview_id)

    for interview in existing:
        existing_start, existing_end = interview.get_time_range()
        # Standard interval overlap check: two ranges overlap unless one
        # ends before the other starts.
        if new_start < existing_end and existing_start < new_end:
            return True, interview

    return False, None
