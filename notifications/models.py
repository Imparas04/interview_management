from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    A single notification for one user. Kept as plain FK to User + a
    notif_type choice instead of a GenericForeignKey to "related object" -
    simpler to query/filter, and the spec's examples never require
    following a link back to the source object, just showing the message.
    """

    class Type(models.TextChoices):
        APPLICATION = 'application', 'Application'
        INTERVIEW = 'interview', 'Interview'
        FEEDBACK = 'feedback', 'Feedback'
        GENERAL = 'general', 'General'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=Type.choices, default=Type.GENERAL)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] {self.recipient.username}: {self.message[:40]}"
