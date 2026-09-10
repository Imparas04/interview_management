"""
Application status state machine.

This is the ONLY place allowed to move an Application from one status to
another. Views must call transition_application_status() - never assign
application.status = X directly - so there's exactly one place that
knows/enforces which transitions are legal.
"""
from django.core.exceptions import ValidationError
from .models import Application

S = Application.Status

ALLOWED_TRANSITIONS = {
    S.APPLIED: [S.ATS_ANALYSIS, S.REJECTED],
    S.ATS_ANALYSIS: [S.SHORTLISTED, S.REJECTED],
    S.SHORTLISTED: [S.HR_SCREENING, S.REJECTED],
    S.HR_SCREENING: [S.TECHNICAL_ROUND, S.REJECTED],
    S.TECHNICAL_ROUND: [S.CODING_ROUND, S.REJECTED],
    S.CODING_ROUND: [S.MANAGERIAL_ROUND, S.REJECTED],
    S.MANAGERIAL_ROUND: [S.FINAL_HR, S.REJECTED],
    S.FINAL_HR: [S.SELECTED, S.REJECTED],
    S.SELECTED: [],   # terminal
    S.REJECTED: [],   # terminal
}


def transition_application_status(application, new_status):
    """
    Raises ValidationError if the transition isn't allowed from the
    application's current status. Saves and returns the application if it
    succeeds.
    """
    current = application.status
    allowed = ALLOWED_TRANSITIONS.get(current, [])

    if new_status not in allowed:
        raise ValidationError(
            f"Cannot move application from '{current}' to '{new_status}'. "
            f"Allowed next states: {allowed or 'none (terminal status)'}."
        )

    application.status = new_status
    application.save(update_fields=['status', 'updated_at'])
    return application
