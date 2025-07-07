from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from petitions.models import Petition
from .models import Notification
from .utils import trigger_user_notification

User = get_user_model()


def get_users_with_access(petition: Petition):
    if petition.level == Petition.Level.SCHOOL:
        return User.objects.filter(role=User.Role.STUDENT, is_active=True)
    if petition.level == Petition.Level.CLASS and petition.class_group:
        return User.objects.filter(student__in=petition.class_group.students.all(), is_active=True)
    return User.objects.none()


def create_notifications(users, message: str, link: str):
    notifications = [
        Notification(user=user, message=message, link=link)
        for user in users
    ]
    Notification.objects.bulk_create(notifications)
    

@receiver(pre_save, sender=Petition)
def notify_on_petition_status_change(sender, instance: Petition, **kwargs):
    if not instance.pk:
        return

    try:
        previous = Petition.objects.get(pk=instance.pk)
    except Petition.DoesNotExist:
        return

    if previous.status != instance.status and instance.status in {
        Petition.Status.PENDING,
        Petition.Status.APPROVED,
        Petition.Status.REJECTED,
    }:
        users = get_users_with_access(instance).exclude(role=User.Role.DIRECTOR)
        status_display = instance.get_status_display()
        message = f"Петиція «{instance.title}» тепер має статус: {status_display}"
        link = f"/petitions/{instance.pk}/"

        for user in users:
            create_notifications([user], message=message, link=link)
            trigger_user_notification(user.id)