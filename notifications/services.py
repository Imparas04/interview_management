"""
Notification creation helpers. Other apps (applications, interviews) import
notify()/notify_role() rather than creating Notification objects directly -
keeps the "who gets notified when" logic discoverable in one place.
"""
from .models import Notification


def notify(recipient, message, notif_type=Notification.Type.GENERAL):
    return Notification.objects.create(recipient=recipient, message=message, notif_type=notif_type)


def notify_role(role, message, notif_type=Notification.Type.GENERAL):
    """Notify every user currently holding a given role (e.g. all HR)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(role=role)
    Notification.objects.bulk_create([
        Notification(recipient=u, message=message, notif_type=notif_type) for u in users
    ])
